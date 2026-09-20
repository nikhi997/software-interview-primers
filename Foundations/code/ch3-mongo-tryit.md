# Chapter 3 (MongoDB companion): What the database is actually doing — Try it

*Answers for the Try it questions in [ch3-mongo.md](../1-sql-and-databases/mongo/ch3-mongo.md).*

1. A query `{ email: "..." }` on a 5-million-document users collection takes 4 seconds. What's almost certainly missing, and which command confirms it before you change anything — and what field in its output gives it away?


2. Explain why you wouldn't put an index on every field of a write-heavy collection.


3. You have a compound index `{ country: 1, city: 1 }`. Which queries can use it: `country` only? `city` only? both? Then restate the ESR rule and give the ideal index for a query that equality-matches `status`, sorts by `created_at`, and ranges on `total`.


4. An interviewer says "NoSQL isn't ACID, right?" Give the accurate, up-to-date correction in two sentences.


5. Two users try to buy the last concert ticket at the same instant. Describe how you'd model and write this in MongoDB so exactly one succeeds — and say whether you'd even need a multi-document transaction.


6. What's the difference between write concern and read concern, and which one is MongoDB's answer to a dirty read?
