# Chapter 1: Java core

*[Contents](interview-topics-README.md)*

- [ ] **Mark as read**

When a JD says "Java," the screen that follows almost never asks you to write a clever algorithm in Java — it asks whether you understand the **language's machinery**: how a `HashMap` finds a bucket, what `volatile` actually guarantees, why two threads corrupt a counter. These are the questions that separate "I've written Java" from "I understand Java." This chapter is the recall layer for that screen.

The track principle lands immediately: **feel the concept beneath the brand name.** Java's collections are just hash tables and arrays; its concurrency is just the OS threads and locks from [Foundations Ch 5](../Foundations/2-operating-systems/ch5-os.md) with a language API on top. Know the mechanism and the Java-specific questions answer themselves.

---

## Collections: the everyday data structures, named in Java

The collections framework is the most-asked Java topic because you use it constantly and it exposes whether you know what's happening underneath.

> 💡 **Concept notes — the four you must know cold**
> - **`HashMap`** — an array of buckets. The key's `hashCode()` picks a bucket; collisions chain in a linked list, converting to a balanced tree past a threshold in modern Java. O(1) average get/put, O(n) worst (O(log n) once treeified).
> - **`ArrayList`** — a contiguous, resizable array. O(1) index access, O(n) insert/remove in the middle (everything shifts).
> - **`LinkedList`** — nodes with pointers. O(1) insert/remove at the ends, O(n) to index into the middle.
> - **`ConcurrentHashMap`** — the thread-safe map; use it instead of synchronizing a plain `HashMap` for concurrent access.
> Pick by access pattern: random access → `ArrayList`; lots of end-insertion → `LinkedList`; keyed lookup → `HashMap`.

Two of those — `HashMap` and its cousin `HashSet` — only work if your objects honour one contract.

