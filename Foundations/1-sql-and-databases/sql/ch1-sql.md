# Chapter 1: SQL you must be able to write

*[Contents](../../foundations-README.md)*

- [ ] **Mark as read**

If there's one technical skill that shows up in more interviews than any other besides plain coding, it's SQL. Backend, full-stack, data, even some frontend roles — at some point someone slides a table schema across the table (or screen) and says "write me a query that...". And here's the thing: SQL is *easy to fake until you're not.* You can muddle through simple `SELECT`s for years and then freeze on a `GROUP BY` with a `HAVING`. This chapter makes sure the everyday 80% — the queries you should be able to write without thinking — is genuinely automatic.

The principle for the whole track applies here immediately: **feel the mechanism.** SQL isn't a sequence of words you memorize; it's a description of *what data you want*, and the database figures out *how* to get it. Once you see it that way, the syntax stops being arbitrary.

---

## SQL is declarative — you say *what*, not *how*

Most code you write is **imperative**: you spell out the steps. SQL is **declarative**: you describe the *result* you want, and the database's query planner (Chapter 3) decides how to compute it. "Give me every customer in Germany who ordered in the last month" — you state the shape of the answer, not the loops to get there.

> 💡 **Concept notes — table, row, column**
> A relational database stores data in **tables** (like spreadsheets). Each **row** (or record) is one entity — one customer, one order. Each **column** (or field) is one attribute — name, email, total. A **primary key** is the column that uniquely identifies a row (usually `id`). A **foreign key** is a column in one table that points to a primary key in another (an `orders.customer_id` pointing at `customers.id`) — that's how tables *relate*, and it's what makes JOINs possible.

---

## The core query: SELECT ... FROM ... WHERE

The workhorse. Pick columns, from a table, filtered by a condition.

```sql
SELECT name, email
FROM customers
WHERE country = 'Germany';
```

> 💡 **Concept notes — the pieces**
> - `SELECT` — which columns you want (`*` means all, but name them explicitly in real code).
> - `FROM` — which table.
> - `WHERE` — the filter; only rows where the condition is true come back.
> - Common `WHERE` operators: `=`, `<>` (not equal), `<`, `>`, `IN (...)`, `BETWEEN a AND b`, `LIKE 'A%'` (pattern match), `IS NULL` / `IS NOT NULL`.
> A subtle but important one: `NULL` means "unknown," and comparisons with it are never true — `WHERE x = NULL` matches nothing. You must use `IS NULL`. This is a classic interview gotcha.

---

## ORDER BY and LIMIT: sorting and trimming

```sql
SELECT name, total
FROM orders
ORDER BY total DESC   -- biggest first
LIMIT 10;             -- only the top 10
```

`ORDER BY` sorts (`ASC` default, `DESC` for descending). `LIMIT` caps how many rows return — essential for "top N" questions and for not accidentally pulling a million rows.

---

## JOIN: combining tables

This is where SQL gets real, and where interviews concentrate. Data is split across tables (customers in one, orders in another) to avoid duplication (Chapter 4 explains *why*). A **JOIN** stitches them back together on a shared key.

```sql
SELECT customers.name, orders.total
FROM customers
JOIN orders ON orders.customer_id = customers.id;
```

This pairs each order with its customer, matching `orders.customer_id` to `customers.id`.

> 💡 **Concept notes — the join types (know these cold)**
> - **INNER JOIN** (just `JOIN`): returns only rows with a match in *both* tables. A customer with no orders won't appear.
> - **LEFT JOIN** (left outer): returns *all* rows from the left table, plus matches from the right — and `NULL` where there's no match. "All customers, with their orders if any." This is the one people forget and the one interviewers love.
> - **RIGHT JOIN:** mirror of LEFT (all right-table rows). Rare in practice — people just flip the tables and use LEFT.
> - **FULL OUTER JOIN:** all rows from both sides, NULLs where no match. Rare.
> The mental picture: INNER = the *overlap*; LEFT = the *whole left circle*. The single most common interview JOIN question is "find customers who have *never* ordered" — which is a LEFT JOIN where the right side `IS NULL`:
> ```sql
> SELECT c.name
> FROM customers c
> LEFT JOIN orders o ON o.customer_id = c.id
> WHERE o.id IS NULL;   -- no matching order = never ordered
> ```

