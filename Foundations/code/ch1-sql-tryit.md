# Chapter 1: SQL you must be able to write — Try it

*Answers for the Try it questions in [ch1-sql.md](../1-sql-and-databases/sql/ch1-sql.md).*

For these, assume tables `customers(id, name, country)` and `orders(id, customer_id, total, status, created_at)`.

1. Write a query for the names of all customers in Canada.


2. Write a query for the top 5 orders by `total`, highest first.


3. Write a query for each customer's name and how many orders they've placed (including customers with zero orders).


4. Write a query for customers whose *total* spending exceeds $5000.


5. Why does `WHERE total > AVG(total)` fail, and how would you express "orders above the average order total" correctly?


6. Explain, in execution-order terms, why you can use a `SELECT` alias in `ORDER BY` but not in `WHERE`.
