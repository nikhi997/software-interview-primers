# Chapter 2: SQL you need to know but rarely write

*[← Chapter 1](ch1-sql.md) · [Contents](../../foundations-README.md)*

- [ ] **Mark as read**

Chapter 1 covered the queries you write daily. This chapter covers the ones you write *occasionally* but get *asked about* constantly — because they separate "can use SQL" from "actually understands SQL." Window functions especially are a favorite interview filter: they look intimidating, they're genuinely useful, and most people never quite learned them. Get comfortable here and you'll handle the SQL questions that make other candidates sweat.

---

## CTEs: naming a subquery to stay sane

A complex query nested inside another query is hard to read and harder to debug. A **Common Table Expression (CTE)** — the `WITH` clause — lets you name an intermediate result and build on it, top to bottom, like declaring a variable.

```sql
WITH customer_revenue AS (
    SELECT customer_id, SUM(total) AS revenue
    FROM orders
    GROUP BY customer_id
)
SELECT c.name, cr.revenue
FROM customer_revenue cr
JOIN customers c ON c.id = cr.customer_id
WHERE cr.revenue > 1000;
```

> 💡 **Concept notes — CTE vs subquery**
> A **subquery** is a query nested inside another (in the `FROM`, `WHERE`, or `SELECT`). A **CTE** is the same idea pulled out and *named* with `WITH`, so the main query reads cleanly. They're often interchangeable; CTEs win on readability and let you reference the same intermediate result multiple times. You can chain several CTEs (`WITH a AS (...), b AS (...)`) to build a pipeline of steps. When an interviewer hands you a gnarly multi-step problem, reaching for a CTE to break it into stages is a strong, senior-looking move.

---

## Window functions: aggregate without collapsing

Here's the big one. A `GROUP BY` *collapses* rows — group 100 orders into 1 row per customer, and you lose the individual orders. But often you want a per-group calculation *alongside each original row* — "show every order, and next to it, this customer's running total" or "rank each order within its customer." That's a **window function**: it computes across a set of rows *related to the current row* without collapsing anything.

```sql
SELECT
    customer_id,
    total,
    SUM(total) OVER (PARTITION BY customer_id) AS customer_total,
    ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY total DESC) AS rank_in_customer
FROM orders;
```

Every order row stays, but each gains two computed columns: the customer's overall total, and that order's rank within the customer.

> 💡 **Concept notes — anatomy of a window function**
> The `OVER (...)` clause is what makes a function a *window* function. Inside it:
> - **`PARTITION BY col`** — divides rows into groups (like `GROUP BY`, but without collapsing). Omit it to treat all rows as one window.
> - **`ORDER BY col`** — orders rows *within* each partition; required for ranking and running totals.
> Common window functions:
> - **`ROW_NUMBER()`** — a unique sequential number per partition (1, 2, 3...).
> - **`RANK()`** / **`DENSE_RANK()`** — ranking, where ties share a rank (RANK leaves gaps after ties, DENSE_RANK doesn't).
> - **`SUM/AVG/COUNT() OVER (...)`** — running or partition-wide aggregates.
> - **`LAG(col)`** / **`LEAD(col)`** — the value from the previous / next row (great for "compare each month to the one before").
> The killer interview question window functions solve: **"find the top 3 orders per customer"** or **"the 2nd highest salary per department."** With `GROUP BY` this is painful; with `ROW_NUMBER() OVER (PARTITION BY ... ORDER BY ... DESC)` and a filter `WHERE rn <= 3`, it's clean. If you learn one "advanced" SQL thing, learn this.

```sql
-- Top 3 orders per customer:
WITH ranked AS (
    SELECT *,
           ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY total DESC) AS rn
    FROM orders
)
SELECT * FROM ranked WHERE rn <= 3;
```

(Note: you need the CTE because you can't reference the window alias `rn` directly in a `WHERE` — execution order again, Chapter 1.)

---

## Subqueries in WHERE: filtering by another query

You can filter rows using the result of another query. Two flavors worth knowing:

> 💡 **Concept notes — IN, EXISTS, and correlated subqueries**
> - **`IN (subquery)`:** "customers who have at least one order" → `WHERE id IN (SELECT customer_id FROM orders)`.
> - **`NOT IN` / `NOT EXISTS`:** the "never ordered" question (also solvable with a LEFT JOIN, Chapter 1). *Caution:* `NOT IN` behaves surprisingly if the subquery can return `NULL` — `NOT EXISTS` is safer.
> - **Correlated subquery:** a subquery that references the outer query, run once per outer row. Powerful but can be slow (it's a loop). Often a JOIN or window function does the same thing faster — a useful thing to point out in an interview.

---

## The N+1 problem: a performance trap you must recognize

This one is less about SQL syntax and more about how SQL meets application code — and it's a *very* common interview and code-review topic. The **N+1 problem** is when your app runs 1 query to fetch a list, then 1 more query *per item* in that list — turning what should be 2 queries into 1 + N.

> 💡 **Concept notes — N+1 explained**
> Say you fetch 100 customers (1 query), then loop and fetch each customer's orders one at a time (100 more queries) — that's 101 queries where 2 would do. It usually creeps in through ORMs (object-relational mappers) that lazily load related data: the code looks innocent (`for customer in customers: print(customer.orders)`) but each `.orders` access fires a query. At 100 items it's slow; at 100,000 it's a production incident. **The fix:** fetch the related data up front in a single query — a JOIN, or an `IN (...)` over all the IDs at once ("eager loading"). Recognizing N+1 from a description ("it's slow and the logs show thousands of tiny identical queries") and naming the fix is a strong practical signal — it shows you understand the *boundary* between your code and the database, not just SQL in isolation.

---

## Try it

Tables: `customers(id, name)`, `orders(id, customer_id, total, created_at)`, `employees(id, name, department, salary)`.

1. Write a CTE that computes each customer's order count, then selects only those with more than 5 orders.
2. Using a window function, write a query that returns every order with a column showing its rank (highest total = 1) *within its customer*.
3. Write a query for the 2nd-highest-paid employee in each department.
4. Using `LAG`, write a query showing each order's total and the previous order's total for the same customer (ordered by date).
5. Explain the N+1 problem to a teammate in two sentences, and describe how you'd fix a page that loads 50 blog posts and then queries each post's author separately.
6. Why does the "top 3 per group" query need a CTE (or subquery) rather than just a `WHERE rn <= 3` in the same SELECT?

*Write your answers in [ch2-sql-tryit.md](../../code/ch2-sql-tryit.md).*

---

## The bumper sticker

> *Window functions are the "advanced" SQL that interviews actually test: they compute per-group results without collapsing rows, so "top N per group" becomes easy. Pair them with CTEs for readability — and always recognize the N+1 problem, where 1 query plus a loop quietly becomes 1 + N.*

Next: stop writing queries and look under the hood — what the database is actually *doing* with your query, why indexes make it fast, and what ACID really guarantees.

---

<div align="right">

[Chapter 3 →](ch3-sql.md)

</div>
