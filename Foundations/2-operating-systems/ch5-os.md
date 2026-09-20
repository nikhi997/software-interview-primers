# Chapter 5: Processes, threads, and the trouble with sharing

*[← Chapter 4](../1-sql-and-databases/sql/ch4-sql.md) · [Contents](../foundations-README.md)*

- [ ] **Mark as read**

We drop down a layer now — to the operating system. Even if you never write OS code, the OS is the stage your program runs on, and interviewers probe it because *concurrency bugs* live here: the race conditions, deadlocks, and "works on my machine" mysteries that plague real systems. The mechanism to feel: your program isn't alone, and the moment two things run at once and touch the same data, you need to understand what the OS is actually doing underneath.

---

## Process vs thread: the foundational distinction

This is one of the most-asked OS interview questions, full stop. Know it cold.

> 💡 **Concept notes — process**
> A **process** is a running program with its *own* isolated memory space. When you launch your app, the OS creates a process and hands it its own chunk of memory, file handles, and resources. Two processes can't directly read each other's memory — that isolation is a safety feature (one crashing process doesn't corrupt another). They communicate only through deliberate channels (**IPC** — inter-process communication: pipes, sockets, shared memory).

> 💡 **Concept notes — thread**
> A **thread** is a unit of execution *within* a process. A process can have many threads, and crucially they **share the same memory.** That shared memory is what makes threads lightweight and fast to communicate (no IPC needed — they just read the same variables) — *and* what makes them dangerous (they can step on each other's data, as we'll see).
> The one-liner: **"a process is an isolated program with its own memory; a thread is a lighter unit of execution inside a process, and threads in the same process share memory."** That last clause — *threads share memory* — is the whole reason concurrency is hard.

---

## Context switching: the illusion of simultaneity

Your laptop runs hundreds of processes on a handful of CPU cores. How? The OS **time-slices** — it runs one thing briefly, pauses it, runs another, and cycles so fast it *looks* simultaneous.

> 💡 **Concept notes — context switch**
> A **context switch** is the OS saving the state (registers, program counter) of the currently running thread and loading another's, so a single core can juggle many threads. It's the mechanism behind multitasking — but it isn't free: each switch costs time (saving/restoring state, cache effects). This is why spawning *thousands* of threads can actually slow a program down — it spends its time switching instead of working. It also explains why you can't predict *exactly* when a thread will be paused — which is the root of the bugs below.

> 💡 **Concept notes — concurrency vs parallelism**
> Worth separating because interviewers do: **concurrency** is *dealing with* many things at once (structuring a program so tasks can make progress independently — possibly via time-slicing on one core). **Parallelism** is *doing* many things at the literal same instant (requires multiple cores). Concurrency is about structure; parallelism is about execution. You can have concurrency without parallelism (one core, time-sliced). Rob Pike's line: "concurrency is about dealing with lots of things at once; parallelism is about doing lots of things at once."

---

## The core danger: race conditions

Here's where shared memory bites. Suppose two threads both run `counter = counter + 1`. That innocent line is actually *three* steps: read `counter`, add 1, write it back. If the OS context-switches at the wrong moment, both threads read the same old value, both add 1, both write — and you've counted *one* increment instead of two. The result depends on *timing*, which you don't control.

> 💡 **Concept notes — race condition**
> A **race condition** is a bug where the outcome depends on the unpredictable *timing/interleaving* of concurrent threads. They're insidious because they're **non-deterministic** — the code might work 999 times and fail the 1000th, and fail differently each time, making them brutal to reproduce and debug. The region of code that touches shared data and must not be interrupted mid-way is called a **critical section.**

---

## The fix: locks (mutexes)

To prevent races, you ensure only one thread enters the critical section at a time — you make the operation **atomic** (indivisible, all-or-nothing — same word as in ACID, Chapter 3). The basic tool is a **lock.**

> 💡 **Concept notes — mutex / lock**
> A **mutex** ("mutual exclusion") is a lock a thread must *acquire* before entering a critical section and *release* when done. While one thread holds it, others trying to acquire it **wait** (block) until it's free. This serializes access to shared data, eliminating the race. Related primitives: a **semaphore** (a counter allowing up to N threads in at once, not just one). The cost of locking is reduced concurrency — threads wait — so you lock the *smallest* critical section you can. Locking too much serializes your whole program (killing the benefit of threads); locking too little leaves races. That balance is the art of concurrent programming.

---

## When locks go wrong: deadlock

Locks prevent races but introduce a new failure mode that's a guaranteed interview topic: **deadlock** — two threads waiting on each other forever.

> 💡 **Concept notes — deadlock**
> A **deadlock** is when two (or more) threads are each waiting for a lock the other holds, so neither can proceed — the program hangs permanently. The classic picture: Thread A holds lock 1 and wants lock 2; Thread B holds lock 2 and wants lock 1. Neither will release until it gets the other's lock. Stalemate.
> Deadlock requires **four conditions simultaneously** (Coffman conditions — worth knowing):
> 1. **Mutual exclusion** — a resource can be held by only one thread.
> 2. **Hold and wait** — a thread holds one resource while waiting for another.
> 3. **No preemption** — a resource can't be forcibly taken; it must be released voluntarily.
> 4. **Circular wait** — a cycle of threads each waiting for the next.
> Break *any one* and deadlock can't happen. The most practical fix is breaking **circular wait**: always acquire locks in a consistent global order (everyone grabs lock 1 before lock 2), so no cycle can form. "Acquire locks in a fixed order" is the answer to "how do you prevent deadlock."

---

## Try it

1. State the difference between a process and a thread in one sentence, and explain why the "threads share memory" part is what makes concurrency hard.
2. Walk through how two threads running `counter += 1` can lose an update. At which step does the context switch cause the problem?
3. What's a race condition, and why are they so hard to debug compared to ordinary bugs?
4. What does a mutex do, and what's the downside of holding locks for too large a section of code?
5. Describe a deadlock with the two-lock example, then name the four conditions required for one.
6. Your service occasionally hangs under load with no error. Two locks are involved. What do you suspect, and what's the simplest design rule that would prevent it?

*Write your answers in [ch5-os-tryit.md](../code/ch5-os-tryit.md).*

---

## The bumper sticker

> *A process is isolated memory; a thread shares memory with its siblings — and that sharing is the whole reason concurrency is hard. Race conditions come from unpredictable timing on shared data; locks fix them but risk deadlock, which you prevent by always acquiring locks in the same order.*

Next: the other half of OS fundamentals — how memory itself is organized into stack and heap, and where memory leaks come from.

---

<div align="right">

[Chapter 6 →](ch6-os.md)

</div>
