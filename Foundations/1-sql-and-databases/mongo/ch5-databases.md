# Chapter 5 (MongoDB companion): The database families

*[← Chapter 4 (companion)](ch4-mongo.md) · [Contents](../../foundations-README.md)*

- [ ] **Mark as read**

The first four companions lived inside the relational-vs-document rivalry. This one zooms all the way out. "SQL vs NoSQL" is a question interviewers love, but the strong answer isn't picking a side — it's knowing that **"NoSQL" is a whole family of stores, each earning its place from a different access pattern.** Relational and document are just the two you've met. Here we walk the rest — key-value, wide-column, graph, and the one that's exploded in the AI era, vector — so that when someone describes a problem, you reach for the *shape* that fits how the data is read and written, not the brand you happen to know.

The principle, one last time: **feel the mechanism.** Every store here exists because some access pattern was painful in the others. Derive the store from the pain and you never have to memorize a list.

---

## The one idea: pick the store by access pattern

There is no "best database." There's the store whose native shape matches how you *read and write* your data. Every family below drops something the relational model gives you — usually rich joins and multi-record transactions — to buy something else: raw speed, horizontal scale, or a query shape that would make SQL joins explode. Recognizing *what was traded for what* is the whole skill.

---

## The families, each from its pain

> 💡 **Concept notes — relational and document (recap)**
> - **Relational (Postgres, MySQL):** tables, fixed schema, joins, strong ACID. The pain it solves: keeping structured, interconnected, transactional data correct. Still the right default for most apps.
> - **Document (MongoDB):** queryable JSON-like documents, flexible schema, embed-or-reference modeling. The pain it solves: data that's hierarchical and read as one self-contained aggregate, and schemas that evolve fast. This is your home base — the last four companions.

> 💡 **Concept notes — key-value (Redis, DynamoDB)**
> A giant distributed dictionary: `get(key)` / `put(key, value)`, and almost nothing else — no querying *across* values. The pain it solves: you need a specific value *fast*, by a key you already know. Perfect for **caches, sessions, rate limiters, feature flags, leaderboards.** The trade: you give up ad-hoc queries entirely — if you can't name the key, you can't find the value. A document store is really a key-value store where the value is *queryable*; strip the queryability and you get raw key-value speed.

> 💡 **Concept notes — wide-column (Cassandra, HBase, Bigtable)**
> Rows with flexible columns, partitioned across many machines for enormous **write throughput** and linear scale. The pain it solves: firehose write volume — **time-series, event logs, feeds, telemetry at massive scale** — where a single relational primary would fall over. The trade: you design the table around *one* query pattern up front (the partition key decides everything), joins are gone, and consistency is typically tunable/eventual. Great when writes vastly outnumber reads and the read patterns are known and few.

> 💡 **Concept notes — graph (Neo4j, and graph features elsewhere)**
> Nodes and edges as first-class citizens, with the *relationships* stored directly rather than reconstructed by joins. The pain it solves: **relationship-heavy traversal** — "friends of friends of friends," recommendation paths, fraud rings, dependency graphs — where each hop in SQL is another self-join and a five-hop query becomes a monster. The trade: it's specialized; for flat, tabular data it buys you nothing. The tell that a graph fits: the *connections* are the point, and the questions are about paths between things, not the things themselves.

