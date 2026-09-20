# Chapter 9: The classes under the patterns

*[← Chapter 8](lld-chapter-8.md) · [Contents](lld-README.md)*

- [ ] **Mark as read**

The last six chapters taught you to relieve pain with patterns — Strategy, Observer, State, Decorator, plus Singleton and Factory. But notice what every one of them actually *was*: a plain class with a job. The pattern was the clever bit on top. Underneath sat ordinary classes with attributes and methods, modeling some real-world thing.

The next chapter throws a whole parking lot at you — floors, spots, vehicles, the lot itself — and asks you to wire several patterns through it at once. Before you can do that, you have to do the unglamorous thing first: *turn a pile of requirements into a set of plain classes that relate to each other correctly.* No pattern saves you here. This is modeling, and it's the part most people skip — which is exactly why they freeze when an interviewer says "design a parking lot" and there's no obvious pattern to grab.

This chapter is about the skeleton. And about the one relationship we've quietly leaned on a couple of times without ever slowing down to understand it: **inheritance.**

> Model the nouns first. Reach for inheritance only when the duplication actually demands it.

---

## Finding the classes: noun-spotting

You're handed a blob of requirements. Where do classes even come from? There's a mechanical first move that gets you 80% of the way: **the nouns are your candidate classes, the verbs are your candidate methods, and the describing words are your attributes.**

Take a tiny example. A company wants to track its staff:

> *"Each **employee** has a **name** and an **ID**. **Engineers** write **code** and have a **programming language**. **Managers** run **one-on-ones** and have a list of **reports**. Payroll needs the **monthly pay** for everyone."*

Underline the nouns: employee, name, ID, engineer, code, language, manager, one-on-one, reports, payroll, monthly pay. Most of those are either **classes** (employee, engineer, manager) or **attributes** (name, id, language, reports). The verbs — *write code, run one-on-ones, compute monthly pay* — are **methods**.

> 💡 **Concept notes — noun-spotting, and when a noun is *not* a class**
> Not every noun deserves its own class. A noun becomes a class when it has *its own state and behavior* — things it knows and things it does. "Name" is just a string an Employee holds, so it's an attribute, not a class. "Engineer" has its own data (language) and behavior (writes code), so it's a class. Rule of thumb: if a noun is only ever a single value carried by something else, it's an attribute; if it bundles several values *and* actions, it's a class. When in doubt, start it as an attribute — you can always promote it later when it grows behavior.

---

## Plain classes, plainly

Let's model two of those staff types directly, the obvious way:

```python
class Engineer:
    def __init__(self, name, employee_id, language):
        self.name = name
        self.employee_id = employee_id
        self.language = language
        self.base_salary = 100_000

    def badge(self):
        return f"EMP-{self.employee_id:05d} ({self.name})"

    def monthly_pay(self):
        return self.base_salary / 12


class Manager:
    def __init__(self, name, employee_id, reports):
        self.name = name
        self.employee_id = employee_id
        self.reports = reports
        self.base_salary = 150_000

    def badge(self):
        return f"EMP-{self.employee_id:05d} ({self.name})"

    def monthly_pay(self):
        return self.base_salary / 12
```

Two plain classes. State and behavior, sitting together in a folder, exactly as Chapter 2 taught. No pattern anywhere — and none is needed. This is what most of a modeling problem looks like.

But read those two classes side by side and something should itch.

---

## The pain: duplication that drifts apart

Look at what's *identical* in both classes: the `name` and `employee_id` attributes, the `badge()` method, the `monthly_pay()` method. Copied, character for character, into both.

It works. Until it doesn't. Picture the requirement landing three weeks later:

> *"Badge IDs should be prefixed `ACME-`, not `EMP-`."*

You open `Engineer`, fix `badge()`, test it, ship it. Done. Except there are *two* `badge()` methods, and you only changed one. Managers still print `EMP-`. Nobody notices until a manager is turned away at the door by a security guard whose scanner only knows `ACME-` codes.

