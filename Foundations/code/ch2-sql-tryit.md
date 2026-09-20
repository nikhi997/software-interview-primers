# Chapter 2: SQL you need to know but rarely write — Try it

*Answers for the Try it questions in [ch2-sql.md](../1-sql-and-databases/sql/ch2-sql.md).*

Tables: `customers(id, name)`, `orders(id, customer_id, total, created_at)`, `employees(id, name, department, salary)`.

1. Write a CTE that computes each customer's order count, then selects only those with more than 5 orders.


2. Using a window function, write a query that returns every order with a column showing its rank (highest total = 1) *within its customer*.


3. Write a query for the 2nd-highest-paid employee in each department.


4. Using `LAG`, write a query showing each order's total and the previous order's total for the same customer (ordered by date).


5. Explain the N+1 problem to a teammate in two sentences, and describe how you'd fix a page that loads 50 blog posts and then queries each post's author separately.


6. Why does the "top 3 per group" query need a CTE (or subquery) rather than just a `WHERE rn <= 3` in the same SELECT?
