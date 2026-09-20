# Foundations mechanism maps

*[Contents](foundations-README.md)*

The chapters teach the concepts, and the appendix helps you look them up. This companion sits between them: it shows the causal chain. Use it when you can name a term but cannot yet explain what moves, waits, locks, scans, or rewrites underneath it.

These are deliberately independent maps, not one forced story. SQL, OS, networking, Python, and Git fail in different ways; keep their mechanisms separate in your head.

---

## SQL: the query path

Read with [Chapter 1](1-sql-and-databases/sql/ch1-sql.md), [Chapter 2](1-sql-and-databases/sql/ch2-sql.md), and [Chapter 3](1-sql-and-databases/sql/ch3-sql.md).

```text
query text
  |
  v
logical clause order
  FROM / JOIN
    -> WHERE
    -> GROUP BY
    -> HAVING
    -> SELECT
    -> ORDER BY
    -> LIMIT
  |
  v
planner chooses a physical path
  |
  +--> no useful index
  |      -> scan table / joined rows
  |      -> filter each candidate
  |      -> slow when the table is large
  |
  +--> useful index
         -> walk sorted structure
         -> jump to matching rows
         -> fast reads, especially equality/range filters
  |
  v
result rows
```

The failure this explains: a query can be syntactically correct and still crawl because the planner has no cheap path to the rows. The interview move is not "add indexes everywhere"; it is "read the plan, find the scan, add the index that matches the access pattern."

```text
INSERT / UPDATE / DELETE
  |
  v
change table row
  |
  v
also maintain every affected index
  |
  v
write gets slower as indexes pile up
```

That is the index tradeoff in one line: you buy faster reads by paying extra work on writes and disk.

```text
BEGIN transaction
  |
  v
operation A + operation B + ...
  |
  +--> one operation fails
  |      -> ROLLBACK
  |      -> no half-finished state
  |
  +--> all operations succeed
         -> COMMIT
         -> durable state
  |
  v
isolation level controls what overlapping transactions can see
  Read Uncommitted
    -> Read Committed
    -> Repeatable Read
    -> Serializable
  |
  v
stronger isolation prevents more anomalies, but allows less concurrency
```

The failure this explains: two correct operations can be wrong together if isolation is too weak for the invariant you need.

---

## Databases: model from the access pattern

Read with [Chapter 3](1-sql-and-databases/sql/ch3-sql.md) and [Chapter 4](1-sql-and-databases/sql/ch4-sql.md).

```text
access pattern
  "what do we read together?"
  "what changes together?"
  "what must stay correct together?"
  |
  v
data shape choice
  |
  +--> facts are relational / shared / transactional
  |      -> normalize
  |      -> reference by keys
  |      -> joins assemble the view
  |      -> fewer update anomalies
  |
  +--> data is hierarchical / owned / read as a unit
         -> embed or denormalize deliberately
         -> one read gets the whole aggregate
         -> writes and duplication get harder
         -> unbounded arrays become a growth failure
  |
  v
index and plan
  |
  +--> no matching index
  |      -> COLLSCAN / full table scan
  |      -> every document or row is inspected
  |
  +--> matching index
         -> IXSCAN / index scan
         -> sorted lookup narrows candidates first
  |
  v
consistency choice
  |
  +--> strict transaction across related facts
  |      -> safer invariants
  |      -> more coordination
  |
  +--> looser / eventual consistency
         -> easier scale and availability
         -> readers may briefly see stale or partial state
```

The failure this explains: schema design goes wrong when you start from a database brand instead of the read/write pattern. "SQL or document?" is usually "do these facts need joins and transactions, or are they one bounded aggregate?"

---

## OS: sharing creates the bug

Read with [Chapter 5](2-operating-systems/ch5-os.md) and [Chapter 6](2-operating-systems/ch6-os.md).

