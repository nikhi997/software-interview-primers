# Appendix: Quick reference

*[← Chapter 20](lld-chapter-20.md) · [Contents](lld-README.md)*

Three short references for after you've finished the book. Not study material — lookup material. Want the whole book applied to one running system instead? See the [code evolution companion](lld-code-evolution.md). Want retrieval practice in fresh domains instead? See the [cold rebuild drills](lld-cold-rebuild-drills.md). Want to turn dependency inversion and concurrency into executable evidence? See the [boundaries and testing companion](lld-boundaries-and-testing.md).

## A. Pattern catalog

The patterns covered, one line each:

**Strategy** — A class delegates one job to a swappable object. Caller picks. *For:* swappable algorithms (storage backends, payment methods, pricing rules, matching).

**Observer** — A class announces events; multiple listeners react independently. *For:* notifications, audit logs, UI updates, anything that fans out.

**State** — Object behavior changes based on its state; each state is a class. *For:* lifecycle objects with rich transitions (orders, trips, document workflows).

**Decorator** — Wrap an object to add behavior without modifying it. *For:* cross-cutting concerns (logging, encryption, caching, middleware).

**Singleton** — Enforce that only one instance of a class ever exists. *For:* shared resources (loggers, config). *Controversial — prefer dependency injection where possible.*

**Factory** — Hide construction details behind a function or class. *For:* configurable object creation, especially when the right type depends on runtime data.

**Proxy** — A stand-in with the same interface as the real object, controlling access to it. *For:* lazy/expensive creation (virtual), access control (protection), caching.

**Facade** — One simple interface over a complicated subsystem. *For:* hiding multi-step orchestration (checkout, booking) behind a single call.

**Chain of Responsibility** — A request travels a chain of handlers; each one handles it or passes it on. *For:* middleware, validation pipelines, approval/escalation workflows.

**Other patterns you'll meet eventually** (worth knowing the names):
- **Adapter** — make incompatible interfaces work together
- **Command** — wrap an action as an object (for queueing, undo, retry)
- **Template Method** — define the skeleton of an algorithm, let subclasses fill in steps
- **Builder** — construct complex objects step by step
- **Composite** — treat individual objects and groups uniformly (trees)

## B. OOP modeling & code craft

**The modeling recipe (Ch 9).** Given a "design X" prompt with no obvious pattern:
1. Nouns → candidate classes (demote single-value nouns to attributes).
2. What each class *knows* → attributes.
3. What each class *does* → methods.
4. Each relationship: *is-a* → inherit; *has-a* → compose. Favor composition.
5. Hide state that has rules behind methods that enforce them (encapsulation).
6. *Only now* reach for a pattern — most classes need none.

**The four OOP words, plainly.** Encapsulation = bundle data with the methods that guard it (expose behavior, hide state). Abstraction = expose *what*, hide *how*. Inheritance = `is-a` reuse. Polymorphism = one call, many behaviors.

**Inheritance vs composition.** Inherit only on a true, stable `is-a` (Engineer *is a* Employee). Otherwise compose (Manager *has a* CodingSkill). Deep hierarchies and multiple inheritance are smells; favor composition.

**Code smells to name (Ch 12).** Cryptic names, magic numbers, long method, primitive obsession, duplication, long parameter list, comment-as-deodorant, speculative generality.

**Refactoring moves.** Rename; Extract Function; Replace Magic Number with Constant; Replace Primitive with Object; Replace Conditional with Polymorphism. Small, behavior-preserving steps, verified after each.

**Principles.** DRY (one home per fact), YAGNI (don't build for imagined futures), orthogonality (one change shouldn't ripple), ubiquitous language (one precise domain word, used identically in code and conversation).

## C. Concurrency — the basics for LLD

If an interviewer asks "what if multiple threads access this?", here's the toolkit.

**Race condition.** Two threads read-modify-write the same variable. One overwrites the other. Fix: lock the operation.

**Lock (mutex).** Acquire before the critical section, release after. In Python: `threading.Lock()`.

```python
import threading

class Counter:
    def __init__(self):
        self.count = 0
        self.lock = threading.Lock()

    def increment(self):
        with self.lock:
            self.count += 1
```

**Common pitfall — deadlock.** Two threads each hold a lock the other needs. Avoid by always acquiring locks in the same order, or by using timeouts.

**Stateless > stateful when possible.** A class with no mutable shared state is thread-safe by default. Strategy and Observer pattern classes are often stateless or per-thread — half of why they're easy to reason about.

**For LLD interviews you need to be able to:**
- Identify which methods need locking (anything mutating shared state)
- Mention thread safety as a tradeoff when relevant
- Know that read-heavy systems benefit from read-write locks
- Know that compare-and-swap exists at a high level

You don't need to implement a concurrent system in an LLD interview. You need to *talk about* concurrency intelligently when asked.

For a worked example — making "check the seat, then take it" one atomic step so two users can't grab the same seat — see Ch20.

## D. Common pitfalls

**Pattern shoehorning.** Using a pattern because you know its name, not because the problem needs it. If "no patterns" is also a clean answer, sometimes that's the right answer.

**Premature abstraction.** Extracting to a Strategy when there's only one algorithm and no second one in sight. Wait until you have two.

**God classes.** One class that knows about everything. The fix is almost always Single Responsibility — find the jobs it's doing, pull each into its own class.

**Big Ball of Mud (spaghetti).** No architecture — everything reaches into everything, so one change breaks unrelated features. The end state of ignored smells. Fix by introducing boundaries incrementally (extract modules, add seams), never one big rewrite.

**Golden Hammer.** Forcing one familiar tool or pattern onto every problem (Singleton everywhere, a queue for a function call). Choose from the pain, not from habit.

**Lava flow.** Dead or mysterious code no one dares delete, accreting forever. Prove it's unused and remove it — version control remembers it if you were wrong.

**Anemic models.** Classes that are just data (all getters and setters, no logic). Behavior leaks into "Service" classes. Sometimes okay, often a sign the class doesn't know its own behavior.

**Inheritance overuse.** Reaching for inheritance when composition would be cleaner. "Is-a" → inheritance. "Has-a" → composition. When in doubt, prefer composition.

**Hidden side effects.** Methods named like questions (`get_x`, `find_y`) that secretly mutate state. Keep reads and writes separate. (Remember `peek` vs `return_long_url` from Ch3's reps.)

**Mocking too much in tests.** If a class is hard to test without mocks, that's design feedback. The fix is usually dependency injection — passing collaborators in instead of creating them inside.

## E. The 25-minute interview budget

A typical LLD interview is 45 minutes. After intros and follow-ups, you have ~25 minutes of design time. Rough budget:

- **5 min** — clarify requirements
- **5 min** — identify entities, sketch class diagram
- **10 min** — code skeleton, walk one flow
- **5 min** — discuss tradeoffs, answer follow-ups

Stay within these. If you blow 20 minutes on requirements, you'll have nothing to show. Move on even when uncertain — note assumptions and proceed. "I'm assuming single currency for now" is a valid move.

## F. Final notes

The patterns in this book are the foundation, not the ceiling. Once you've internalized these, you'll see them everywhere — in framework source code, in your colleagues' designs, in your own past code.

The skill you're really building isn't "knowing patterns." It's *seeing the smell that calls for a pattern.* That comes from reps. Lots of them. Across many problems. Over months.

Be patient with the process. The understanding comes faster than you'd think — but the *automatic recognition* takes time. Trust it.
