# Appendix: Foundations cheat-sheet kit

*[← Chapter 14](5-bonus/ch14-git.md) · [Contents](foundations-README.md)*

The skim-the-morning-of reference for the whole track: a SQL cheat sheet, OS and networking vocabularies, the four-step answer framework, and a question bank by chapter. Pair it with the fast-review grid in [Chapter 12](4-putting-it-together/ch12-ritual.md), the causal flows in [mechanism maps](foundations-mechanism-maps.md), and the timed spoken cards in [60-second recall](foundations-60-second-recall.md).

---

## SQL cheat sheet

### Query skeleton (written order)
```sql
SELECT   columns, AGG(col)
FROM     table
JOIN     other ON other.fk = table.id
WHERE    row_condition
GROUP BY columns
HAVING   group_condition
ORDER BY columns [ASC|DESC]
LIMIT    n;
```

### Logical execution order (what actually runs)
`FROM/JOIN → WHERE → GROUP BY → HAVING → SELECT → ORDER BY → LIMIT`

### JOIN types
| Type | Returns |
|---|---|
| `INNER JOIN` | Only rows matching in both tables (the overlap) |
| `LEFT JOIN` | All left rows + matches; NULL where no match |
| `RIGHT JOIN` | All right rows + matches (rare; flip and use LEFT) |
| `FULL OUTER JOIN` | All rows from both sides; NULL where no match |

"Customers who never ordered": `LEFT JOIN orders ... WHERE orders.id IS NULL`

### Aggregates & grouping
- Functions: `COUNT(*)`, `SUM`, `AVG`, `MIN`, `MAX`
- Rule: every SELECTed column must be grouped or aggregated
- `WHERE` filters rows *before* grouping; `HAVING` filters groups *after*

### Window functions
```sql
func() OVER (PARTITION BY col ORDER BY col)
```
- `ROW_NUMBER()`, `RANK()`, `DENSE_RANK()` — ranking
- `SUM/AVG() OVER (...)` — running / partition aggregate
- `LAG(col)`, `LEAD(col)` — previous / next row
- "Top N per group": rank in a CTE, then `WHERE rn <= N`

### CTE
```sql
WITH step1 AS (SELECT ...),
     step2 AS (SELECT ... FROM step1)
SELECT * FROM step2;
```

### Gotchas
- `NULL`: use `IS NULL` / `IS NOT NULL`, never `= NULL`
- Can't use aggregates in `WHERE` (use `HAVING`)
- Can't use a SELECT alias in `WHERE` (can in `ORDER BY`) — execution order
- N+1: 1 query + 1 per row; fix with a JOIN or `IN (...)` / eager loading

---

## Database vocabulary

| Term | One-liner |
|---|---|
| **Primary key** | Column uniquely identifying a row |
| **Foreign key** | Column pointing at another table's primary key |
| **Index** | Sorted structure (B-tree) → O(log n) lookups; speeds reads, slows writes |
| **B-tree** | Balanced sorted tree; fast lookups + range queries |
| **Composite index** | Index on multiple columns; leftmost-prefix rule |
| **EXPLAIN** | Shows query plan; full table scan on big table = missing index |
| **Query planner** | Decides *how* to execute your declarative SQL |
| **Transaction** | All-or-nothing group of operations (`BEGIN ... COMMIT`) |
| **ACID** | Atomicity, Consistency, Isolation, Durability |
| **Isolation levels** | Read Uncommitted → Committed → Repeatable Read → Serializable |
| **Dirty read** | Reading uncommitted data |
| **Normalization** | Each fact in one place; prevents update anomalies; aim 3NF |
| **Denormalization** | Deliberate duplication for read speed |
| **1NF/2NF/3NF** | Atomic cells / depend on whole key / no transitive deps |
| **One-to-many** | FK on the "many" side |
| **Many-to-many** | Needs a join/junction table |
| **SQL vs NoSQL** | Relational+transactional vs hierarchical/schema-flexible/document |
| **NoSQL families** | Key-value, document, wide-column, graph — pick by access pattern |
| **Document store** | JSON-like documents (MongoDB); embeds related data instead of joining |
| **Embed vs reference** | Nest child in parent (one read) vs store an id and look it up |
| **Unbounded array** | Embedding an ever-growing list until the document bloats — reference instead |

