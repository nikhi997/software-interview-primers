# Chapter 4 (MongoDB companion): Designing the schema

*[← Chapter 3 (companion)](ch3-mongo.md) · [SQL twin: Chapter 4](../sql/ch4-sql.md) · [Contents](../../foundations-README.md)*

- [ ] **Mark as read**

[Chapter 4](../sql/ch4-sql.md) is about *structuring* data rather than querying it — and it's the chapter where thinking in documents changes the most, so this is the companion that pays off hardest. In the relational world the default is "normalize: every fact in one place, join to reassemble." In the document world the default flips to "keep together what's read together." Neither is more correct; they're two answers to the same question — *where do you put each fact?* — and the mature interview answer knows both and picks by access pattern.

The mechanism to feel: **schema design is deciding where each fact lives, once, versus copied.** Normalizing and embedding are the two ends of that one dial.

---

## The core mapping: normalize ↔ reference, denormalize ↔ embed

Everything in this chapter hangs off one translation. Hold it first, then the rest is detail.

> 💡 **Concept notes — the one mapping that matters**
> - **Normalization** (SQL's default) = store each fact once and **reference** it. In MongoDB that's keeping related data in a separate collection and storing its `_id` — the document-world *reference*, the equivalent of a foreign key.
> - **Denormalization** (SQL's deliberate exception) = duplicate/nest data for read speed. In MongoDB that's **embedding** — nesting the related data inside the parent document. Embedding *is* denormalization, made the everyday default instead of the exception.
> So the relational instinct is "normalize until joins hurt, then denormalize the hot paths"; the document instinct is "embed what's read together, reference what isn't." Same dial, opposite starting point. When a SQL interviewer asks "what's normalization?", you can answer it cleanly *and* add "in a document store the analogous decision is embed-vs-reference" — that shows range.

---

## Normalization's motivation still applies

The reason SQL normalizes — avoiding **update, insertion, and deletion anomalies** from duplicated data — doesn't vanish in MongoDB. If you copy a customer's name into every order document and the customer renames, you face the same update anomaly: fix every copy or your data contradicts itself. Embedding is a *choice to accept that risk* in exchange for read speed, made deliberately for data that is owned-by and read-with its parent. So the normal-forms intuition (each atomic fact ideally in one place) is still the baseline you deviate from on purpose — the deviation is just far more common here.

---

## Modeling relationships, the document way

The same three relationship shapes from Chapter 4 — one-to-many, many-to-many, one-to-one — each get an embed-or-reference decision.

> 💡 **Concept notes — the three shapes, translated**
> - **One-to-many** (a customer has many orders). SQL puts a foreign key on the "many" side (`orders.customer_id`). MongoDB has *two* good options: **embed** the many inside the one (orders as an array in the customer) when the list is bounded and read with the parent, or **reference** (each order its own document with a `customer_id`) when orders are numerous, large, or queried on their own. This *choice* is the new thing document modeling adds.
> - **Many-to-many** (students and courses). SQL requires a **join table** (`enrollments(student_id, course_id)`). MongoDB usually stores an **array of references** on one or both sides (a `course_ids` array on the student), and only creates a separate collection if the *relationship itself* carries data (a grade, an enrolment date) — at which point you've reinvented the join table on purpose.
> - **One-to-one** (a user and their profile). SQL either folds the columns into one table or splits with a unique foreign key. MongoDB almost always just **embeds** the profile in the user document — the one-to-one case is where embedding is nearly always right.

---

## Embed vs reference: the decision that defines document modeling

This is the heart of MongoDB schema design, and the direct analogue of normalize-vs-denormalize. (The canonical [Chapter 4](../sql/ch4-sql.md) covers it from the SQL side; here it's the main event.)

> 💡 **Concept notes — embed or reference?**
> - **Embed** (nest the related data inside the parent): a blog post with its comments as an array *inside* it. One read pulls the whole thing, no `$lookup`. Choose it when the child is *owned by* and *always read with* the parent, and won't grow without bound. Embedding turns a would-be multi-document transaction into a single atomic write (Chapter 3's companion) — a real bonus.
> - **Reference** (store the other document's `_id` and look it up): keep comments in their own collection with a `post_id`. Choose it when the related data is large, shared across parents, queried independently, or grows unboundedly.
> - **The trap unique to embedding: the unbounded array.** Nest something that keeps growing — every like, every event, every log line — and the document creeps toward MongoDB's **16 MB document limit** and gets slow to load *in full* even when you only wanted a field. When a nested list has no natural ceiling, **reference instead**, or use the **bucket** pattern below. Recognizing an unbounded array before it bites is a strong modeling signal.
> The reasoning is the same read-vs-write tradeoff as everywhere in this track: embedding optimizes reading the whole aggregate; referencing keeps writes small and avoids duplication.

> 💡 **Concept notes — a few named patterns worth recalling**
> Interviewers who go deep on MongoDB like to hear that modeling has known patterns, not just vibes:
> - **Subset** — embed the *hot* few (the 5 most recent comments) in the parent for the common read, keep the full set in a referenced collection. Best of both for "show a preview, load the rest on demand."
> - **Computed** — store a precomputed `order_count` or `total` on the document instead of aggregating every read. Denormalization by another name; the same "cache the hot read" move as a SQL rollup column.
> - **Bucket** — group many small time-series records into one document per time window (an hour of sensor readings as one bucketed document), taming what would otherwise be an unbounded array or billions of tiny documents.
> - **Extended reference** — a reference *plus* a copy of the one or two fields you always display (store `customer_id` **and** `customer_name` on the order), so the common read needs no `$lookup`. Accepts controlled duplication to kill an N+1.
> You don't need to drill all four; naming one or two when discussing a schema shows you model deliberately.

---

## The honest "SQL vs document" answer — from the document side

This is one of the most common database interview questions, and as a MongoDB-native engineer you're expected to answer it *without* either bashing SQL or overselling NoSQL. The mature answer is about fit.

> 💡 **Concept notes — the balanced answer**
> - **Relational (Postgres, MySQL):** fixed schema, relationships via foreign keys and joins, strong ACID across many rows. Best when data is structured and interconnected, relationships matter, and cross-entity correctness is critical — finance, orders, anything transactional. The default for most apps.
> - **Document (MongoDB):** flexible schema, related data often embedded, historically easier horizontal scaling. Best when data is hierarchical and read as a self-contained unit (a product with its variants), the schema evolves fast, or a document maps cleanly to an application object.
> Say it as fit, not fashion: **"relational for structured, relational, transactional data — which is most apps; document when the data is naturally hierarchical, schema-flexible, or read as one aggregate. It's about the data's shape and access pattern, not which is 'better.'"** The tell of a strong candidate is starting from **how the data is read and written** and letting the model fall out of that — the same instinct behind embed-vs-reference, one level up.

---

## Try it

1. A junior dev embeds the full author document — name, bio, join date — into every one of the author's blog posts. Name two specific problems and how you'd restructure. Which SQL anomaly is this?
2. Give the one-mapping summary: what does normalizing correspond to in MongoDB, and what does denormalizing correspond to?
3. You're modeling students and the courses they enroll in. Show the MongoDB shape, and say when you'd add a separate collection for the relationship anyway.
4. You're modeling users, each with a growing stream of activity events. Embed or reference? What exactly breaks if you choose wrong, and which limit do you hit?
5. Give a concrete case where you'd use the *extended reference* pattern, and state the duplication cost you're accepting and the problem it solves.
6. A team wants to switch from Postgres to MongoDB "because NoSQL scales better." What do you ask before agreeing, and what data shape would actually justify it?

*Write your answers in [ch4-mongo-tryit.md](../../code/ch4-mongo-tryit.md).*

---

## The bumper sticker

> *Document modeling is one dial: normalize↔reference, denormalize↔embed. Embed what's owned-by and read-with the parent (and gain atomic single-document writes); reference what's large, shared, or unbounded — and watch for the unbounded array creeping toward 16 MB. "SQL vs document" isn't better-vs-worse; it's structured-and-transactional vs hierarchical-and-read-as-a-unit, decided by how the data is read and written.*

Next: zoom all the way out — past relational and document to the full family of databases (key-value, wide-column, graph, and vector), and how to pick the right shape for an access pattern.

---

<div align="right">

[Chapter 5 (MongoDB companion) →](ch5-databases.md)

</div>