---

## GROUP BY: aggregating

When you want a number *per group* — total revenue per customer, count of orders per day — you `GROUP BY` the thing you're grouping on and apply an **aggregate function**.

```sql
SELECT customer_id, COUNT(*) AS order_count, SUM(total) AS revenue
FROM orders
GROUP BY customer_id;
```

> 💡 **Concept notes — aggregate functions and HAVING**
> - Aggregates collapse many rows into one value: `COUNT(*)`, `SUM(col)`, `AVG(col)`, `MIN(col)`, `MAX(col)`.
> - **The rule that trips everyone:** every column in your `SELECT` must either be *in* the `GROUP BY` or *inside* an aggregate. You can't `SELECT name` while grouping by `customer_id` unless `name` is also grouped or aggregated — the database wouldn't know *which* name to show for the group.
> - **`WHERE` vs `HAVING`:** `WHERE` filters *rows before* grouping; `HAVING` filters *groups after* aggregating. "Customers who spent over $1000 total" needs `HAVING SUM(total) > 1000`, because the sum doesn't exist until after grouping. Mixing these up is one of the most common SQL mistakes.
> ```sql
> SELECT customer_id, SUM(total) AS revenue
> FROM orders
> WHERE status = 'completed'      -- filter rows first
> GROUP BY customer_id
> HAVING SUM(total) > 1000;       -- then filter groups
> ```

---

## The twist that explains everything: execution order

Here's the insight that turns SQL from memorized incantation into something you *understand* — and it's a favorite interview question. **SQL is not executed in the order you write it.** You write `SELECT` first, but the database runs it almost last. The logical order is:

> 💡 **Concept notes — logical execution order**
> 1. **FROM** / **JOIN** — assemble the source tables.
> 2. **WHERE** — filter individual rows.
> 3. **GROUP BY** — bucket rows into groups.
> 4. **HAVING** — filter the groups.
> 5. **SELECT** — pick/compute the output columns.
> 6. **ORDER BY** — sort the result.
> 7. **LIMIT** — trim to N rows.
> This order explains the rules you just learned: why `WHERE` can't use an aggregate (aggregates don't exist until step 3, but `WHERE` runs at step 2 — that's what `HAVING` is for), and why you often *can't* reference a `SELECT` alias in `WHERE` (the alias isn't created until step 5) but *can* in `ORDER BY` (step 6, after SELECT). When an interviewer asks "why doesn't this query work?", the answer is very often "because of execution order." Knowing this one list makes you look like you actually understand SQL rather than having memorized patterns.

---

## Try it

For these, assume tables `customers(id, name, country)` and `orders(id, customer_id, total, status, created_at)`.

1. Write a query for the names of all customers in Canada.
2. Write a query for the top 5 orders by `total`, highest first.
3. Write a query for each customer's name and how many orders they've placed (including customers with zero orders).
4. Write a query for customers whose *total* spending exceeds $5000.
5. Why does `WHERE total > AVG(total)` fail, and how would you express "orders above the average order total" correctly?
6. Explain, in execution-order terms, why you can use a `SELECT` alias in `ORDER BY` but not in `WHERE`.

*Write your answers in [ch1-sql-tryit.md](../../code/ch1-sql-tryit.md).*

---

## The bumper sticker

> *SQL is declarative — you describe the result and the database finds the path. Master SELECT/WHERE/JOIN/GROUP BY, know your join types cold, and remember the query runs in a different order than you write it: FROM, WHERE, GROUP BY, HAVING, SELECT, ORDER BY, LIMIT. That one list explains half of SQL's "gotchas."*

Next: the SQL you don't write every day but get asked about anyway — window functions, CTEs, and the subtle performance trap called the N+1 problem.

---

<div align="right">

[Chapter 2 →](ch2-sql.md)

</div>