```text
process
  -> isolated memory
  -> safer failure boundary
  -> heavier communication through IPC

process
  |
  v
threads inside it
  -> shared heap and globals
  -> cheap communication
  |
  v
scheduler time-slices threads
  |
  v
context switch can happen between tiny steps
  |
  v
shared critical section
  read counter
    -> compute counter + 1
    -> write counter
  |
  v
race condition
  -> result depends on timing
  |
  v
lock / mutex
  -> one thread enters the critical section
  -> others wait
  |
  v
deadlock
  -> thread A holds lock 1 and waits for lock 2
  -> thread B holds lock 2 and waits for lock 1
  -> both wait forever
```

The tradeoff this explains: threads are attractive because sharing is cheap; threads are dangerous because sharing is cheap. Locks serialize the dangerous part, but lock ordering now matters.

```text
function call
  |
  v
call frame pushed on stack
  -> parameters
  -> local variables
  -> return address
  |
  v
local variable points to heap object
  |
  v
function returns
  -> frame pops
  -> stack memory is reclaimed automatically
  |
  v
GC reachability walk
  roots: stack variables, globals, live registers
  -> follow references into heap
  |
  +--> unreachable heap object
  |      -> collect it
  |
  +--> still reachable by an accidental reference
         -> keep it
         -> memory leak in a GC language
```

The failure this explains: garbage collection frees unreachable objects, not unwanted objects. A cache, listener list, or global reference can keep dead data alive forever.

---

## Networking: one request is a relay

Read with [Chapter 7](3-networking/ch7-networking.md) and [Chapter 8](3-networking/ch8-networking.md).

```text
URL
  |
  v
parse scheme / host / path
  |
  v
DNS lookup
  browser cache
    -> OS cache
    -> router / resolver cache
    -> recursive resolver if needed
  |
  v
IP address
  |
  v
TCP three-way handshake
  SYN -> SYN-ACK -> ACK
  |
  v
TLS handshake for HTTPS
  certificate
    -> key exchange
    -> shared symmetric key
  |
  v
HTTP request over encrypted TCP
  |
  v
CDN / edge cache
  |
  v
load balancer
  |
  v
application server
  -> route
  -> authenticate identity
  -> authorize this action
  -> validate input
  |
  v
cache
  |
  +--> hit
  |      -> skip database
  |
  +--> miss
         -> indexed database lookup
         -> populate cache
  |
  v
HTTP response
  |
  v
browser parses HTML
  -> fetches CSS / JS / images
  -> renders page
```

The failure this explains: "the website is slow" is not one problem. It could be DNS, handshake latency, a cold CDN, an overloaded app server, a missing database index, a cache miss storm, or expensive rendering. The ordered path tells you where to look.

---

## Concurrency: waiting is not working

Read with [Chapter 9](4-putting-it-together/ch9-concurrency.md).

```text
classify the work
  |
  +--> I/O-bound
  |      -> mostly waiting on DB / network / disk
  |      |
  |      +--> async / event loop
  |      |      await slow_call()
  |      |        -> yield control
  |      |        -> run another ready task
  |      |        -> I/O completes
  |      |        -> resume after await
  |      |
  |      +--> thread pool
  |             -> blocking calls run on reusable workers
  |             -> OS runs another thread while one waits
  |
  +--> CPU-bound
         -> mostly computing
         -> needs real parallel execution across cores
         -> use multiprocessing / separate processes in Python
```

```text
CPython threads
  |
  v
Global Interpreter Lock
  -> only one thread executes Python bytecode at a time
  |
  +--> I/O-bound thread waits
  |      -> GIL can be released
  |      -> another thread can run
  |
  +--> CPU-bound thread computes
         -> threads take turns under the GIL
         -> no multi-core speedup for Python bytecode
```

The tradeoff this explains: async and threads overlap waiting; they do not make one CPU do two computations at once. In CPython, CPU-bound parallelism means processes unless native extensions release the GIL.

---

## Python: idioms are small mechanisms

Read with [Chapter 10](4-putting-it-together/ch10-python.md) and [Chapter 11](4-putting-it-together/ch11-python-objects.md).