> 💡 **Concept notes — the equals/hashCode contract**
> Hash-based collections find an object by computing its `hashCode()` to locate the bucket, then calling `equals()` to match within it. So the contract: **equal objects must return equal hash codes.** Override both together or neither — overriding `equals` without `hashCode` (or vice versa) silently corrupts `HashMap`/`HashSet` (you store a key and can't find it again). This is a classic interview gotcha.

---

## Concurrency: where Java interviews get sharp

This is the part of the Java screen that exposes depth. The concepts are the OS-level ones from [Foundations Ch 5](../Foundations/2-operating-systems/ch5-os.md); here they wear Java's API.

> 💡 **Concept notes — visibility vs atomicity**
> - **`volatile`** guarantees **visibility** — a write by one thread is seen by others (reads/writes go to main memory, not a per-thread cache). It does **not** make compound actions atomic. `count++` on a `volatile` is still a race: it's read-modify-write, three steps.
> - **`synchronized`** (and `Lock`) give **both** mutual exclusion and visibility for a block/method. Use it — or an atomic class (`AtomicInteger`) — for read-modify-write.
> - **Atomic classes** (`AtomicInteger`, `AtomicLong`) do lock-free atomic updates via compare-and-swap — the right tool for a simple shared counter.
> The one-line answer: *`volatile` for a simple flag, `synchronized`/atomics for anything you read-then-write.*

Once shared state is safe, the next question is how you actually run work off the main thread.

> 💡 **Concept notes — running async work**
> - **`Runnable`** returns nothing; **`Callable`** returns a value and can throw.
> - Submit either to an **`ExecutorService`** (a managed thread pool) rather than spawning raw threads. Submitting a `Callable` gives you a **`Future`** to get the result.
> - **`CompletableFuture`** composes async steps (`thenApply`, `thenCompose`) without blocking — the modern way to chain non-blocking work.
> Reach for `ExecutorService` + `Future` when you want a result back, `CompletableFuture` when you're chaining steps.

The moment threads share locks, you inherit the failure mode every concurrency screen circles back to.

> 💡 **Concept notes — deadlock, in one breath**
> A deadlock needs four conditions at once: mutual exclusion, hold-and-wait, no preemption, and circular wait. Break any one — most practically, impose a **global lock ordering** so every thread acquires locks in the same order, or use `tryLock` with a timeout. (The same four conditions from [Foundations Ch 5](../Foundations/2-operating-systems/ch5-os.md).)

---

## The JVM: just enough

You don't need GC internals, but you must not hand-wave the runtime.

> 💡 **Concept notes — heap, stack, GC**
> - **Stack** — per-thread; holds method frames and local variables/references. **Heap** — shared; holds all objects. (Same split as [Foundations Ch 6](../Foundations/2-operating-systems/ch6-os.md).)
> - **Garbage collection** reclaims heap objects no longer reachable from any live reference — so you don't `free()` manually.
> - A **memory leak** in a managed language is a *lingering reference*: an object you're done with but a long-lived structure (a static `List`, a cache, an unremoved listener) still points at, so GC can't collect it.
> So the honest answer to “do you manage memory in Java?” is: no — but you can still leak by holding references you forgot to drop.

---

## Language fundamentals: the warm-up questions

Before the hard concurrency questions, the screen checks you know the basics every Java dev hits daily. Miss these and the interview ends early.

> 💡 **Concept notes — the must-not-fumble basics**
> - **`String` is immutable** — every "change" makes a new object; that's why the pool can share literals and why heavy concatenation in a loop wants `StringBuilder`. `==` compares references, **`equals` compares contents** — always use `equals` for Strings.
> - **Checked vs unchecked** — checked exceptions (`extends Exception`) must be declared/caught; unchecked (`extends RuntimeException`) needn't. Don't swallow exceptions silently.
> - **Generics + type erasure** — generics are compile-time only; the runtime erases `List<String>` to `List`. So you can't do `new T[]` or check `instanceof List<String>` — a favourite trap.
> - **`final` / `static`** — `final` = can't reassign (not deep-immutable); `static` = belongs to
6. Why is `String` immutable, and what's the difference between `==` and `equals`?
7. Rewrite "sum the ages of users over 18" as a stream — name the intermediate and terminal ops. Checked vs unchecked exceptions: which rolls back, which must you declare?the class, not the instance.
> - **`Optional`** — a typed "maybe-null" to avoid NPEs; return it, don't shove it in fields. **Records** (Java 16+) are immutable data carriers with generated `equals`/`hashCode`/`toString`.

---

## Streams and lambdas: the modern Java fluency check

Any Java role written after Java 8 expects you to think in streams. "Rewrite this loop as a stream" is one of the most common live exercises.

> 💡 **Concept notes — streams in one breath**
> A **lambda** is an inline function; it implements a **functional interface** (one abstract method — `Function`, `Predicate`, `Supplier`, `Consumer`). A **stream** is a pipeline: a source → intermediate ops (`map`, `filter`, `sorted` — **lazy**) → a terminal op (`collect`, `count`, `reduce` — triggers execution). Favourite collectors: `toList()`, `groupingBy`, `joining`. **Streams don't mutate** the source; they produce a new result. Use them for readable transforms — keep ordinary loops where they're clearer or you need to break early.

---

## Try it

Answer aloud, as if to an interviewer:

1. Walk through what happens inside a `HashMap` when you call `put(key, value)` — bucket, collision, treeify. What's the average and worst-case complexity, and why must `equals` and `hashCode` agree?
2. Does `volatile` make `count++` thread-safe? Explain exactly why or why not, and what you'd use instead.
3. Name the four conditions for deadlock and the single most practical way to prevent it.
4. `Runnable` vs `Callable`, and how do you run a task asynchronously and get its result?
5. What is a memory leak in Java, given that there's a garbage collector? Give a concrete example.

*Write your answers in [interview-topics-chapter-1-tryit.md](code/interview-topics-chapter-1-tryit.md).*

## The bumper sticker

> *The Java screen isn't testing Java trivia — it's testing whether you know the data structures and OS concurrency underneath the API. `HashMap` is a hash table, `volatile` is visibility-not-atomicity, a deadlock is the same four conditions everywhere. Name the mechanism and the Java question answers itself.*

Next: the framework that sits on top of Java in almost every backend JD — **Spring Boot**, where dependency injection is the concept beneath the brand.

---

<div align="right">

[Chapter 2 →](interview-topics-chapter-2.md)

</div>
