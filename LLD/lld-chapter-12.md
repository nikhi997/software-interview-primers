# Chapter 12: Smells, names, and refactoring

*[← Chapter 11](lld-chapter-11.md) · [Contents](lld-README.md)*

- [ ] **Mark as read**

You can model classes now. You can reach for the right pattern. But here's a truth no pattern catalogue mentions: **code is read and changed far more often than it's written.** The first version of a class is the easy part. The cost lands every time someone — usually a future you, six months from now, with no memory of today — has to open it and change it without breaking it.

This chapter is the craft of keeping code *changeable*. It's the part captured by Robert C. Martin's *Clean Code*, Martin Fowler's [*Refactoring*](https://refactoring.com/), and David Thomas and Andrew Hunt's [*The Pragmatic Programmer*](https://pragprog.com/titles/tpp20/the-pragmatic-programmer-20th-anniversary-edition/) — three books that circle the same idea from different angles. We'll do it our way: start from code that works but fights you, learn to name the discomfort, then fix it with small safe moves.

> Working code is the floor, not the ceiling. Optimize for the next person who has to change it — it's usually you.

---

## The pain: code that works but fights you

Here's a function that processes a checkout. It works. It passes its tests. Ship it.

```python
def proc(c, items):
    t = 0
    for i in items:
        t += i[1] * i[2]
    if c[3] == 1:
        t = t * 0.9
    elif c[3] == 2:
        t = t * 0.8
    if t > 100:
        s = 0
    else:
        s = 10
    if c[4] == "CA":
        tax = t * 0.0725
    elif c[4] == "NY":
        tax = t * 0.08
    else:
        tax = t * 0.05
    return t + s + tax
```

Now actually try to *change* it. The product manager says: *"Gold members should get free shipping too, and we're adding Texas at 6.25%."* Go on — find where. You have to decode `c[3]`, `c[4]`, the bare `0.9`, the `100` threshold, the `s` that's secretly "shipping." Every edit is a small act of archaeology, and every guess risks breaking a branch you didn't fully understand.

The code isn't *wrong*. It's *hostile*. That hostility has names.

---

## Smells: naming the discomfort

A **code smell** is a surface sign that something underneath will hurt to change. Smells aren't bugs — the code runs fine. They're warnings. Learning their names turns a vague "ugh" into a precise "ah, that's a long method with magic numbers."

> 💡 **Concept notes — the smells in that function**
> - **Cryptic names:** `proc`, `c`, `t`, `i`, `s`. A name should say what the thing *is*. `c[3]` tells you nothing; `customer.tier` tells you everything.
> - **Magic numbers:** `0.9`, `100`, `0.0725`, `1`, `2`. Unexplained literals. What is `2`? Why `100`? The number encodes a meaning that lives only in the author's head.
> - **Long method doing many jobs:** this one function computes a subtotal, applies a discount, decides shipping, *and* computes tax. Four responsibilities welded together (Single Responsibility, Chapter 11, at the function level).
> - **Primitive obsession:** a customer is a tuple `c` indexed by position. `c[3]` is the tier, `c[4]` is the state — knowledge that should live in a `Customer` class, not in every caller's memory.
> - **Duplicated structure:** the `if/elif` ladders for tier and state are the same shape repeated — and you know from Chapter 9 where duplication leads.
> - **Comment-as-deodorant** (when you see it): a comment like `# apply discount` over a cryptic block is often a smell — it's a name wishing it were code. Prefer a well-named function over a comment explaining a bad one.

---

## Refactoring: change the shape, not the behavior

**Refactoring** is improving the *structure* of code without changing what it *does*. Same inputs, same outputs — better shape. The discipline that makes it safe: **one small step at a time, with tests (or at least a REPL check) after each**, so if behavior changes you know exactly which step did it.

Let's clean the checkout, move by move.

**Move 1 — Rename to intention-revealing names, and give the customer a class.** Kill primitive obsession first:

```python
class Customer:
    def __init__(self, name, tier, state):
        self.name = name
        self.tier = tier        # "standard", "silver", "gold"
        self.state = state      # "CA", "NY", ...
```

**Move 2 — Replace magic numbers with named constants.** Now the literals explain themselves:

```python
TIER_DISCOUNT = {"standard": 0.0, "silver": 0.10, "gold": 0.20}
STATE_TAX_RATE = {"CA": 0.0725, "NY": 0.08, "TX": 0.0625}
DEFAULT_TAX_RATE = 0.05
FREE_SHIPPING_THRESHOLD = 100
FLAT_SHIPPING_FEE = 10
```

Notice the PM's two requests just got *easy*: adding Texas is one line in `STATE_TAX_RATE`; the tier table is one line per tier. The data that varies is now data, not buried `if` branches.

**Move 3 — Extract each responsibility into its own well-named function.** One job per function:

```python
def subtotal(items):
    return sum(line.unit_price * line.quantity for line in items)


def discount_rate(customer):
    return TIER_DISCOUNT.get(customer.tier, 0.0)


def shipping_fee(amount, customer):
    if amount > FREE_SHIPPING_THRESHOLD or customer.tier == "gold":
        return 0
    return FLAT_SHIPPING_FEE


def tax(amount, customer):
    rate = STATE_TAX_RATE.get(customer.state, DEFAULT_TAX_RATE)
    return amount * rate
```

**Move 4 — Compose them into a tiny, readable top-level function:**

```python
def checkout_total(customer, items):
    discounted = subtotal(items) * (1 - discount_rate(customer))
    return discounted + shipping_fee(discounted, customer) + tax(discounted, customer)
```

Read that last function out loud. It *is* the business rule: take the subtotal, apply the customer's discount, add shipping and tax. The PM's "gold gets free shipping" lives in exactly one obvious place (`shipping_fee`). Same output as the ugly `proc`. Completely different cost to change.

> 💡 **Concept notes — the refactoring moves you'll use most**
> - **Rename:** the highest-value, lowest-risk refactor. A good name removes the need for a comment and a re-read.
> - **Extract Function/Method:** pull a chunk that does one thing into its own named function. The name becomes documentation.
> - **Replace Magic Number with Named Constant:** give the literal a name that states its meaning.
> - **Introduce Class / Replace Primitive with Object:** when several primitives always travel together (a customer's name, tier, state), make them a class.
> - **Replace Conditional with Polymorphism:** when a big `if/elif` switches on a *type* and that switch is repeated in several places, push each branch into a subclass or strategy object — you've done this already (State in Chapter 7, inheritance in Chapter 9). Use it when the conditional keeps reappearing, not for a single small `if`.
> Refactoring is never one big rewrite. It's a chain of these tiny, behavior-preserving steps, each verifiable on its own.

---

## The principles underneath

These moves aren't arbitrary taste. They're three durable principles wearing work clothes.

> 💡 **Concept notes — DRY, YAGNI, orthogonality**
> - **DRY — Don't Repeat Yourself.** Every piece of knowledge should have *one* authoritative home. The tax rates live in one table, not scattered across `if` branches. We felt the cost of violating this in Chapter 9: duplicated logic drifts, and drift is a bug waiting for the worst moment.
> - **YAGNI — You Aren't Gonna Need It.** Don't build for an imagined future. It's tempting to add a plugin system for "any future discount type" before anyone's asked. Resist. Speculative generality is its own smell — it adds weight and indirection to pay for a requirement that may never arrive. Build for today's requirement; refactor when tomorrow's actually shows up. (YAGNI and "design for change" aren't in conflict: keep the code *clean* so change is cheap, but don't *pre-build* the change.)
> - **Orthogonality / decoupling.** Independent things should stay independent, so one change doesn't ripple. After refactoring, changing a tax rate can't possibly affect shipping — they're separate functions with no shared state. When editing one thing forces edits in five unrelated places, that's a coupling smell.

---

## Anti-patterns: smells that grew up

A smell is local — one hostile function. Let it spread unchecked across a codebase for a year and it hardens into an **anti-pattern**: a *structural* mistake big enough to have a name and a reputation. Same idea as a smell, one level up — a solution that looks reasonable in the moment but reliably makes the whole system harder to change. Naming them is a senior signal: it turns "this codebase is a mess" into a precise diagnosis with a known cure.

> 💡 **Concept notes — the anti-patterns interviewers expect you to name**
> - **God object / God class.** One class that knows and does everything — the `Manager` with 3,000 lines that every other class leans on. *Spot it:* the file everyone edits and no one understands; a class with a dozen unrelated responsibilities. *Fix:* Single Responsibility (Ch 11) — find the jobs it's doing and extract each into its own class.
> - **Big Ball of Mud (spaghetti code).** No discernible architecture — everything reaches into everything, control flow you can't trace. Usually the end state of ignored smells. *Spot it:* changing one feature breaks three unrelated ones. *Fix:* introduce boundaries incrementally (extract modules, add seams, decouple); there is no single big rewrite that's safe.
> - **Golden Hammer.** "When all you have is a hammer, everything looks like a nail" — forcing one familiar tool onto every problem (Singleton everywhere, inheritance for everything, a message queue for a function call). *Spot it:* the same solution shape regardless of the problem. *Fix:* choose from the pain, not from habit — the whole thesis of this book.
> - **Premature optimization / speculative generality.** Adding complexity for a performance or flexibility need that hasn't shown up — the YAGNI violation, structural edition. *Spot it:* a plugin system with one plugin, a cache nobody measured a need for, an abstract base class with one subclass. *Fix:* delete the speculative layer; add it back when a *second* real case arrives.
> - **Lava flow.** Dead or mysterious code no one dares remove, so it accretes forever — commented-out blocks, a `handle_v1_legacy()` still wired in. *Spot it:* "don't touch that, nobody knows what it does." *Fix:* prove it's unused (tests, logging, coverage) and delete it — version control remembers it if you're wrong.

The through-line: every anti-pattern is a *local* good intention (one convenient class, one familiar tool, one just-in-case abstraction) that was never refactored and grew load-bearing. You catch them the same way you catch smells — by feeling the change get harder — and you fix them with the same small, safe moves, just applied at the seams *between* classes instead of inside one function.

---

## Names are a design tool: speak the domain's language

Of all the moves, renaming carries the most weight — because a name is a tiny piece of design. And the best names aren't invented; they're *borrowed from the business.*

Here's the pain. The word "user" means three different things at your company: to the growth team it's a *signup*, to billing it's an *account*, to support it's a *ticket-opener*. Your code says `user` everywhere. In a meeting, someone says "cancel the user" — billing hears "close the account," support hears "ban the person," and a bug is born in the gap between the two meanings. The ambiguity in the conversation became ambiguity in the code.

The fix is to agree on **one precise word per concept and use that exact word everywhere** — in conversation, on the whiteboard, and in the code. If the domain calls it a `Subscription`, the class is `Subscription`, the variable is `subscription`, and everyone says "subscription." This shared, rigorous vocabulary is called the **ubiquitous language**, and it's the heart of Domain-Driven Design.

> 💡 **Concept notes — the ubiquitous language (and why it's a craft skill)**
> The **ubiquitous language** is a shared, precise vocabulary for the domain, used identically by engineers and non-engineers and reflected directly in the code's class and method names. Its payoff: there's no translation layer between "what the business said" and "what the code calls it," so whole categories of misunderstanding-bugs never happen. In an interview, naming your classes after real domain terms — `BoardingPass`, `Reservation`, `LedgerEntry`, not `DataManager` or `InfoObject` — signals that you think in the problem's language, which is exactly the senior signal designers look for. When one word starts meaning two things, that's usually a sign you actually have *two* concepts that deserve two names (and often two classes) — the same "is it really one thing?" instinct from Chapter 9's noun-spotting.

---

## In the interview

LLD interviewers watch your *naming* and whether you *refactor as you go*. Reaching for `tmp`, `data`, `mgr` reads as junior; naming the domain crisply and saying "this `if` ladder is a smell — in real code I'd push it into strategy objects, but I'll keep it inline for time" reads as someone who's shipped and maintained software. You don't have to refactor everything live. You have to *see* the smells and *narrate the tradeoff*. That narration is the signal.

---

## Try it

1. Take the original `proc` function. Without looking at the refactored version, add a "Texas at 6.25%" tax and "platinum tier at 30% off, free shipping." Time yourself. Then do the same on `checkout_total`. The gap between the two times *is* the value of refactoring — feel it.
2. Name the smell in each: (a) a function with eight parameters; (b) a `Vehicle` class with a `print_invoice()` method; (c) the literal `86400` appearing in five files; (d) a variable named `data2`.
3. Refactoring is "behavior-preserving." Why does that definition make tests (or REPL checks) essential to doing it safely? What goes wrong if you "refactor" and change behavior in the same step?
4. Name the anti-pattern: (a) a `SystemManager` class imported by 40 other files; (b) a codebase where every new type is added by subclassing a 12-level-deep hierarchy; (c) a 600-line function no one will touch because "it works." For each, what's the first small move to improve it?
5. Your team's code uses `user`, `customer`, `account`, and `member` interchangeably for the same concept. Walk through how you'd establish a ubiquitous language for it: who do you talk to, how do you pick the one word, and what do you change?
6. YAGNI vs "design for change" sound contradictory. Give one concrete example where adding flexibility now is *premature* (violates YAGNI), and one where *not* adding a seam now will clearly hurt. What distinguishes them?

*Write your answers in [lld-chapter-12-tryit.md](code/lld-chapter-12-tryit.md).*

---

## The bumper sticker

> *Working code is just the first draft. The craft is keeping it changeable: name things in the domain's own words, keep each piece doing one job, and refactor in small safe steps the moment a smell shows up — because the person who pays for messy code is almost always future you.*

Next: a picture is worth a thousand classes. Time to draw what you've been building — UML, the 10% you actually need.

---

<div align="right">

[Chapter 13 →](lld-chapter-13.md)

</div>
