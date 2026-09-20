# Chapter 1 (MongoDB companion): Querying, both ways

*[SQL twin: Chapter 1](../sql/ch1-sql.md) · [Contents](../../foundations-README.md)*

- [ ] **Mark as read**

This is a companion to [Chapter 1](../sql/ch1-sql.md), written for the way *you* already think — in documents, not rows. The canonical chapters teach the four data topics through SQL because SQL is still what most interviewers reach for when they say "write me a query." But the thing being tested is never really the syntax; it's whether you understand *what the database is doing*. So in this companion we do every concept **mechanism first** — the idea that's true of any database — and only then show it twice: once in SQL, once in MongoDB. Learn the mechanism once and both dialects become surface detail.

The track's principle carries straight over: **feel the mechanism before trusting the abstraction.** A JOIN and a `$lookup` are two spellings of the same idea. Once you see the idea, you stop memorizing either one.

---

## The same job, two shapes for the data

Before any query, get the vocabulary lined up, because most SQL-vs-Mongo confusion is just two words for one thing.

> 💡 **Concept notes — the vocabulary map**
> Relational and document databases store the *same* information in two shapes:
> - A **table** is a **collection**. Both are "a bunch of similar things."
> - A **row** is a **document**. One customer, one order.
> - A **column** is a **field**. But a row's columns are fixed by the table's schema, while a document's fields can vary document to document — that flexibility is the headline difference.
> - A **primary key** is the **`_id`** field. MongoDB gives every document a unique `_id` automatically (an `ObjectId`) if you don't set one.
> - A **foreign key** — a column pointing at another table's key — has no enforced equivalent. In Mongo you either **store the other document's `_id`** and look it up yourself (a *reference*), or you **nest the related data right inside** the document (*embedding*). That one choice, embed vs reference, is the whole of document modeling, and it's Chapter 4's companion.
> The mental shift: relational splits data across tables and *joins it back*; document tends to *keep together what's read together*. Same data, different default.

---

## Declarative either way: you say *what*, not *how*

Chapter 1's opening idea — SQL is **declarative**, you describe the result and the planner figures out the *how* — is just as true in MongoDB. `find()` takes a filter describing the documents you want; the query engine decides whether to scan the collection or use an index (Chapter 3's companion). You're not writing the loop either way.

---

## The core query: pick documents, filter them

Pick some fields, from a collection, filtered by a condition.

```sql
-- SQL
SELECT name, email
FROM customers
WHERE country = 'Germany';
```

```js
// MongoDB
db.customers.find(
  { country: "Germany" },   // the filter — like WHERE
  { name: 1, email: 1, _id: 0 }  // the projection — like the SELECT list
)
```

> 💡 **Concept notes — the pieces line up**
> - `SELECT` columns ↔ the **projection** (second argument): `{ name: 1, email: 1 }` means "give me these fields." `_id: 0` opts out of the always-on `_id`.
> - `FROM table` ↔ the **collection** you call `.find()` on.
> - `WHERE condition` ↔ the **filter** (first argument): `{ country: "Germany" }`.
> - Operators translate almost one to one, they just move inside the field: `=` is `{ country: "Germany" }`; `<>` is `{ status: { $ne: "closed" } }`; `<`/`>` are `$lt`/`$gt`; `IN (...)` is `{ status: { $in: [...] } }`; `BETWEEN a AND b` is `{ total: { $gte: a, $lte: b } }`; `LIKE 'A%'` is a regex `{ name: /^A/ }`.
> The one genuinely different gotcha is **null**. In SQL, `NULL` means "unknown" and `WHERE x = NULL` matches nothing — you must use `IS NULL`. In MongoDB there are *two* things SQL folds into one: a field can be present-and-`null`, or **missing entirely**. `{ x: null }` matches *both* the null and the missing. To catch only documents where the field truly exists, use `{ x: { $exists: true, $ne: null } }`. This missing-vs-null distinction is the document world's version of the classic NULL trap.

---

## Sorting and trimming

```sql
-- SQL
SELECT name, total
FROM orders
ORDER BY total DESC
LIMIT 10;
```

```js
// MongoDB
db.orders.find({}, { name: 1, total: 1 })
  .sort({ total: -1 })  // -1 = descending, 1 = ascending
  .limit(10);
```

`ORDER BY ... DESC` ↔ `.sort({ total: -1 })`; `LIMIT 10` ↔ `.limit(10)`. Same "top N" job, same mechanism: sort the result, then trim.

---

## Combining data: JOIN vs `$lookup` (and why you often skip it)

In SQL, data is split across tables to avoid duplication, and a **JOIN** stitches it back on a shared key. MongoDB *can* do this too — the aggregation stage `$lookup` — but the document-native instinct is different: if two things are always read together, you **embed** one inside the other and there's nothing to join. So the honest framing is: *a `$lookup` is what you do when you chose to reference instead of embed.*

```sql
-- SQL: every order paired with its customer
SELECT customers.name, orders.total
FROM customers
JOIN orders ON orders.customer_id = customers.id;
```

