# Chapter 1 (MongoDB companion): Querying, both ways — Try it

*Answers for the Try it questions in [ch1-mongo.md](../1-sql-and-databases/mongo/ch1-mongo.md).*

Collections: `customers` (documents with `_id`, `name`, `country`), `orders` (documents with `_id`, `customer_id`, `total`, `status`, `created_at`).

1. Write the MongoDB `find()` for "name and email of every customer in Germany," and say which argument is the WHERE and which is the SELECT.


2. A field `discount` is missing on some order documents and explicitly `null` on others. Write the filter that matches *only* documents where `discount` genuinely holds a non-null value — and explain why `{ discount: { $ne: null } }` alone isn't quite it.


3. Translate `SELECT name, total FROM orders ORDER BY total DESC LIMIT 5` into MongoDB.


4. Write the aggregation that finds, per customer, their order count and total revenue, keeping only customers whose revenue exceeds 1000. Mark which stage is the WHERE and which is the HAVING.


5. In one sentence each: when would you `$lookup` orders onto customers, and when would you have embedded the orders instead so there's nothing to look up?


6. Write the "customers who never ordered" query in MongoDB, and name the SQL join it mirrors.
