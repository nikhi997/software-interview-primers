# Foundations 60-second recall

*[Contents](foundations-README.md)*

The chapters teach, the appendix helps you look up, and the mechanism maps show causality. This companion trains the last mile: spoken delivery. Each card uses the DART ritual from [Chapter 12](4-putting-it-together/ch12-ritual.md), but timed so you can rehearse it out loud.

The shape is always:

- **0–10s — Definition:** one crisp sentence.
- **10–30s — Mechanism:** the ordered flow underneath.
- **30–45s — Tradeoff or failure mode:** what it buys, costs, or breaks.
- **45–60s — Concrete choice:** a small example of what you would do.

Do not memorize these word-for-word. Rehearse the beats until your own version lands in under a minute.

---

## SQL and databases

### Prompt: "What's the logical execution order of a SQL query?"

**0–10s — Definition:** SQL is written in a human-friendly order, but logically evaluated in a different order.

**10–30s — Mechanism:** Start with `FROM` and `JOIN` to assemble rows, then `WHERE` filters rows, `GROUP BY` forms groups, `HAVING` filters groups, `SELECT` computes output columns, `ORDER BY` sorts, and `LIMIT` trims.

**30–45s — Failure mode:** This explains why aggregates cannot go in `WHERE`, and why a `SELECT` alias often is not visible to `WHERE`.

**45–60s — Concrete choice:** If I need "customers with total spend over $1000," I filter completed orders in `WHERE`, group by customer, then put `SUM(total) > 1000` in `HAVING`.

### Prompt: "How would you debug a slow database query?"

**0–10s — Definition:** I would look for the physical path the database chose, not just stare at the SQL text.

**10–30s — Mechanism:** Run `EXPLAIN` or `EXPLAIN ANALYZE`, find whether the planner is scanning the whole table or using an index, then compare that plan to the columns filtered, joined, and sorted.

**30–45s — Tradeoff:** A missing index can turn a lookup into a full scan, but indexes are not free because every write must maintain them.

**45–60s — Concrete choice:** For `WHERE customer_id = ? ORDER BY created_at`, I would consider a composite index on `(customer_id, created_at)` if that access pattern is common.

### Prompt: "Explain transactions and isolation levels."

**0–10s — Definition:** A transaction is an all-or-nothing group of database operations, and isolation controls how overlapping transactions see each other.

**10–30s — Mechanism:** You `BEGIN`, make several changes, then `COMMIT` them together or `ROLLBACK` them all. Isolation levels go from weaker to stronger: Read Uncommitted, Read Committed, Repeatable Read, Serializable.

**30–45s — Tradeoff:** Stronger isolation prevents more anomalies, like dirty reads or phantom reads, but reduces concurrency because the database must coordinate more.

**45–60s — Concrete choice:** For a last-ticket purchase, I care more about correctness than raw concurrency, so I would use a transaction and the locking or isolation needed to let only one buyer win.

### Prompt: "Normalize, denormalize, embed, or reference?"

**0–10s — Definition:** Data modeling starts from the access pattern: what is read together, what changes together, and what must stay consistent.

**10–30s — Mechanism:** If facts are shared and relational, normalize and reference them by keys. If a child is owned by a parent and always read with it, embedding or denormalizing can make the read one hop.

**30–45s — Tradeoff:** Normalization protects writes from duplicated facts; denormalization and embedding speed hot reads but risk drift, harder updates, and unbounded growth.

**45–60s — Concrete choice:** I would embed a product's small fixed set of variants, but reference an ever-growing event stream in its own table or collection.

---

## Operating systems

### Prompt: "Process vs thread?"

**0–10s — Definition:** A process is a running program with isolated memory; a thread is an execution path inside a process.

**10–30s — Mechanism:** Processes communicate through explicit IPC. Threads in the same process share memory, so they can communicate cheaply by reading the same objects.

**30–45s — Failure mode:** That shared memory is where races come from: two threads can interleave reads and writes in an order you did not predict.