---

## Operating-systems vocabulary

| Term | One-liner |
|---|---|
| **Process** | Running program with its own isolated memory |
| **Thread** | Execution unit inside a process; **shares memory** with siblings |
| **Context switch** | OS saving/loading thread state to time-slice a core; not free |
| **Concurrency** | Dealing with many things at once (structure) |
| **Parallelism** | Doing many things at once (needs multiple cores) |
| **Race condition** | Outcome depends on thread timing on shared data |
| **Critical section** | Code touching shared data that must not be interrupted |
| **Mutex / lock** | Acquire before critical section; others wait; serializes access |
| **Semaphore** | Counter lock allowing up to N concurrent holders |
| **Deadlock** | Threads wait on each other's locks forever |
| **Coffman conditions** | Mutual exclusion, hold-and-wait, no preemption, circular wait |
| **Deadlock fix** | Acquire locks in a consistent global order (break circular wait) |
| **Stack** | Fast, automatic, short-lived locals & call frames; LIFO |
| **Heap** | Flexible, large, long-lived dynamic allocations; needs cleanup |
| **Stack overflow** | Stack exhausted (e.g., infinite recursion) |
| **Garbage collection** | Frees *unreachable* heap objects automatically |
| **Memory leak** | Memory never reclaimed; in GC = accidental retained reference |
| **Value vs reference** | Copy vs same underlying object passed to a function |
| **GIL** | One Python thread runs bytecode at a time; CPU-bound → multiprocessing |

---

## Networking vocabulary

| Term | One-liner |
|---|---|
| **IP address** | Numeric machine address; best-effort routing |
| **Port** | Identifies a program/service on a machine |
| **TCP** | Reliable, ordered, connection-oriented; every byte matters |
| **UDP** | Fast, connectionless, unreliable; speed beats completeness |
| **Three-way handshake** | SYN → SYN-ACK → ACK; costs a round trip before data |
| **HTTP** | Stateless request/response; methods GET/POST/PUT/DELETE |
| **Status codes** | 2xx success, 3xx redirect, 4xx client error, 5xx server error |
| **HTTPS / TLS** | HTTP + encryption; privacy, integrity, authentication (certificate) |
| **TLS handshake** | Cert + key exchange after TCP; asymmetric to set up symmetric key |
| **DNS** | Domain name → IP; cached with TTL; first step of any URL |
| **CDN** | Geo-distributed cache for static content near users |
| **Load balancer** | Distributes requests across servers; scaling + failover |
| **Cache (cache-aside)** | Check fast store first; on miss query DB and populate |
| **Cookie / token** | Carries identity in each request (HTTP is stateless) |
| **Session** | Server-side logged-in state keyed by cookie/token |
| **Authentication vs authorization** | Who are you? (verify identity) vs what may you do? (check permission) |
| **Password hashing + salt** | Store a one-way hash (bcrypt/argon2) + per-user random salt, never plaintext |
| **SQL injection / XSS** | Top web vulns: use parameterized queries; escape user content before rendering |
| **OAuth 2.0** | Delegated authorization: grant an app scoped, revocable access to your data without your password |
| **Scope / access token / refresh token** | Narrow permission grant / short-lived API key / quietly renews the access token |
| **OpenID Connect** | Thin identity layer on OAuth; powers "Sign in with Google" |
| **OWASP Top 10** | Consensus list of common web risks; recognize each so you don't build one |
| **Broken access control** | #1 risk: authenticated but not authorized — change an `id` and see others' data |
| **CSRF / SSRF** | Trick your logged-in browser into a request / trick your server into fetching an internal URL |

---

## Concurrency-patterns vocabulary