> 💡 **Concept notes — the real cost of copy-paste**
> Duplicated logic isn't wrong on the day you write it — both copies are correct and identical. The cost arrives *later*, when the logic has to change. Now "make a change" means "find every copy and change all of them, identically, without missing one." Humans miss one. The two copies *drift*, and a drifted duplicate is a bug that hides until exactly the wrong moment. The pain of duplication is not the typing; it's the future edit. (This is the **DRY** principle — Don't Repeat Yourself — which we'll name properly in the code-craft chapter.)

When two classes share state and behavior because they're *the same kind of thing underneath*, copy-paste is the wrong fix. We want one home for the shared part.

---

## The move: pull the shared part up

`Engineer` and `Manager` are both **employees**. They share what every employee has. So we make that shared thing a real class and let the two specific types build on top of it:

```python
class Employee:
    badge_prefix = "EMP"

    def __init__(self, name, employee_id, base_salary):
        self.name = name
        self.employee_id = employee_id
        self.base_salary = base_salary

    def badge(self):
        return f"{self.badge_prefix}-{self.employee_id:05d} ({self.name})"

    def monthly_pay(self):
        return self.base_salary / 12


class Engineer(Employee):
    def __init__(self, name, employee_id, language):
        super().__init__(name, employee_id, base_salary=100_000)
        self.language = language

    def writes_code_in(self):
        return self.language


class Manager(Employee):
    def __init__(self, name, employee_id, reports):
        super().__init__(name, employee_id, base_salary=150_000)
        self.reports = reports

    def run_one_on_ones(self):
        return [f"1:1 with {r.name}" for r in self.reports]
```

`name`, `employee_id`, `badge()`, and `monthly_pay()` now live in **one place**. `Engineer` and `Manager` *inherit* them — they get all of `Employee`'s attributes and methods for free, and add only what's specific to them.

Now that badge-prefix change? One line, in one class, and *both* types are fixed at once:

```python
class Employee:
    badge_prefix = "ACME"   # changed once; Engineer and Manager both update
```

> 💡 **Concept notes — the inheritance vocabulary, from this code**
> - **Base class / parent / superclass:** `Employee` — the general thing that holds what's shared.
> - **Subclass / child / derived class:** `Engineer(Employee)` — a specific kind that *is an* Employee and gets everything Employee has.
> - **`super().__init__(...)`:** inside the child's constructor, this calls the parent's constructor so the parent's setup (name, id, salary) runs without you re-typing it. You then add the child-specific attributes (`self.language`).
> - **Override:** a subclass can *redefine* a method it inherited, replacing the parent's version with its own. (We'll do this in a moment.)
> - **`is-a`:** the test for whether inheritance is even appropriate. "An Engineer **is an** Employee" — true, so inheritance fits. If you can't say "X is a Y" with a straight face, inheritance is the wrong tool (we'll see why below).

---

## Polymorphism: one loop, many types

Here's the payoff the requirements asked for — payroll needs the monthly pay for *everyone*, regardless of type:

```python
staff = [
    Engineer("Ada", 1, "Python"),
    Manager("Grace", 2, reports=[]),
    Engineer("Linus", 3, "C"),
]

for person in staff:
    print(person.badge(), "->", person.monthly_pay())
```

The loop doesn't check "is this an Engineer or a Manager?" It just calls `monthly_pay()` and trusts each object to know how to compute its own. That's **polymorphism**: the same call (`person.monthly_pay()`) does the right thing for whatever type the object actually is.

It gets sharper when a subclass *overrides* a method. Say managers earn a bonus:

```python
class Manager(Employee):
    def __init__(self, name, employee_id, reports):
        super().__init__(name, employee_id, base_salary=150_000)
        self.reports = reports

    def monthly_pay(self):                      # override
        base = super().monthly_pay()            # reuse the parent's calc
        return base + 1_000 * len(self.reports) # add the manager-specific part
```

The payroll loop **doesn't change at all.** It still just calls `person.monthly_pay()`. Engineers run `Employee`'s version; managers run their own. The caller is blissfully unaware.