> 💡 **Concept notes — vector (pgvector, Pinecone, Milvus, MongoDB Atlas Vector Search)**
> The newest family, and the one interviewers increasingly probe because it powers modern AI. It stores **embeddings** — high-dimensional numeric vectors that encode the *meaning* of text, images, or audio — and answers **similarity** queries: "find the items whose vectors are nearest to this one." The pain it solves: **semantic search and retrieval** — matching by meaning rather than exact keywords — which is the retrieval half of a **RAG** (retrieval-augmented generation) system and the backbone of recommendation and dedup. See the AI/ML track for how embeddings are produced and used.
> - **Why it needs its own index:** finding the exact nearest neighbors in hundreds of dimensions is brutally slow, so vector databases use **ANN (approximate nearest neighbor)** indexes — most commonly **HNSW** (Hierarchical Navigable Small World), a layered graph you greedily walk to *near*-nearest neighbors in log-ish time. The trade you're making is explicit and worth naming: **a little accuracy for enormous speed** — ANN may miss the exact closest match but returns very-close ones fast enough for interactive search.
> - **The interview move:** "vectors store meaning as coordinates; similarity search is a nearest-neighbor query; and because exact NN is too slow at scale, we use an ANN index like HNSW that trades a little recall for a lot of speed." Note too that this often isn't a *separate* database — Postgres (`pgvector`) and MongoDB (Atlas Vector Search) bolt vector search onto the store you already run, so the honest recommendation is frequently "add vectors to your existing database, don't adopt a new one unless scale demands it."

> 💡 **Concept notes — a couple more you might hear named**
> - **Search engines (Elasticsearch, OpenSearch):** inverted-index full-text search — the pain of "find every document containing these words, ranked by relevance," which `LIKE '%...%'` does terribly.
> - **Time-series (InfluxDB, Timescale, Mongo time-series collections):** wide-column's specialization for timestamped metrics, with built-in downsampling and retention.
> - **Columnar / OLAP (Snowflake, BigQuery, ClickHouse):** store by *column* not row, so analytical scans over billions of rows (`SUM` across one column) fly — the pain of analytics, versus the row-oriented stores tuned for transactional reads and writes.

---

## The tradeoff underneath all of them: consistency vs scale

Most non-relational stores distribute data across many machines, and that forces a choice relational single-nodes could dodge.

> 💡 **Concept notes — CAP, the one-liner**
> **CAP** says that when a network **partition** (P) splits your nodes — which *will* happen at scale — you must choose between **consistency** (C: every read sees the latest write) and **availability** (A: every request still gets an answer). You can't have both during a partition. Relational systems and MongoDB lean **CP** (refuse or delay rather than serve stale data — Chapter 3's write/read concern is exactly this dial); Cassandra and DynamoDB lean **AP** (stay up, reconcile later — "eventual consistency"). The interview-grade framing: **"it's not that NoSQL is 'less safe' — it's that distributed stores trade some immediate consistency for availability and scale, and you pick where you want to sit on that line based on whether stale reads or downtime hurts your app more."** That single sentence turns "SQL vs NoSQL" from a slogan into an engineering judgment.

---

## Try it

1. State the one idea of this chapter in a sentence: how do you choose among database families?
2. For each, name the access-pattern pain that justifies it: key-value, wide-column, graph, vector.
3. A feature needs "find products similar in *meaning* to this description." Which family, what does it store, and what kind of index makes it fast — and what does that index trade away?
4. Explain HNSW and ANN to an interviewer in two sentences, including the tradeoff you're accepting.
5. A social app needs "people you may know (friends of friends of friends)." Which store fits, and why does doing this in SQL get painful?
6. State CAP in one sentence, then say which side (CP or AP) MongoDB and Cassandra each lean toward and what that means for a user during a network partition.
7. A team says "let's add a dedicated vector database." When is that premature, and what's the lighter first step?

*Write your answers in [ch5-databases-tryit.md](../../code/ch5-databases-tryit.md).*

---

## The bumper sticker

> *"NoSQL" isn't one thing — it's a family, and each member earns its place from an access pattern the others handle badly: key-value for get-by-key speed, wide-column for write firehoses, graph for relationship traversal, vector for meaning-based similarity. Pick the shape that matches how you read and write, remember most of them trade some consistency for scale (CAP), and know that vector search — embeddings plus an ANN index like HNSW — is increasingly just a feature you add to the database you already run.*

That closes the MongoDB companion. From here, rejoin the main track at [Chapter 5 (Processes, threads, and concurrency)](../../2-operating-systems/ch5-os.md) — the operating-systems layer beneath every database you've just mapped.

---

<div align="right">

[Contents](../../foundations-README.md)

</div>