| Term | One-liner |
|---|---|
| **I/O-bound** | Mostly waiting (DB/network/disk); overlap with async/threads |
| **CPU-bound** | Mostly computing; needs real parallelism across cores |
| **Event loop** | One thread juggling tasks by never waiting idle |
| **async / await** | Mark async fn / yield point while waiting; single-thread concurrency |
| **Thread pool** | Fixed reusable workers fed by a task queue |
| **Multiprocessing** | Separate processes on separate cores; true parallelism (Python CPU-bound) |

---

## Python idioms vocabulary

| Idiom | One-liner |
|---|---|
| **List/dict/set comprehension** | `[expr for x in it if cond]` — map+filter in one expression; keep to one step |
| **Dict/set comprehension** | `{v: i for i, v in enumerate(nums)}` builds a lookup; `{x for x in it}` dedups |
| **2-D init / aliasing trap** | `[[0]*cols for _ in range(rows)]`; `[[0]*cols]*rows` aliases one row into every slot |
| **Ternary in comprehension** | `[x if x>0 else 0 for x in xs]` transforms every item; filter `if` goes at the end |
| **Generator / `yield`** | Lazy, one-at-a-time values; constant memory for huge/streamed data; single-use |
| **Generator expression** | `sum(x for x in it)` — like a comprehension but doesn't build the list |
| **Tuple unpacking** | `a, b = pair`; `first, *rest = seq`; `a, b = b, a` swap |
| **`@dataclass`** | Auto-generates `__init__`/`__repr__`/`__eq__` from typed fields; `frozen=True` for immutable |
| **Dunder methods** | `__repr__`, `__eq__`, `__lt__`, `__len__`, `__getitem__`, `__enter__/__exit__` — hook into Python syntax |
| **Context manager (`with`)** | Acquire-then-must-release; `__exit__` runs even on exception (files, locks, connections) |
| **`Counter`** | Dict that counts; `.most_common(n)` |
| **`defaultdict(list)`** | Auto-default for missing keys; grouping without existence checks |
| **`deque`** | O(1) append/pop at both ends; the right BFS-queue / sliding-window structure |
| **Type hints** | `x: int`, `-> bool`, `list[dict]`; documentation tools enforce, runtime doesn't |

---

## Version-control (Git) vocabulary

| Term | One-liner |
|---|---|
| **Commit** | Immutable snapshot + parent pointer(s), identified by a content hash |
| **Branch** | A movable pointer to a commit (cheap — just one hash) |
| **HEAD** | Pointer to where you are now; "detached" = pointing at a commit, not a branch |
| **Staging area (index)** | Holding pen for the next commit; `git add` puts changes here |
| **Working dir / staging / repo** | Edit → `git add` → `git commit` |
| **Merge** | New commit with two parents; preserves history, non-linear |
| **Rebase** | Replay commits onto a new base; linear history but new hashes — never on pushed work |
| **Merge conflict** | Both sides changed the same lines; Git declines to guess |
| **fetch / pull / push** | Download only / download+merge / upload; `pull` = `fetch` + merge |
| **revert vs reset** | Revert adds an undo commit (safe on shared); reset/`amend` rewrite history (local only) |
| **reflog** | Log of everywhere HEAD has been — the safety net after a bad reset |
| **Trunk-based / Gitflow** | Frequent integration into `main` vs many long-lived branches |

---

## The four-step answer framework (DART)

1. **Definition** — one crisp sentence: what it *is.*
2. **Analogy / mechanism** — how/why it works, with the mental picture.
3. **Reason / tradeoff** — why it exists and what it costs. *(The differentiator.)*
4. **Tie to practice** — when you'd use it / a real example.

---

## Question bank by chapter

**Ch 1 — SQL basics**
- Difference between WHERE and HAVING?
- Name the JOIN types; how do you find rows with no match on the other side?
- What's the logical execution order of a SQL query, and why does it matter?
- Why does `WHERE x = NULL` return nothing?

**Ch 2 — Advanced SQL**
- What's a window function and when do you need one over GROUP BY?
- Write "top 3 per group." Why does it need a CTE?
- What's the N+1 problem and how do you fix it?
- CTE vs subquery — when do you prefer a CTE?