> 💡 **Concept notes — polymorphism and overriding**
> *Polymorphism* (literally "many shapes") means one interface, many behind-the-scenes behaviors. A function written against `Employee` works for every present and future subclass without modification — which is exactly the Open/Closed idea from Chapter 3, now powered by inheritance instead of duck typing. *Overriding* is how a subclass customizes inherited behavior; `super().method()` lets it *extend* the parent's behavior rather than replace it wholesale. This is the same shape you've already used — the Strategy and State patterns are polymorphism with a swappable object instead of a subclass. Inheritance is just one way to get it.

---

## Abstract base classes: a contract subclasses must honor

Look again at `Employee`. Does it ever make sense to create a *bare* employee — someone who is neither an engineer nor a manager nor anything else? No. `Employee` exists only to be a parent; the real objects are always some concrete subclass. Yet nothing stops this:

```python
nobody = Employee("Nobody", 99, 100_000)   # a typeless employee — meaningless, but allowed
```

And there's a second, nastier hole. Say payroll *requires* every employee type to answer `monthly_pay()`. Add an `Intern` subclass and forget to write it:

```python
class Intern(Employee):
    def __init__(self, name, employee_id):
        super().__init__(name, employee_id, base_salary=0)
    # oops — forgot monthly_pay(); silently inherits Employee's and returns 0
```

The bug doesn't announce itself. `intern.monthly_pay()` quietly returns the wrong number, and you find out on payday. The base class made a *promise* — "every employee can compute monthly pay" — that the language never enforced.

An **abstract base class** closes both holes. It marks the base as "not a real thing on its own" and marks certain methods as "every subclass MUST implement this":

```python
from abc import ABC, abstractmethod


class Employee(ABC):                        # ABC → can't be instantiated directly
    badge_prefix = "ACME"

    def __init__(self, name, employee_id, base_salary):
        self.name = name
        self.employee_id = employee_id
        self._base_salary = base_salary

    def badge(self):                        # concrete — shared by every subclass
        return f"{self.badge_prefix}-{self.employee_id:05d} ({self.name})"

    @abstractmethod
    def monthly_pay(self):                  # abstract — each subclass must define it
        ...
```

Now the language enforces the contract for you:

```python
Employee("Nobody", 99, 100_000)   # TypeError: Can't instantiate abstract class Employee
Intern("Sam", 7)                  # TypeError too — Intern never implemented monthly_pay()
```

You can't make a bare `Employee`, and you can't make an `Intern` until you actually write its `monthly_pay()`. The mistake moves from *payday* to *the moment you try to construct the object* — which is exactly where you want bugs to surface.

> 💡 **Concept notes — abstract base classes (ABCs)**
> An **abstract base class** exists only to define a contract and share common code — never to be instantiated on its own. In Python you get it from the `abc` module: subclass `ABC`, and decorate the methods every child must provide with `@abstractmethod`. Two guarantees follow: (1) `SomeABC()` raises `TypeError` — you can only instantiate concrete subclasses; (2) a subclass that fails to implement *every* abstract method is itself still abstract and also can't be instantiated. The abstract method body is usually just `...` or a docstring — it's a *signature*, a promise, not logic. This is the formal version of the "interface" you've been leaning on informally: the Strategy in Chapter 3 (`PricingStrategy.calculate()`), the State in Chapter 7, the `Storage` base behind your file/memory/redis classes — each is really an abstract base class declaring *what* its subclasses must do and leaving *how* to them. Reach for an ABC whenever a base (a) should never be created directly and (b) defines methods its subclasses are obliged to fill in.

This is why `Vehicle` (Chapter 10), `Storage` (Chapter 3), and every Strategy or State "interface" in this book are abstract by nature: you never want a bare `Vehicle("ABC-123")` with no real type — only a `Motorcycle`, `Car`, or `Truck`. Marking the base `ABC` makes that rule the computer's job instead of a comment everyone forgets. The earlier caution still applies — don't make a base abstract just because it's a parent — use an ABC when there's a genuine contract to enforce, and leave a plain base class when it's only sharing code.

---

## When inheritance is the wrong tool

Inheritance is seductive. Once you have a hammer that removes duplication, every two classes start looking like they want a common parent. Resist it. Inheritance is a strong claim — "*is-a*" — and when the claim isn't true, you get a mess.