**45–60s — Concrete choice:** I use processes when I need isolation or true CPU parallelism, and threads when shared state is manageable or the work is mostly waiting.

### Prompt: "What is a race condition, and how do locks help?"

**0–10s — Definition:** A race condition is a bug where the result depends on the timing of concurrent operations.

**10–30s — Mechanism:** A line like `counter += 1` really reads, computes, then writes. If two threads interleave those steps, both can read the same old value and one update disappears.

**30–45s — Tradeoff:** A lock makes the critical section one-at-a-time, which fixes the race, but too much locking serializes the program.

**45–60s — Concrete choice:** I would protect the smallest shared update with one mutex, then keep non-shared work outside the lock.

### Prompt: "What is deadlock?"

**0–10s — Definition:** Deadlock is when threads wait on each other's resources forever.

**10–30s — Mechanism:** Thread A holds lock 1 and waits for lock 2; thread B holds lock 2 and waits for lock 1. Neither reaches the release step.

**30–45s — Failure mode:** The program does not crash; it just hangs. The practical prevention is to break circular wait, usually with a consistent lock ordering.

**45–60s — Concrete choice:** If code sometimes needs both account locks, I would always acquire the lower account id first, then the higher one.

### Prompt: "Stack, heap, GC, and memory leaks?"

**0–10s — Definition:** The stack holds call frames; the heap holds longer-lived objects; GC frees heap objects that are no longer reachable.

**10–30s — Mechanism:** A function call pushes a frame. Locals may point to heap objects. When frames pop, GC traces from live roots into the heap and collects anything it cannot reach.

**30–45s — Failure mode:** A GC language can still leak if a cache, global list, or listener keeps a reference to data the program no longer needs.

**45–60s — Concrete choice:** If server memory climbs all day, I would look for retained references: unbounded caches, subscriptions not removed, or queues never drained.

---

## Networking

### Prompt: "What happens when you type a URL and press Enter?"

**0–10s — Definition:** A page load is an ordered relay from browser to network to edge to app to data store and back.

**10–30s — Mechanism:** The browser parses the URL, resolves DNS, opens TCP, performs TLS for HTTPS, sends HTTP, hits CDN or load balancer, reaches the app, checks auth, cache, and database, then returns a response.

**30–45s — Failure mode:** Any hop can dominate latency: DNS cache miss, handshake cost, cold CDN, overloaded app, cache miss, or missing DB index.

**45–60s — Concrete choice:** In a slow product page, I would ask where time is spent before guessing: edge timing, app timing, cache hit rate, and DB plan.

### Prompt: "TCP vs UDP, and where does TLS fit?"

**0–10s — Definition:** TCP is reliable ordered transport; UDP is fast connectionless transport; TLS secures traffic above transport.

**10–30s — Mechanism:** TCP handshakes, tracks byte order, retransmits loss, and gives HTTP a reliable stream. UDP sends datagrams without setup or delivery guarantees. TLS happens after TCP for HTTPS and establishes encrypted communication.

**30–45s — Tradeoff:** TCP's reliability costs setup and overhead. UDP is lower latency but the application must tolerate or handle loss. TLS adds security and setup work.

**45–60s — Concrete choice:** I use TCP/TLS for APIs and payments, and UDP for cases like live voice where a late packet is less useful than a dropped one.

### Prompt: "How does HTTP stay logged in if it is stateless?"

**0–10s — Definition:** HTTP does not remember clients by itself, so identity has to ride along with each request.

**10–30s — Mechanism:** After login, the server gives the browser a cookie or token. The browser sends it on later requests, and the app maps it to a session or verifies the token.

**30–45s — Failure mode:** Authentication says who the user is; authorization still has to check whether this user may do this action. Skipping that check creates broken access control.

**45–60s — Concrete choice:** For "delete order 42," I would verify the token, then check that order 42 belongs to this user or that the user has an admin role.

---

## Concurrency

### Prompt: "I/O-bound vs CPU-bound?"