**Ch 3 — DB internals**
- How does an index work? Why is it fast?
- Why not index every column?
- How would you debug a slow query?
- Explain ACID. Explain isolation levels and the anomalies they prevent.

**Ch 4 — Schema design**
- What is normalization and what does it prevent?
- When would you denormalize?
- How do you model a many-to-many relationship?
- SQL vs NoSQL — how do you choose?
- In a document store, when do you embed vs reference, and what's the unbounded-array trap?

**Ch 14 — Git**
- What is a commit, and what is a branch? Why is branching cheap?
- Merge vs rebase — and why must you never rebase pushed commits?
- How do you undo a commit you already pushed, and why `revert` over `reset`?
- What is a merge conflict, and why won't Git resolve it for you?
- What does `git pull` actually do under the hood?

**Ch 5 — Processes & threads**
- Process vs thread? Why is shared memory the source of concurrency bugs?
- What's a race condition? How do you prevent it?
- What's a deadlock and what are its four conditions? How do you prevent one?

**Ch 6 — Memory**
- Stack vs heap?
- What is garbage collection? Can a GC language still leak memory?
- Pass by value vs pass by reference?

**Ch 7 — Networking fundamentals**
- TCP vs UDP, with a use case for each?
- Walk through the TCP handshake.
- What does HTTPS/TLS add? What's a certificate for?
- What does DNS do?

**Ch 8 — Request journey**
- What happens when you type a URL and hit enter?
- Where does caching appear in that journey?
- What does a load balancer do?
- How does a stateless protocol keep you logged in?
- Authentication vs authorization — what's the difference?
- How should passwords be stored, and why hash + salt rather than encrypt?
- What problem does OAuth solve, and what makes its access token safe (scoped, expiring, revocable)?
- Beyond SQLi and XSS, name a few OWASP Top 10 risks; which two habits prevent most of the list?

**Ch 9 — Concurrency patterns**
- I/O-bound vs CPU-bound — how does it change your approach?
- How does an event loop achieve concurrency on one thread?
- What's the GIL and its consequence for CPU-bound Python?
- Async vs threads vs multiprocessing — when each?

**Ch 10 — Python: data and iteration**
- Rewrite a filter-and-transform loop as a comprehension. Where does the filter `if` go, and where does an `x if cond else y` ternary go?
- Build a value→index map in one line; when is a dict/set comprehension the right reach?
- Why does `[[0] * cols] * rows` corrupt every row, and what's the correct 2-D initializer?
- When is a generator the right call over a list comprehension? What does `yield` do to a function?
- `Counter`, `defaultdict`, `deque` — what bookkeeping does each remove?

**Ch 11 — Python: objects and idioms**
- What does `@dataclass` generate for you, and when would you reach for it? What does `frozen=True` add?
- Your object prints as `<... object at 0x...>` and won't sort — which dunder methods fix each?
- Why use `with` for a file or lock instead of a manual close/release? What does `__exit__` guarantee?
- What do type hints buy you, and what do they pointedly *not* do at runtime?

**Ch 12 — The ritual**
- Give the four-step answer for any concept on demand.
- Narrate URL→page in 90 seconds.
- Define ACID with an example in under 20 seconds.

**Ch 13 — Working with the data teams** *(bonus, not a pop-quiz topic)*
- What does a Data Engineer own versus a Data Analyst versus a Data Scientist?
- A stakeholder-facing metric needs to be correct and trusted over time — do you write the SQL yourself or hand it off, and to whom?
- Your app is about to emit a new event — who do you tell, and before what?

---

## Theory you can name and move on

These sit *below* the day-job layer — the CS-degree topics a working engineer rarely touches but should be able to *name* without a flicker of FOMO. The goal here is one honest paragraph each: what it is, and why recognizing it is usually enough. Depth is optional; recognition is not.

