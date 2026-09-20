# Chapter 3: What the database is actually doing — Try it

*Answers for the Try it questions in [ch3-sql.md](../1-sql-and-databases/sql/ch3-sql.md).*

1. A query `WHERE email = '...'` on a 5-million-row users table takes 4 seconds. What's almost certainly missing, and how would you confirm it before making a change?


2. Explain why you wouldn't just add an index to every column in a table. What's the cost?


3. You have a composite index on `(country, city)`. Which of these queries can use it: filter by `country` only? by `city` only? by both? Why?


4. Define each letter of ACID in one sentence, with the bank-transfer example for Atomicity.


5. Two users try to buy the last concert ticket at the same moment. Which ACID property is most relevant to making sure only one succeeds, and why?


6. What's a dirty read, and which isolation level is the lowest that prevents it?
