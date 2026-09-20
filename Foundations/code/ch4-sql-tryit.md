# Chapter 4: Designing the schema — Try it

*Answers for the Try it questions in [ch4-sql.md](../1-sql-and-databases/sql/ch4-sql.md).*

1. A junior dev stores each blog post with the author's name and bio copied into every post row. Name two specific problems this causes and how you'd fix the schema.


2. Give the one-sentence summary of what normalization is and what it prevents.


3. You're modeling students and the courses they enroll in. What tables do you need, and why can't a single foreign key express this relationship?


4. Give a concrete example where you'd *deliberately* denormalize, and state the cost you're accepting.


5. A team wants to switch from Postgres to MongoDB "because NoSQL scales better." What questions would you ask before agreeing, and what kind of data would actually justify the switch?


6. Explain how document databases' "embedding" relates to the concept of denormalization.


7. You're modeling a MongoDB collection of users, each with a growing list of their activity events. Would you embed the events in the user document or reference them in a separate collection? What breaks if you choose wrong?