**Theory of Computation.** The math of what computers *can* and *can't* do, regardless of speed. It builds a ladder of idealized machines — finite automata (think regex engines), pushdown automata (matching brackets), and the **Turing machine** (the abstract model of "a computer") — and proves some problems are simply **undecidable**: no program can ever solve them for all inputs, the **halting problem** (can you tell if an arbitrary program loops forever?) being the famous one. Why you can move on: you'll basically never *use* this, but knowing "some problems are provably unsolvable, and the halting problem is the canonical example" is the entire interview-relevant takeaway.

**Compilers.** How human-readable source code becomes something a machine runs. The pipeline is worth recognizing: **lexing** (text → tokens), **parsing** (tokens → a tree that captures structure), then **code generation** and **optimization** passes that emit and improve the machine/byte code. Why you can move on: unless you build a language, DSL, or developer tooling, you *consume* compilers rather than write them — but the lex → parse → generate shape shows up anywhere you process structured text (config parsers, query engines, even the SQL planner in Chapter 3), so the vocabulary pays off.

**Discrete Mathematics.** The math of distinct, countable things — the actual foundation under everything else in this list: **logic and proofs** (including induction), **set theory**, **combinatorics** (counting arrangements), and **graph theory** (the formal study of nodes and edges). Why you can move on: you already *use* its fruits — Big-O reasoning, graph algorithms (DSA track), relational set operations (SQL) — so you rarely need the formal proofs themselves. Recognize that "discrete math" is the rigorous bedrock and you can reach for the specific piece when a problem demands it.

**Complexity theory (P vs NP).** A classification of problems by how hard they are to *solve* versus *check*. **P** is problems solvable quickly (polynomial time); **NP** is problems whose answer can be *verified* quickly even if finding it seems slow. **NP-hard** means "at least as hard as the hardest problems in NP"; **NP-complete** problems (like the travelling-salesman decision problem or SAT) are the bridge — in NP *and* NP-hard. Whether **P = NP** (is every quickly-checkable problem also quickly-solvable?) is the famous open question. Why you can move on: you won't write proofs, but recognizing "this smells NP-hard, so I should reach for an approximation or heuristic instead of an exact algorithm" is a genuinely useful senior instinct.

**Cryptography foundations.** The math that makes TLS and password hashing (Chapters 7–8) actually work. Underneath sits **number theory** — modular arithmetic, prime factorization, and the fact that some operations are easy one way but infeasible to reverse (the basis of **RSA** and other **asymmetric** "public/private key" schemes). Why you can move on: the cardinal rule is **never roll your own crypto** — you use vetted libraries and protocols, not hand-built primitives. Knowing "public-key crypto relies on hard number-theory problems, and I should always use a standard library" is the practitioner-level takeaway; the proofs belong to specialists.

**Computer organization / architecture.** What's physically happening one level below your code. The CPU runs a **fetch-decode-execute** cycle over machine instructions, using tiny ultra-fast **registers**, backed by a **cache hierarchy** (L1/L2/L3) that sits between the CPU and slow main memory — which is *why* cache-friendly, sequential memory access can be dramatically faster than random access. Why you can move on: high-level code hides almost all of it, but the one idea that escapes into daily work is the **memory hierarchy** — it explains cache-friendly data layouts, why locality matters, and connects straight back to the caching theme that runs through this whole track.

---

## The five bumper stickers

1. **SQL:** *Describe the result and the database finds the path; master the joins and remember the query runs in a different order than you write it.*
2. **Databases:** *An index is the book's back-index — logarithmic lookups at the cost of slower writes; ACID is why we trust databases with money.*
3. **OS:** *A thread shares memory with its siblings — that sharing is the whole reason concurrency is hard; lock the smallest section and always in the same order.*
4. **Networking:** *Envelopes inside envelopes — HTTP in TLS in TCP in IP; and naming each handoff from URL to page proves you see the whole machine.*
5. **The habit:** *Every pop-quiz question asks whether you know what's happening one level below where you normally code. Feel the mechanism, answer in four beats with the tradeoff, and no quiz can catch you out.*