**0–10s — Definition:** I/O-bound work waits on external systems; CPU-bound work spends time computing.

**10–30s — Mechanism:** Waiting can be overlapped with async or threads because the CPU can run something else. Computing needs actual cores doing work at the same time.

**30–45s — Failure mode:** Async does not speed up a tight CPU loop; it blocks the event loop. Python threads do not speed CPU-bound bytecode because of the GIL.

**45–60s — Concrete choice:** For many slow DB calls, I consider async or a thread pool. For image resizing in Python, I use multiprocessing or native code that releases the GIL.

### Prompt: "What does await do?"

**0–10s — Definition:** `await` is a yield point in an async function.

**10–30s — Mechanism:** The task starts an I/O operation, suspends itself, gives control back to the event loop, lets another ready task run, then resumes when the awaited result is ready.

**30–45s — Tradeoff:** This gives high concurrency on one thread when tasks wait often, but one long CPU computation can freeze every task on the loop.

**45–60s — Concrete choice:** I would use `await` around network or database calls, not around a million-iteration pure-Python calculation.

### Prompt: "What is the Python GIL?"

**0–10s — Definition:** In CPython, the Global Interpreter Lock allows only one thread to execute Python bytecode at a time.

**10–30s — Mechanism:** Threads can still be scheduled, and I/O waits can release the GIL, but compute-heavy Python threads take turns instead of running bytecode on multiple cores simultaneously.

**30–45s — Tradeoff:** Threads remain useful for I/O-bound work; they are the wrong expectation for CPU-bound speedups.

**45–60s — Concrete choice:** For CPU-heavy Python, I reach for multiprocessing, a process pool, or a native library that does the heavy work outside the GIL.

---

## Python

### Prompt: "Comprehension or generator?"

**0–10s — Definition:** A comprehension eagerly builds a collection; a generator produces values lazily.

**10–30s — Mechanism:** A list comprehension walks the iterable now and stores every result. A generator expression or `yield` returns one value, pauses with state preserved, and resumes when the next value is requested.

**30–45s — Tradeoff:** Eager lists are reusable and indexable but cost memory. Generators keep memory flat but are single-use and cannot be indexed or measured with `len`.

**45–60s — Concrete choice:** For a million log lines I would stream with a generator; for a small transformed list I need to reuse, I would use a comprehension.

### Prompt: "Why does `[[0] * cols] * rows` break?"

**0–10s — Definition:** It creates multiple references to the same inner list, not multiple independent rows.

**10–30s — Mechanism:** The inner list is built once. Multiplying the outer list repeats that same reference. Mutating one row mutates the one object every row points at.

**30–45s — Failure mode:** Your grid looks rectangular until the first write, then one cell change appears in every row.

**45–60s — Concrete choice:** I initialize with `[[0] * cols for _ in range(rows)]` because the inner list is created fresh on each iteration.

### Prompt: "What does dataclass buy you?"

**0–10s — Definition:** A dataclass is for classes that are mostly named fields.

**10–30s — Mechanism:** You declare fields once with type hints, and Python generates the constructor, useful representation, and value equality. With `frozen=True`, instances become immutable value objects.

**30–45s — Tradeoff:** It removes boilerplate and reduces missing-field bugs, but it is not a replacement for a class with serious behavior or invariants that need custom construction.

**45–60s — Concrete choice:** I would use a dataclass for a `Point`, `Money`, or parsed config record instead of passing anonymous tuples around.

### Prompt: "What are dunder methods?"

**0–10s — Definition:** Dunder methods are Python's hooks from syntax to your object's behavior.

**10–30s — Mechanism:** `repr(obj)` calls `__repr__`, `obj == other` calls `__eq__`, sorting uses comparison methods like `__lt__`, indexing uses `__getitem__`, and `with` uses `__enter__` and `__exit__`.

**30–45s — Failure mode:** Without the right hook, your object prints uselessly, compares by identity, refuses to sort, or cannot participate in normal Python idioms.

