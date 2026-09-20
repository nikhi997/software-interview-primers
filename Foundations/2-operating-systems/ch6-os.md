# Chapter 6: Memory — stack, heap, and leaks

*[← Chapter 5](ch5-os.md) · [Contents](../foundations-README.md)*

- [ ] **Mark as read**

Where does your data actually *live* while a program runs? Most developers go years without a clear answer, and then an interviewer asks "what's the difference between the stack and the heap?" and they wave their hands. This chapter gives you the crisp mental model. It's the second OS chapter, and it closes out the "what the machine does with your code" layer. The mechanism to feel: memory isn't one undifferentiated blob — it's organized into regions with very different rules, and knowing which is which explains crashes, leaks, and performance.

---

## Two regions: the stack and the heap

When your program runs, the OS gives its process a block of memory, and two parts of it matter most: the **stack** and the **heap.** They behave completely differently.

> 💡 **Concept notes — the stack**
> The **stack** holds the bookkeeping for function calls. Every time you call a function, a **stack frame** is pushed on: its local variables, parameters, and where to return when it finishes. When the function returns, its frame is **popped** off and that memory is instantly reclaimed. It's a literal stack (last-in-first-out), which is why it's *fast* — allocating is just moving a pointer — and *automatic*: you never manage it. The catch is it's limited in size and its lifetime is tied to the function call. Infinite recursion overflows it — that's a **stack overflow.**

> 💡 **Concept notes — the heap**
> The **heap** is the region for data that must outlive a single function call or whose size isn't known until runtime — anything you explicitly allocate (objects, large arrays, data structures). It's flexible and large, but slower to allocate (the system must *find* a suitable free block) and it must be *cleaned up* — either manually (C/C++ `free`/`delete`) or automatically by a garbage collector. The trade: stack is fast/automatic/short-lived; heap is flexible/large/long-lived but needs management.

> 💡 **Concept notes — the quick contrast (memorize this)**
> | | **Stack** | **Heap** |
> |---|---|---|
> | Holds | Local variables, call frames | Dynamically allocated objects |
> | Speed | Very fast (move a pointer) | Slower (find a free block) |
> | Management | Automatic (pop on return) | Manual or garbage-collected |
> | Lifetime | Until the function returns | Until freed / collected |
> | Failure | Stack overflow | Memory leak, fragmentation |
> "Stack for short-lived local variables, automatic and fast; heap for long-lived dynamically-allocated data, flexible but needs cleanup" is the answer interviewers want.

---

## How the heap gets cleaned up: garbage collection

Heap memory must be returned when no longer needed, or it accumulates. In languages like Java, Python, Go, JavaScript, you don't free it by hand — a **garbage collector** does.

> 💡 **Concept notes — garbage collection (GC)**
> A **garbage collector** automatically reclaims heap memory that the program can no longer reach. The core idea is **reachability**: starting from "roots" (local variables on the stack, globals), the GC traces every object you can still get to by following references. Anything *not* reachable is garbage — nobody can use it — so its memory is freed. This frees you from manual memory management (and the whole class of bugs that come with it: use-after-free, double-free, forgetting to free). The cost: GC runs periodically and can pause your program briefly ("GC pauses" / "stop-the-world"), which matters for latency-sensitive systems — a real tradeoff worth mentioning.

---

## The bug that survives garbage collection: memory leaks

Surprising fact that makes a great interview point: **garbage-collected languages can still leak memory.** GC only frees what's *unreachable* — so if you accidentally keep a reference to something you're done with, the GC thinks it's still needed and never frees it.

> 💡 **Concept notes — memory leak**
> A **memory leak** is memory that's no longer needed but never reclaimed, so the program's memory use grows over time until it slows or crashes (out-of-memory). In manual languages, a leak is forgetting to `free`. In *garbage-collected* languages, a leak is an **unintended reference that keeps an object alive** — the classic example is a cache or a list you keep appending to but never clear, or an event listener you register but never remove. The object stays reachable, so GC won't touch it, even though you'll never use it again. The tell-tale symptom: memory climbs steadily and never comes back down, often crashing a long-running server after hours or days. The fix is finding and dropping the stray reference (clear the cache, unregister the listener, null out the field). Knowing that "GC doesn't prevent leaks — it just changes their form to *accidental retention*" is a genuinely senior insight.

---

## Pass by value vs pass by reference (a quick but common one)

When you pass a variable to a function, does the function get a *copy* or the *original*? This connects directly to stack vs heap and trips people up.

> 💡 **Concept notes — value vs reference**
> - **Pass by value:** the function gets a *copy*; changes inside don't affect the caller's variable. Typically how primitives (numbers, booleans) behave.
> - **Pass by reference:** the function gets a *reference* to the same underlying object; changes are visible to the caller. Typically how objects/arrays behave (the reference is copied, but it points at the same heap object).
> This is why modifying a list inside a function changes the caller's list, but reassigning a number doesn't. Languages differ in the details (Java is "pass by value" but the value passed for objects is a reference; Python is "pass by object reference"), and a careful candidate notes that nuance rather than over-claiming.

---

## Try it

1. Fill in the contrast: stack vs heap on speed, management, lifetime, and what holds what.
2. What is a stack overflow, and what common programming mistake causes it?
3. Explain garbage collection using the idea of "reachability." What gets collected and what doesn't?
4. Your Java service's memory climbs all day and the box OOM-crashes every night, yet it's garbage collected. How is that possible, and where would you look?
5. Give a concrete code pattern that causes a memory leak in a GC language.
6. You pass a list to a function and the function appends to it; the caller sees the change. You pass an integer and increment it; the caller doesn't. Explain why in terms of value vs reference.

*Write your answers in [ch6-os-tryit.md](../code/ch6-os-tryit.md).*

---

## The bumper sticker

> *The stack is fast, automatic, and short-lived — local variables that vanish when a function returns. The heap is flexible and long-lived but must be cleaned up. Garbage collection automates that cleanup by freeing unreachable objects — but a stray reference still leaks, because GC can't free what you're accidentally still holding.*

That completes the OS section. Next we move to the wire — networking: TCP, HTTP, TLS, DNS, and what really happens between two machines.

---

<div align="right">

[Chapter 7 →](../3-networking/ch7-networking.md)

</div>
