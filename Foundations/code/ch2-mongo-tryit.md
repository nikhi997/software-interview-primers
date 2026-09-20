# Chapter 2 (MongoDB companion): Advanced querying, both ways — Try it

*Answers for the Try it questions in [ch2-mongo.md](../1-sql-and-databases/mongo/ch2-mongo.md).*

Collections: `customers` (`_id`, `name`), `orders` (`_id`, `customer_id`, `total`, `created_at`), `employees` (`_id`, `name`, `department`, `salary`).

1. Rewrite the SQL CTE "each customer's order count, keep those with more than 5" as a MongoDB pipeline, and say which stage plays the CTE's role.


2. Using `$setWindowFields`, return every order with its rank (highest total = 1) within its customer.


3. Write the "2nd-highest-paid employee per department" pipeline. Which two stages do the work, and why must the filter be a separate stage?


4. Using `$shift`, add to each order the previous order's total for the same customer (ordered by date). What SQL function does `$shift` mirror?


5. A page loads 50 posts, then queries each post's author separately. Describe the two ways to fix this in MongoDB — one that keeps the reference, one that removes the need for it.


6. Explain why the "top 3 per group" pipeline needs a `$match` in a *later* stage rather than filtering inside `$setWindowFields`.