```text
iterable
  |
  +--> list comprehension
  |      -> evaluate every item now
  |      -> build a full list in memory
  |      -> good when you need the collection
  |
  +--> generator expression / yield
         -> produce one item when asked
         -> pause with local state preserved
         -> resume on next()
         -> constant memory
         -> single-use, no indexing or len
```

The tradeoff this explains: comprehensions buy clarity for small eager transforms; generators buy flat memory when the data is large or streamed.

```text
grid = [[0] * cols] * rows
  |
  v
outer list stores the same inner list reference many times
  |
  v
mutate grid[0][0]
  |
  v
every "row" changes
```

```text
grid = [[0] * cols for _ in range(rows)]
  |
  v
comprehension runs the inner expression again each row
  |
  v
each row is a different list
```

The failure this explains: the bug is not multiplication; it is aliasing. You copied a reference, not the row.

```text
class with mostly fields
  |
  v
@dataclass
  |
  v
declared fields
  -> generated __init__
  -> generated __repr__
  -> generated __eq__
  -> optional frozen value object
```

```text
Python syntax
  |
  +--> print(obj) / repr(obj)
  |      -> __str__ / __repr__
  |
  +--> obj == other
  |      -> __eq__
  |
  +--> sorted(items)
  |      -> __lt__
  |
  +--> len(obj), obj[i], for item in obj
         -> __len__, __getitem__, __iter__
```

The mechanism this explains: dunder methods are dispatch hooks. Your object feels built in when the syntax has a method to call.

```text
with resource as name:
  |
  v
__enter__()
  -> acquire file / lock / connection
  |
  v
use resource
  |
  +--> normal exit
  |      -> __exit__()
  |      -> release
  |
  +--> exception raised
         -> __exit__ still runs
         -> release
         -> exception is re-raised unless suppressed
```

The failure this explains: cleanup at the end of a block is not enough; cleanup must run on the exceptional path too.

---

## Git: commands move pointers or add graph nodes

Read with [Chapter 14](5-bonus/ch14-git.md).

```text
edit file
  |
  v
working directory
  |
  v
git add
  |
  v
staging area / index
  |
  v
git commit
  |
  v
new commit in repository
```

```text
commit
  -> snapshot of tracked files
  -> parent pointer
  -> content-derived hash
  |
  v
branch
  -> movable pointer to a commit
  |
  v
HEAD
  -> where you are now
  -> usually points to a branch
  -> detached HEAD points directly to a commit
```

The mechanism this explains: a branch is cheap because it is not a copy of the project. It is one pointer into the commit graph.

```text
shared base
  |
  +--> main adds commits
  |
  +--> feature adds commits
```

```text
merge
  -> create one new commit
  -> new commit has two parents
  -> original commit hashes stay the same
  -> history records the fork
```

```text
rebase
  -> replay feature commits on top of new base
  -> each replayed commit has a different parent
  -> each replayed commit gets a new hash
  -> history is linear, but rewritten
```

The tradeoff this explains: merge preserves public history; rebase cleans local history by recreating commits. Rebase pushed commits only if you are deliberately coordinating a history rewrite.

```text
bad public commit
  |
  v
git revert
  -> add a new commit that undoes it
  -> shared history remains coherent
```

```text
bad local commit
  |
  +--> git commit --amend
  |      -> replace the last commit with a new hash
  |
  +--> git reset
         -> move branch pointer backward
         -> choose whether changes stay staged, unstaged, or discarded
```

The failure this explains: undoing is safe when it adds history and risky when it rewrites history. Ask "has anyone else seen this commit?" before choosing the command.

---

## How to use this page

1. Pick the map for the domain you are drilling.
2. Cover the explanation under it.
3. Say the arrows aloud until the failure mode at the end feels inevitable.
4. Then move to [60-second recall](foundations-60-second-recall.md) and turn the same mechanism into a spoken answer.

---

<div align="right">

[60-second recall →](foundations-60-second-recall.md)

</div>
