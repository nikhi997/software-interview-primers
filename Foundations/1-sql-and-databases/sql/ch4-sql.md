# Chapter 4: Designing the schema

*[← Chapter 3](ch3-sql.md) · [Contents](../../foundations-README.md)*

- [ ] **Mark as read**

The last three chapters were about *querying* data. This one is about *structuring* it — deciding what tables exist, what columns they hold, and how they relate. It's the closing chapter of the SQL & databases section, and it answers the design questions that come up both in pure-fundamentals rounds ("what's normalization?") and inside system-design interviews ("how would you model this?"). The mechanism to feel here: good schema design is mostly about *where you put each fact* — once, in the right place, versus copied everywhere.

---

## Normalization: every fact in exactly one place

**Normalization** is the discipline of organizing tables so that each piece of information lives in *one* place, with no redundant duplication. The motivation is concrete and worth feeling.

> 💡 **Concept notes — why duplication is dangerous**
> Imagine storing each order with the customer's full name and address copied into every order row. Now the customer moves. You must update *every* order — miss one and your data contradicts itself (an **update anomaly**). Other failures: you can't store a customer who has no orders yet (**insertion anomaly**), and deleting their last order erases their details entirely (**deletion anomaly**). Normalization removes these by storing the customer *once* in a `customers` table and pointing to it from `orders` via a foreign key. One fact, one place.