Suppose someone becomes a manager who still writes code. Tempting:

```python
class ManagerWhoCodes(Manager, Engineer):   # multiple inheritance — careful
    ...
```

Now `ManagerWhoCodes` inherits from both. Which `__init__` runs? Both parents expect different arguments. Which `monthly_pay()` wins — the Manager bonus version, or the Employee base version through Engineer? Python has rules for this (the "method resolution order"), but the fact that you have to *look them up* is the warning sign. You've modeled a *role someone plays* as a *type they are*, and the type system is now fighting you.

The fix is to ask the better question: is "writes code" something this person **is**, or something they **have**? It's a capability they have. Model it as a thing they hold, not a parent they inherit:

```python
class CodingSkill:
    def __init__(self, language):
        self.language = language

    def write_code(self):
        return f"writing {self.language}"


class Manager(Employee):
    def __init__(self, name, employee_id, reports, coding_skill=None):
        super().__init__(name, employee_id, base_salary=150_000)
        self.reports = reports
        self.coding_skill = coding_skill   # has-a, optional

    def monthly_pay(self):
        base = super().monthly_pay()
        return base + 1_000 * len(self.reports)
```

A coding manager is just a `Manager` who *has* a `CodingSkill`. A non-coding one has `None`. No diamond, no resolution-order puzzle, and you can add a skill to anyone without touching the class hierarchy.

> 💡 **Concept notes — is-a vs has-a, and "favor composition over inheritance"**
> Two ways to reuse another class's stuff:
> - **Inheritance (`is-a`):** `Engineer(Employee)`. Use it when the subclass genuinely *is a kind of* the parent and behaves like it everywhere the parent is expected. It's rigid — a subclass is welded to its parent's internals, and a change to the parent can break every child (the "fragile base class" problem).
> - **Composition (`has-a`):** `Manager` *has a* `CodingSkill`. Use it when you're assembling *capabilities* or *roles* rather than refining *what something is*. It's flexible — you swap, add, or remove the held object freely, and the two classes stay loosely coupled.
> The industry rule of thumb is **favor composition over inheritance.** Not "never inherit" — inheritance is right when the `is-a` is real and stable (Engineer/Employee). But when you catch yourself inheriting just to grab some methods, or building deep multi-level hierarchies, or reaching for multiple inheritance — stop, and ask whether *has-a* models it more honestly. The Decorator and Strategy patterns you already know are composition in action.

---

## Encapsulation: hide what can break

One more modeling decision the requirements quietly imply. Salary is sensitive and rule-bound — raises should go through a process, not by anyone reaching in and setting a number. Right now nothing stops this:

```python
ada.base_salary = 9_999_999   # oops
```

Encapsulation is the discipline of **hiding internal state behind methods that enforce the rules**, so the object stays valid no matter who pokes it:

```python
class Employee:
    def __init__(self, name, employee_id, base_salary):
        self.name = name
        self.employee_id = employee_id
        self._base_salary = base_salary     # "internal" by convention

    def give_raise(self, amount):
        if amount <= 0:
            raise ValueError("raise must be positive")
        if amount > 0.5 * self._base_salary:
            raise ValueError("raise too large; needs VP approval")
        self._base_salary += amount

    def monthly_pay(self):
        return self._base_salary / 12
```

Now the *only* sanctioned way to change pay is `give_raise`, and it enforces the rules. The `_` prefix (Chapter 2) signals "internal — don't touch from outside." Python won't physically stop you, but the boundary is now stated, and the valid operations are the public methods.

> 💡 **Concept notes — encapsulation and abstraction as modeling tools**
> **Encapsulation** is bundling data with the methods that guard it, and hiding the raw data behind those methods. The reason isn't secrecy — it's *invariants*. An Employee should never have a negative or absurd salary; by routing all changes through `give_raise`, that can't happen. Expose behavior, hide state. **Abstraction** is the sibling idea: a caller of `give_raise` or `monthly_pay` doesn't need to know *how* pay is stored or computed — just *what* the method promises. Good classes present a small, honest set of verbs and keep the messy "how" inside. Together these are why we bother putting things in classes at all: not to compute anything new (Chapter 2 said classes add a home, not logic) but to make illegal states unreachable and the moving parts few.