**45–60s — Concrete choice:** For a `Money` class, I would define `__repr__`, `__eq__`, and arithmetic or ordering methods only where the domain meaning is clear.

### Prompt: "Why use a context manager?"

**0–10s — Definition:** A context manager wraps acquire-use-release so cleanup is guaranteed.

**10–30s — Mechanism:** `with` calls `__enter__`, runs the block, then calls `__exit__` on normal exit or on exception.

**30–45s — Failure mode:** Manual cleanup at the bottom of a function is skipped if an exception jumps over it; `__exit__` is the structured cleanup path.

**45–60s — Concrete choice:** I use `with` for files, locks, database sessions, and network connections because those resources must be released even when work fails.

---

## Git

### Prompt: "What is a commit, branch, and HEAD?"

**0–10s — Definition:** A commit is a snapshot plus parent pointer; a branch is a movable pointer to a commit; HEAD is where you are now.

**10–30s — Mechanism:** Each commit records tracked file content and parent metadata, producing a hash. Making a commit advances the current branch pointer. HEAD usually points to that branch.

**30–45s — Failure mode:** If HEAD points directly at a commit, you are detached; new work can be lost from branch history unless you create a branch to hold it.

**45–60s — Concrete choice:** When Git feels confusing, I ask: what commit does my branch point to, and what does HEAD point to?

### Prompt: "Working directory, staging area, repository?"

**0–10s — Definition:** Git has three places for changes: edited files, staged changes, and committed history.

**10–30s — Mechanism:** You edit in the working directory, `git add` copies selected changes into the staging area, and `git commit` records the staged snapshot into the repository graph.

**30–45s — Tradeoff:** Staging is extra ceremony, but it lets you split unrelated edits into clean commits instead of dumping everything together.

**45–60s — Concrete choice:** If I fix a bug and reformat a nearby file, I stage only the bug lines for the first commit and leave formatting for another.

### Prompt: "Merge vs rebase?"

**0–10s — Definition:** Merge combines histories with a two-parent commit; rebase replays commits onto a new base.

**10–30s — Mechanism:** Merge preserves the original commits and adds a node tying both parents together. Rebase recreates each feature commit with a new parent, so each replayed commit gets a new hash.

**30–45s — Tradeoff:** Merge keeps public history honest but non-linear. Rebase makes local history linear but rewrites it.

**45–60s — Concrete choice:** I rebase my local unpushed branch to tidy it, but I avoid rebasing commits teammates may already have pulled.

### Prompt: "How do you undo a bad commit?"

**0–10s — Definition:** The safe undo depends on whether the commit is public or only local.

**10–30s — Mechanism:** `revert` adds a new commit that undoes an older commit. `reset` moves a branch pointer backward. `amend` replaces the last commit with a new one.

**30–45s — Failure mode:** Reset and amend rewrite history; if others have the old commit, your graph now disagrees with theirs.

**45–60s — Concrete choice:** For a pushed production bug, I use `git revert` because it is additive. For an unpushed typo in my last commit, I amend.

### Prompt: "What is a merge conflict?"

**0–10s — Definition:** A merge conflict is Git refusing to guess between incompatible edits.

**10–30s — Mechanism:** Git finds a common ancestor, compares both sides, and can auto-merge non-overlapping changes. If both sides changed the same region, it marks the conflict.

**30–45s — Failure mode:** The danger is not the markers; it is choosing a result that compiles but loses one side's intent.

**45–60s — Concrete choice:** I read both versions, write the intended combined result, remove markers, run the relevant checks, then continue the merge or rebase.

---

## How to drill

1. Pick five prompts, one per weak area.
2. Start a timer and answer each aloud.
3. If you run long, cut detail from the mechanism before cutting the tradeoff.
4. If you sound vague, go back to [mechanism maps](foundations-mechanism-maps.md) and rehearse the arrows.
5. Finish with the appendix question bank in [the cheat-sheet kit](foundations-appendix.md).

---

<div align="right">

[Appendix →](foundations-appendix.md)

</div>