> 💡 **Concept notes — the normal forms (the gist, not the rote)**
> Normalization comes in numbered "normal forms." You rarely need to recite the formal definitions, but know the progression:
> - **1NF (First Normal Form):** each cell holds a single atomic value — no comma-separated lists or repeating groups in a column.
> - **2NF:** every non-key column depends on the *whole* primary key (matters mainly for composite keys).
> - **3NF:** no column depends on another non-key column (no "transitive" dependencies — e.g., don't store `zip_code` *and* the `city` it implies in the same table).
> The practical summary interviewers want: **"normalization means no redundant data — each fact stored once — which prevents update anomalies; in practice I aim for 3NF."** That sentence covers 90% of what's asked.

---

## Denormalization: breaking the rules on purpose

Normalization is the default, but it has a cost: to assemble a full picture you must `JOIN` many tables, and joins take time. So sometimes you *deliberately* duplicate data for speed. That's **denormalization** — and knowing *when* to do it is a senior signal.

> 💡 **Concept notes — the normalize/denormalize tradeoff**
> - **Normalized** = no duplication, easy and safe writes, but reads need joins (slower for complex reads).
> - **Denormalized** = some data copied/precomputed, so reads are fast (fewer joins), but writes are harder and you risk inconsistency (the same fact in two places can drift apart).
> The rule of thumb: **normalize until it's too slow, then denormalize the specific hot paths — consciously.** Examples of justified denormalization: storing a precomputed `order_count` on the customer instead of `COUNT`-ing every time; a read-heavy analytics table; caching a display name. This is the same **read-heavy vs write-heavy** tradeoff as indexing (Chapter 3) — denormalization optimizes reads at the expense of write complexity. Saying "I'd start normalized and denormalize specific read-hot paths if profiling shows the joins are the bottleneck" is exactly the balanced answer interviewers look for.

---

## Modeling relationships

Schema design is largely about expressing how entities relate. Three shapes cover almost everything.

> 💡 **Concept notes — one-to-many, many-to-many, one-to-one**
> - **One-to-many** (most common): one customer has many orders. Implement with a **foreign key** on the "many" side — `orders.customer_id` points to `customers.id`.
> - **Many-to-many:** a student takes many courses; a course has many students. You can't put a foreign key on either side alone — you need a **join table** (a.k.a. junction/bridge table) like `enrollments(student_id, course_id)`, each row linking one of each. Recognizing that M:N needs a third table is a classic schema question.
> - **One-to-one:** one user has one profile. A foreign key with a uniqueness constraint, or the columns folded into one table. Used to split rarely-accessed or sensitive columns off.

---

## Relational vs document: choosing the model

Not every database is a table-and-join relational database. The other big family is **document (NoSQL)** stores, and "SQL vs NoSQL" is one of the most common database interview questions. The honest answer is about *fit*, not fashion.

> 💡 **Concept notes — relational (SQL) vs document (NoSQL)**
> - **Relational (Postgres, MySQL):** data in tables with a fixed **schema**; relationships via foreign keys and joins; strong **ACID** guarantees. Best when data is structured and interconnected, relationships matter, and correctness is critical (finance, orders, anything transactional). The default choice for most applications.
> - **Document (MongoDB, etc.):** data in flexible, JSON-like **documents**; related data often **nested** inside one document instead of joined; schema can vary row to row; historically scaled horizontally more easily. Best when data is hierarchical and read as a unit (a product with its nested variants), the schema evolves fast, or you want a document to map directly to an object.
> The key mental shift: relational **normalizes and joins**; document often **embeds** (nests related data together to avoid joins) — which is essentially *denormalization by design*. That makes reads of a whole document fast, but duplicated nested data can drift, and cross-document consistency is weaker. The mature interview answer avoids dogma: **"relational for structured, relational, transactional data — which is most apps; document when the data is naturally hierarchical, schema-flexible, or read as a self-contained unit. It's about the data's shape and access pattern, not which is 'better.'"**

> 💡 **Concept notes — modeling a document: embed vs reference**
> The one decision that defines document modeling is **embed or reference?** — the document-store version of normalize-vs-denormalize.
> - **Embed** (nest the related data inside the parent document): a blog post with its comments as an array *inside* it. One read pulls the whole thing, no join. Choose it when the child is *owned by* and *always read with* the parent, and won't grow without bound.
> - **Reference** (store an id and look the other document up, like a foreign key): keep comments in their own collection with a `post_id`. Choose it when the related data is large, shared across parents, or grows unboundedly.
> The trap unique to document stores is the **unbounded array** — embedding something that keeps growing (every "like," every event) until the document hits its size limit or gets slow to load. When a nested list has no natural ceiling, reference instead. The reasoning is the same read-vs-write tradeoff as everywhere else: embedding optimizes the read of a whole aggregate; referencing keeps writes small and avoids duplication.

> 💡 **Concept notes — "NoSQL" is a family, not one thing**
> Document is the most common NoSQL store, but the label covers several shapes, each earning its place from an access pattern:
> - **Key-value (Redis, DynamoDB):** a giant dictionary — get/put by key, blazing fast, no querying across values. For caches, sessions, feature flags.
> - **Document (MongoDB):** key-value where the value is a *queryable* JSON document. For app data read as self-contained units.
> - **Wide-column (Cassandra, HBase):** rows with flexible columns, partitioned for huge write throughput. For time-series, event logs, feeds at massive scale.
> - **Graph (Neo4j):** nodes and edges as first-class citizens. For relationship-heavy queries ("friends of friends," fraud rings) where SQL joins would explode.
> The interview move isn't reciting all four — it's recognizing that "NoSQL" means "pick the store that matches how you read and write," and that most of these drop cross-entity joins and strong multi-record transactions to buy horizontal scale.

---

## Try it

1. A junior dev stores each blog post with the author's name and bio copied into every post row. Name two specific problems this causes and how you'd fix the schema.
2. Give the one-sentence summary of what normalization is and what it prevents.
3. You're modeling students and the courses they enroll in. What tables do you need, and why can't a single foreign key express this relationship?
4. Give a concrete example where you'd *deliberately* denormalize, and state the cost you're accepting.
5. A team wants to switch from Postgres to MongoDB "because NoSQL scales better." What questions would you ask before agreeing, and what kind of data would actually justify the switch?
6. Explain how document databases' "embedding" relates to the concept of denormalization.
7. You're modeling a MongoDB collection of users, each with a growing list of their activity events. Would you embed the events in the user document or reference them in a separate collection? What breaks if you choose wrong?

*Write your answers in [ch4-sql-tryit.md](../../code/ch4-sql-tryit.md).*

---

## The bumper sticker

> *Good schema design puts each fact in exactly one place — that's normalization, and it prevents data from contradicting itself. Denormalize only on purpose, for read-hot paths. And SQL vs NoSQL isn't about which is better; it's about whether your data is relational and transactional (SQL) or hierarchical and read as a unit (document).*

That closes the data section. Next we change layers entirely — down to the operating system, to understand processes, threads, and the concurrency bugs that haunt every backend.

---

<div align="right">

[Chapter 5 →](../../2-operating-systems/ch5-os.md)

</div>