---

## The recipe: approaching any "model this" prompt

When an interviewer says "design X" and there's no pattern staring back at you, run this — it's the modeling spine the worked problems (Chapters 15–17) all use:

1. **Find the nouns.** List candidate classes from the requirements. Demote single-value nouns to attributes.
2. **Give each class its state.** What does it *know*? Those are attributes.
3. **Give each class its behavior.** What does it *do*? Those are methods (the verbs).
4. **Wire the relationships.** For each pair, ask *is-a* or *has-a*. Inherit only on a true, stable `is-a`; otherwise compose. Draw the arrows. If a parent is never meant to be instantiated on its own and obliges its children to implement certain methods, make it an **abstract base class** (`ABC` + `@abstractmethod`).
5. **Protect the invariants.** Hide state that has rules; expose methods that enforce them.
6. **Only now, look for patterns.** If a class has swappable algorithms (Strategy), lifecycle-dependent behavior (State), event fan-out (Observer), and so on — *now* reach for the named tool. Most classes won't need one.

Steps 1–5 are plain-class modeling. Step 6 is everything Part 2 taught. The mistake that makes people freeze is jumping straight to step 6.

For step 6, here's the tell-by-phrasing shortcut — what a requirement *sounds like* when it's quietly asking for a pattern:

| When the requirement says… | The tell | Reach for |
|---|---|---|
| "…can be done several ways, configurable/swappable" | swappable algorithm | Strategy |
| "when X happens, several things should react" | event fan-out | Observer |
| "behavior depends on current mode/phase/status" | lifecycle states | State |
| "add behavior on top of existing objects" | layered wrapping | Decorator |
| "build the right object from config, hide construction" | conditional creation | Factory |
| "only one of these may ever exist" | single shared instance | Singleton |
| none of the above | it's just data + verbs | a plain class |

Most rows you'll never trigger on a given problem — that's the point. Patterns are the exception; plain classes are the default.

---

## Try it

1. Model a shopping **cart** with plain classes only — no patterns. Start from this blurb: *"A cart holds line items. Each item has a product name, unit price, and quantity. The cart can add an item, remove an item by product name, and report its total. Premium customers get free shipping; everyone else pays a flat fee."* Name your classes, their attributes, and their methods *before* writing code.
2. In your cart model, is "premium customer" an `is-a` (a subclass of Customer) or a `has-a` (a flag/role the customer holds)? Argue both, then pick one and justify it.
3. You have `Circle`, `Rectangle`, and `Triangle`, each with an `area()`. Write the one base class they should share and the loop that prints every shape's area without checking its type. Which methods go in the base, and which must each subclass override?
4. Someone models `class Stack(list)` so a stack inherits all of `list`'s methods. Why is that a tempting but dangerous `is-a`? What could a caller do to your "stack" that breaks its meaning, and how would composition (`has-a` a list) fix it?
5. Take the `Employee` hierarchy and add a `Contractor` who is paid an hourly rate, not a salary. Does `Contractor` belong under `Employee`? What does it inherit cleanly, and what does it have to override — and does that tell you the hierarchy is right or strained?
6. Turn the `Circle`/`Rectangle`/`Triangle` shapes from Q3 into an abstract base class `Shape`. Which import and which decorator do you need, why can no one create a bare `Shape()` anymore, and at what exact moment does someone who writes `class Hexagon(Shape)` *without* an `area()` find out they forgot it?

*Write your answers in [lld-chapter-9-tryit.md](code/lld-chapter-9-tryit.md).*

---

## The bumper sticker

> *Before any pattern, there's a skeleton of plain classes. Find the nouns, give them state and behavior, and connect them with the honest relationship — `is-a` for inheritance, `has-a` for composition. Inheritance earns its place only when it kills real duplication along a true "is-a"; everywhere else, compose.*

Next: a problem big enough to need *many* classes and *several* patterns at once — the parking lot. Now that you can model the skeleton, you're ready to wire the patterns through it.

---

<div align="right">

[Chapter 10 →](lld-chapter-10.md)

</div>
