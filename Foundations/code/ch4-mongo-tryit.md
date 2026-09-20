# Chapter 4 (MongoDB companion): Designing the schema — Try it

*Answers for the Try it questions in [ch4-mongo.md](../1-sql-and-databases/mongo/ch4-mongo.md).*

1. A junior dev embeds the full author document — name, bio, join date — into every one of the author's blog posts. Name two specific problems and how you'd restructure. Which SQL anomaly is this?


2. Give the one-mapping summary: what does normalizing correspond to in MongoDB, and what does denormalizing correspond to?


3. You're modeling students and the courses they enroll in. Show the MongoDB shape, and say when you'd add a separate collection for the relationship anyway.


4. You're modeling users, each with a growing stream of activity events. Embed or reference? What exactly breaks if you choose wrong, and which limit do you hit?


5. Give a concrete case where you'd use the *extended reference* pattern, and state the duplication cost you're accepting and the problem it solves.


6. A team wants to switch from Postgres to MongoDB "because NoSQL scales better." What do you ask before agreeing, and what data shape would actually justify it?