```js
// MongoDB: same, when orders reference a customer _id
db.customers.aggregate([
  { $lookup: {
      from: "orders",
      localField: "_id",
      foreignField: "customer_id",
      as: "orders"          // matches land in a new array field
  }}
]);
```

> 💡 **Concept notes — the join types, translated**
> A `$lookup` always returns *all* left-side documents, with matches gathered into an array (empty if none) — so by itself it behaves like a **LEFT JOIN**. To get the other shapes you add a `$unwind`:
> - **INNER JOIN** (only rows matching in both): `$lookup` then `$unwind: "$orders"` — unwinding drops documents whose array is empty, so unmatched customers disappear.
> - **LEFT JOIN** (all left rows, nulls where no match): `$lookup` alone, or `$unwind` with `{ preserveNullAndEmptyArrays: true }` to keep the customers who have no orders.
> - The classic "customers who **never** ordered" (a LEFT JOIN where the right side `IS NULL`) becomes: `$lookup`, then `{ $match: { orders: { $eq: [] } } }` — keep only the ones whose matched array came back empty.
> The mental picture is identical to Chapter 1: LEFT = the whole left circle, INNER = the overlap. The only new idea is that Mongo hands you the matches as a *nested array* instead of flattened columns — which is a hint that if you needed this join *often*, you'd probably have embedded the orders in the first place.

---

## GROUP BY vs the aggregation pipeline

When you want a number *per group* — revenue per customer, orders per day — SQL uses `GROUP BY` with aggregate functions. MongoDB uses the **aggregation pipeline**: a list of stages, each transforming the stream of documents and feeding the next. Grouping is the `$group` stage.

```sql
-- SQL
SELECT customer_id, COUNT(*) AS order_count, SUM(total) AS revenue
FROM orders
WHERE status = 'completed'   -- filter rows first
GROUP BY customer_id
HAVING SUM(total) > 1000;     -- then filter groups
```

```js
// MongoDB
db.orders.aggregate([
  { $match: { status: "completed" } },                 // WHERE: filter rows first
  { $group: {
      _id: "$customer_id",                             // GROUP BY key
      order_count: { $sum: 1 },                        // COUNT(*)
      revenue: { $sum: "$total" }                      // SUM(total)
  }},
  { $match: { revenue: { $gt: 1000 } } }               // HAVING: filter groups after
]);
```

> 💡 **Concept notes — WHERE/HAVING is just where the `$match` sits**
> The rule that trips everyone in SQL — `WHERE` filters rows *before* grouping, `HAVING` filters groups *after* — becomes wonderfully literal in a pipeline. It's the *same* `$match` stage; what makes it a "WHERE" or a "HAVING" is simply whether it comes **before or after** `$group`. A `$match` before `$group` can't reference `revenue` because that field doesn't exist yet; a `$match` after `$group` can. That's the execution-order lesson from Chapter 1 made visible — in a pipeline you literally *see* the order, top to bottom, instead of writing the clauses in one order and having them run in another. The `_id` of a `$group` is the grouping key (set it to `null` to aggregate the whole collection into one number), and every output field must be built with an accumulator like `$sum`, `$avg`, `$min`, `$max`, `$first` — the document-world echo of "every SELECT column must be grouped or aggregated."

---

## Try it

Collections: `customers` (documents with `_id`, `name`, `country`), `orders` (documents with `_id`, `customer_id`, `total`, `status`, `created_at`).

1. Write the MongoDB `find()` for "name and email of every customer in Germany," and say which argument is the WHERE and which is the SELECT.
2. A field `discount` is missing on some order documents and explicitly `null` on others. Write the filter that matches *only* documents where `discount` genuinely holds a non-null value — and explain why `{ discount: { $ne: null } }` alone isn't quite it.
3. Translate `SELECT name, total FROM orders ORDER BY total DESC LIMIT 5` into MongoDB.
4. Write the aggregation that finds, per customer, their order count and total revenue, keeping only customers whose revenue exceeds 1000. Mark which stage is the WHERE and which is the HAVING.
5. In one sentence each: when would you `$lookup` orders onto customers, and when would you have embedded the orders instead so there's nothing to look up?
6. Write the "customers who never ordered" query in MongoDB, and name the SQL join it mirrors.

*Write your answers in [ch1-mongo-tryit.md](../../code/ch1-mongo-tryit.md).*

---

## The bumper sticker

> *A row is a document, a table is a collection, a JOIN is a `$lookup` — and `GROUP BY ... HAVING` is just a `$match` sitting after `$group` in a pipeline. Learn the mechanism once and SQL and MongoDB are two accents of the same language; the pipeline even makes execution order something you can see instead of memorize.*

Next: the "advanced" querying — window functions, CTEs, subqueries, and the N+1 trap — and how each of those maps onto the aggregation pipeline.

---

<div align="right">

[Chapter 2 (MongoDB companion) →](ch2-mongo.md)

</div>
