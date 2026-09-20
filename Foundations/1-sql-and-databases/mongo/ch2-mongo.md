# Chapter 2 (MongoDB companion): Advanced querying, both ways

*[← Chapter 1 (companion)](ch1-mongo.md) · [SQL twin: Chapter 2](../sql/ch2-sql.md) · [Contents](../../foundations-README.md)*

- [ ] **Mark as read**

[Chapter 2](../sql/ch2-sql.md) covers the SQL you write occasionally but get *asked about* constantly — CTEs, window functions, subqueries, the N+1 trap. Here's the good news for you: three of those four are, in MongoDB, just *more stages in the aggregation pipeline* you already met in the last companion. The pipeline was built for exactly this "multi-step, name-the-intermediate-result" work, so a lot of what feels advanced in SQL feels natural once you think in stages.

Same principle, still: **feel the mechanism.** A window function and `$setWindowFields` compute the same thing; a CTE and a chain of pipeline stages organize the same thing.

---

## CTEs: naming a step vs adding a stage

A **CTE** (SQL's `WITH` clause) names an intermediate result so a complex query reads top to bottom instead of nesting inward. A MongoDB pipeline *is* that idea by construction — each stage is a named step whose output feeds the next. You don't need special syntax to "break it into stages"; stages are all there is.

```sql
-- SQL: CTE names the per-customer revenue, then filters it
WITH customer_revenue AS (
    SELECT customer_id, SUM(total) AS revenue
    FROM orders
    GROUP BY customer_id
)
SELECT customer_id, revenue
FROM customer_revenue
WHERE revenue > 1000;
```

```js
// MongoDB: the pipeline is already a sequence of named steps
db.orders.aggregate([
  { $group: { _id: "$customer_id", revenue: { $sum: "$total" } } }, // the "CTE"
  { $match: { revenue: { $gt: 1000 } } }                            // build on it
]);
```

> 💡 **Concept notes — the pipeline is a CTE chain by default**
> In SQL you *opt in* to readability with `WITH a AS (...), b AS (...)`. In an aggregation pipeline every stage is implicitly the next line of that chain — the output of `$group` flows straight into the next `$match` with no nesting. When a SQL interviewer praises reaching for a CTE to break a gnarly problem into stages, you can note that this is how *every* Mongo aggregation is written: one stage per step, read straight down. The rare case where you need to reuse the *same* intermediate result in two branches is where SQL CTEs still pull ahead; Mongo's `$facet` stage covers that by running several sub-pipelines over the same input.

---

## Window functions: `$setWindowFields`

Here's the big one from Chapter 2. A `GROUP BY` *collapses* rows; a **window function** computes a per-group value *alongside each original row* without collapsing — "show every order, and next to it this customer's running total" or "rank each order within its customer." MongoDB added the exact same capability as a pipeline stage: **`$setWindowFields`**.

```sql
-- SQL
SELECT
  customer_id,
  total,
  SUM(total)   OVER (PARTITION BY customer_id) AS customer_total,
  ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY total DESC) AS rank_in_customer
FROM orders;
```

```js
// MongoDB
db.orders.aggregate([
  { $setWindowFields: {
      partitionBy: "$customer_id",           // PARTITION BY
      sortBy: { total: -1 },                 // ORDER BY within the window
      output: {
        customer_total:  { $sum: "$total" }, // partition-wide aggregate, rows kept
        rank_in_customer:{ $documentNumber: {} } // ROW_NUMBER()
      }
  }}
]);
```

> 💡 **Concept notes — anatomy, translated**
> The `OVER (...)` clause and `$setWindowFields` carry the same three parts:
> - **`PARTITION BY col`** ↔ **`partitionBy: "$col"`** — divides rows into groups *without collapsing them.* Omit it to treat the whole collection as one window.
> - **`ORDER BY col`** ↔ **`sortBy: { col: 1 }`** — orders rows within each partition; required for ranking and running totals.
> - The functions map across: `ROW_NUMBER()` ↔ `$documentNumber`, `RANK()`/`DENSE_RANK()` ↔ `$rank`/`$denseRank`, `SUM/AVG() OVER` ↔ `$sum`/`$avg` in the `output`, `LAG`/`LEAD` ↔ `$shift`. Running totals use a **window boundary** (`documents: ["unbounded", "current"]`) — the explicit version of a SQL running-total frame.
> The killer interview question is the same in both worlds: **"top 3 orders per customer"** or **"2nd-highest salary per department."** Compute a `ROW_NUMBER()`/`$documentNumber` partitioned by the group and ordered descending, then filter to `<= 3`:
> ```js
> db.orders.aggregate([
>   { $setWindowFields: { partitionBy: "$customer_id", sortBy: { total: -1 },
>       output: { rn: { $documentNumber: {} } } } },
>   { $match: { rn: { $lte: 3 } } }   // the WHERE rn <= 3, as a later stage
> ]);
> ```
> Notice you need the *separate* `$match` stage for the same reason SQL needs a CTE: the rank field doesn't exist until the window stage has run, so you filter on it in the *next* stage. Execution order, made visible again.

---

## Subqueries in a filter

SQL lets you filter by the result of another query — `WHERE id IN (SELECT ...)`, `EXISTS`, and correlated subqueries. MongoDB expresses these as either a two-step pipeline or a `$lookup` with its own sub-pipeline.

> 💡 **Concept notes — IN, EXISTS, correlated — the Mongo shapes**
> - **`IN (subquery)`** — "customers who have at least one order." The document-native move is a `$lookup` from customers to orders and then `$match` on the matched array being non-empty; or, if you already have the ids, a plain `{ _id: { $in: [...] } }`.
> - **`NOT IN` / `NOT EXISTS`** — the "never ordered" question from the last companion: `$lookup` then `$match` on the array being empty. The same SQL caution applies in spirit — reasoning about "absence" is where people slip.
> - **Correlated subquery** (a subquery re-run per outer row) ↔ **`$lookup` with a `let` + sub-pipeline**, which runs a pipeline against the joined collection *parameterized by fields of the current document.* It's powerful and, exactly like its SQL cousin, can be slow because it's a per-document loop — a good thing to flag in an interview, and often a sign you should have embedded the data.

---

## The N+1 problem: identical trap, different driver

This one isn't about query syntax at all — it's about how the database meets your application code, and it bites **exactly the same way** whether you're on SQL or MongoDB. The **N+1 problem** is 1 query to fetch a list, then 1 more query *per item* — turning 2 round trips into 1 + N.

> 💡 **Concept notes — N+1 in a document app**
> Fetch 100 blog posts (1 query), then loop and fetch each post's author with a separate `db.users.findOne({ _id: post.author_id })` (100 more) — that's 101 queries where 2 would do. It creeps in through the *same* innocent-looking loop as in the ORM world (`for post in posts: fetch(post.author_id)`); document databases don't immunize you, because referencing across collections still means round trips. **The fixes are the same two moves:** (1) fetch the related data up front in one shot — gather all the author ids and do a single `db.users.find({ _id: { $in: authorIds } })`, or a `$lookup` in the aggregation; or (2) sidestep it entirely by **embedding** the author info in the post if it's small and read-together — the document world's extra escape hatch that SQL doesn't have. Recognizing N+1 from a description ("it's slow and the logs show thousands of tiny identical queries") and naming the fix shows you understand the boundary between your code and the database, whichever database it is.

---

## Try it

Collections: `customers` (`_id`, `name`), `orders` (`_id`, `customer_id`, `total`, `created_at`), `employees` (`_id`, `name`, `department`, `salary`).

1. Rewrite the SQL CTE "each customer's order count, keep those with more than 5" as a MongoDB pipeline, and say which stage plays the CTE's role.
2. Using `$setWindowFields`, return every order with its rank (highest total = 1) within its customer.
3. Write the "2nd-highest-paid employee per department" pipeline. Which two stages do the work, and why must the filter be a separate stage?
4. Using `$shift`, add to each order the previous order's total for the same customer (ordered by date). What SQL function does `$shift` mirror?
5. A page loads 50 posts, then queries each post's author separately. Describe the two ways to fix this in MongoDB — one that keeps the reference, one that removes the need for it.
6. Explain why the "top 3 per group" pipeline needs a `$match` in a *later* stage rather than filtering inside `$setWindowFields`.

*Write your answers in [ch2-mongo-tryit.md](../../code/ch2-mongo-tryit.md).*

---

## The bumper sticker

> *Most "advanced SQL" is, in MongoDB, just more pipeline stages: a CTE is the chain you already write, a window function is `$setWindowFields`, a subquery is a `$lookup` sub-pipeline. And N+1 is database-agnostic — 1 query plus a loop quietly becomes 1 + N whether you reference rows or documents, so batch the fetch or embed the data.*

Next: stop querying and look under the hood — what MongoDB actually does with your query, why indexes make it fast, and how its transaction and consistency guarantees compare to ACID.

---

<div align="right">

[Chapter 3 (MongoDB companion) →](ch3-mongo.md)

</div>
