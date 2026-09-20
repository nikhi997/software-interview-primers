# Chapter 9: Async, event loops, and the question that decides everything

*[← Chapter 8](../3-networking/ch8-networking.md) · [Contents](../foundations-README.md)*

- [ ] **Mark as read**

Modern backends are full of `async`, `await`, event loops, and thread pools — and most developers cargo-cult them without knowing *why* one task should be async and another threaded. There's a single distinction underneath that decides it all: **is your work I/O-bound or CPU-bound?** Get that, and the whole concurrency toolbox snaps into place. This is the last content chapter; it builds directly on the OS concepts from Chapter 5. The mechanism to feel: waiting is not the same as working, and the right concurrency tool depends entirely on which one you're doing.

---

## The distinction that organizes everything: I/O-bound vs CPU-bound

Before any tool, ask: what is the task spending its time on?

> 💡 **Concept notes — I/O-bound vs CPU-bound**
> - **I/O-bound:** the task spends most of its time *waiting* — for the network, the disk, the database, an API. The CPU is idle, twiddling its thumbs, waiting for data to come back. Most web backends are I/O-bound: a request mostly waits on the database and other services.
> - **CPU-bound:** the task spends most of its time *computing* — crunching numbers, processing images, parsing huge files. The CPU is pegged at 100%, doing real work the whole time.
> This single question determines your strategy: **for I/O-bound work, you want concurrency that lets you do other things *while waiting* (async / threads). For CPU-bound work, waiting isn't the problem — you need *more cores actually computing* (parallelism / multiple processes).** Using the wrong tool — async for CPU-bound, or spawning threads for pure computation in a language with a GIL — is a classic mistake interviewers probe for.

---

## Async / await and the event loop

For I/O-bound work, the elegant solution is **asynchronous** programming: instead of blocking a whole thread while waiting, you *register interest* in the result and let the thread go do other work until the data is ready.

> 💡 **Concept notes — the event loop**
> An **event loop** is a single thread that juggles many tasks by never waiting idly. When a task hits an I/O operation (a database call), instead of blocking, it says "wake me when this finishes" and hands control back to the loop, which immediately runs *another* ready task. When the I/O completes, the loop resumes the first task where it left off. So one thread handles thousands of concurrent connections — because at any instant, almost all of them are just *waiting*, and waiting is free. This is how Node.js, Python's `asyncio`, and nginx achieve massive concurrency on few threads.

> 💡 **Concept notes — async / await**
> **`async`** marks a function as asynchronous; **`await`** marks the points where it's waiting on something (an I/O operation) and is willing to *yield* control back to the event loop. `await some_db_call()` means "pause me here, run other tasks, resume me when the database responds." The crucial insight: async gives you **concurrency on a single thread** — it's *not* parallelism, and it does *nothing* for CPU-bound work (there's no waiting to overlap; a long computation just blocks the whole event loop, freezing every other task). Async shines precisely when there's lots of *waiting* to overlap — i.e., I/O-bound work.

---

## Threads and thread pools

The older approach to concurrency (Chapter 5) is **threads**: run multiple threads, and the OS time-slices them. For I/O-bound work this also works — while one thread blocks on I/O, the OS runs another.

> 💡 **Concept notes — thread pool**
> Spawning a fresh thread per task is wasteful (threads cost memory, and context switching adds up — Chapter 5). A **thread pool** is a fixed set of reusable worker threads fed by a queue of tasks: a worker grabs a task, runs it, then grabs the next. This caps resource use and avoids constant create/destroy overhead. Thread pools are the standard way to add concurrency for I/O-bound (or blocking) work in thread-based languages like Java. Async event loops and thread pools are two solutions to the same I/O-bound problem — async uses one thread cleverly; pools use several.

---

## The GIL: why threads don't always mean parallelism

A subtlety that's a favorite Python interview question and a genuine gotcha.

> 💡 **Concept notes — the GIL (Global Interpreter Lock)**
> Python (the standard CPython) has a **Global Interpreter Lock** — a single lock that lets only *one* thread execute Python bytecode at a time, even on a multi-core machine. The consequence: Python threads give you **concurrency but not true parallelism for CPU-bound work** — multiple compute-heavy threads can't actually run on multiple cores simultaneously; they take turns. Threads *still help for I/O-bound* work (the GIL is released while waiting on I/O), but for *CPU-bound* work in Python you need **multiprocessing** (separate processes, each with its own interpreter and GIL, running on different cores) to get real parallelism. "Use threads/async for I/O-bound, multiprocessing for CPU-bound — because of the GIL" is the textbook Python answer, and it ties this whole chapter together.

---

## Putting it together: the decision

> 💡 **Concept notes — the cheat sheet**
> | Your work is... | Bottleneck | Reach for... |
> |---|---|---|
> | I/O-bound (waiting on DB/network/disk) | Waiting | **async/await** (one thread, event loop) or a **thread pool** |
> | CPU-bound (heavy computation) | Computing | **Multiple processes / cores** (true parallelism); in Python, **multiprocessing** |
> The mistake to avoid: throwing async at a CPU-bound task (it'll block the event loop and freeze everything), or expecting Python threads to speed up a number-crunching loop (the GIL won't let them). Always start by classifying the work.

---

## Try it

1. Define I/O-bound and CPU-bound, and explain why this single distinction drives your choice of concurrency tool.
2. Describe how an event loop handles thousands of connections on one thread. What makes that possible?
3. What does `await` actually do at the moment it's hit? Why does async do nothing for CPU-bound work?
4. What is a thread pool and what problem does it solve versus spawning a thread per task?
5. Explain the GIL and its consequence: for CPU-bound Python work, why won't threads help, and what do you use instead?
6. A Python web service handles many slow database calls and feels sluggish under load. Is it likely I/O- or CPU-bound, and what would you reach for? What if instead it were resizing thousands of images?

*Write your answers in [ch9-concurrency-tryit.md](../code/ch9-concurrency-tryit.md).*

---

## The bumper sticker

> *Before picking a concurrency tool, ask one question: is the work I/O-bound (mostly waiting) or CPU-bound (mostly computing)? For waiting, overlap it — async on an event loop, or a thread pool. For computing, you need real parallelism across cores — and in Python, that means multiprocessing, because the GIL won't let threads compute in parallel.*

Next: before the closing ritual, one chapter on the language you've been writing this whole track in — the Python idioms an interviewer assumes you know, each derived from the boilerplate it kills.

---

<div align="right">

[Chapter 10 →](ch10-python.md)

</div>
