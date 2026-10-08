# Chapter 11: Names for things you already do

*[← Chapter 10](lld-chapter-10.md) · [Contents](lld-README.md)*

- [ ] **Mark as read**

You've written ten chapters of code. Felt the pain points. Moved code around to relieve them. Named four patterns.

Now I'm giving you a vocabulary. It's called **SOLID** — five principles for OO design. Each one is a name for something you've already done.

This chapter is short and dense. You've earned every word.

## S — Single Responsibility

> A class should have one reason to change.

Chapter 3. The URLShortener used to do *two* things: manage URLs, AND save to a file. Adding Redis would have changed the same class. Adding a new URL feature would have changed the same class. The class had two reasons to change.

We pulled storage into its own class. Now URLShortener changes only when URL logic changes. FileStorage changes only when file storage logic changes.

That's Single Responsibility.

Note what it does *not* say. Not "one method per class." Not "small classes." It says: *one reason to change.* A class doing ten things, all serving one cohesive purpose, has single responsibility.

## O — Open/Closed

> Open for extension. Closed for modification.

Chapter 3 again. After extracting storage, adding Redis was one new class. URLShortener didn't change. The system was *extended* without *modifying* existing code.

Chapter 5 again. Adding a new notifier was one new class. The order service didn't change.

Chapter 8 again. Adding compression as a wrapper meant a new class. Nothing existing changed.

Closed for modification means: code that works should stay working. Open for extension means: new behavior should be addable without touching it.

The way you achieve this is almost always the same: instead of `if/elif` ladders, extract variations into classes that share a shape. Then "new variation" = "new class." Original code untouched.

## L — Liskov Substitution

> If a function works with type T, it should work with any subtype of T.

The one with the most academic phrasing. Here's what it actually means.

Chapter 10. Your `find_free_spot` method calls `spot.can_fit(vehicle)`. It works with `Motorcycle`, `Car`, `Truck`. None of them surprise the function. They all behave like a Vehicle.

If you made a `class FlyingCar(Vehicle)` whose `size` was sometimes `None` or whose constructor raised an error, code expecting a Vehicle would break when it got a FlyingCar. That's a Liskov violation — the subclass doesn't behave like its parent claims to.

The principle: inheritance is a *promise.* When you say "Car is a Vehicle," you're promising Cars work everywhere Vehicles work. Break the promise, you surprise callers.

In Python, where duck typing dominates, Liskov applies more broadly: anything claiming to have `save` and `load` should *actually* save and load in a way the caller expects. Don't write a "storage" whose `save` silently drops data.

## I — Interface Segregation

> Don't force a class to implement methods it doesn't use.

Subtle in Python because we don't declare interfaces formally. Here's the spirit.

Imagine a `Storage` base class with methods: `save`, `load`, `backup`, `restore`, `migrate`, `replicate`. Every storage has to implement all six.

`MemoryStorage` doesn't need `backup` or `replicate` — there's nothing to back up; it's in memory. But it's forced to implement them anyway, probably as no-ops.

Worse: callers see those methods and might call them, expecting them to work. They don't.

Fix: split the big interface into smaller ones. `Storage` (save, load), `BackupableStorage` (save, load, backup, restore), `ReplicableStorage` (save, load, replicate). Each class implements only what it actually does.

In Python, the practical version: keep your "shapes" small. Don't bloat a contract just because two classes share a category. Two methods (`save`, `load`) was enough for storage. Resist adding more.

## D — Dependency Inversion

> Depend on abstractions, not on concretions.

Chapter 3, again. URLShortener depended on *a storage* (abstraction: something with `save` and `load`). It did *not* depend on *a JSON file* (concretion: specific filename, specific format).

The shortener could be paired with any object matching the storage shape. Meaning the shortener didn't have to change when the concrete storage changed.

This is the "inversion" — instead of the high-level thing (shortener) depending on the low-level thing (file I/O), both depend on a shared abstract shape (storage with save/load).

In code, this almost always looks like *passing dependencies in* (constructor or method arguments) rather than *creating them internally* (hardcoded `open()` inside the class).

## The cheat sheet

- **S** — one class, one job
- **O** — add new things without changing old things
- **L** — children keep their parent's promises
- **I** — small focused interfaces beat sprawling ones
- **D** — depend on shapes, not on specific implementations

That's SOLID. Five lines.

## The honest bit

SOLID is a vocabulary, not a religion. Some experienced engineers think it's overemphasized. Some think it's foundational. Most working code follows three of the five most of the time and breaks one of them somewhere defensible.

What matters is *recognizing* when a SOLID violation is causing pain. "This file is hard to change because it's doing too many things" — that's S. "Adding this feature means modifying ten existing files" — that's O. "This test broke because I added a subclass" — that's L.

When you can articulate the pain in SOLID terms, you can fix it. The names give you shared vocabulary with other engineers. That's the value.

## Before you turn the page

**Exercise:** Take any class you've written professionally in the last year. Apply the five letters:

- Does it have *one* reason to change? (S)
- Can you add new features without modifying it? (O)
- If it has subclasses, do they behave like the parent? (L)
- Are its public methods all things callers actually need? (I)
- Does it depend on specific implementations, or on shapes? (D)

Don't fix anything. Just diagnose. Diagnosing is the skill.

Then make the dependency rule concrete in the [boundaries and testing companion](lld-boundaries-and-testing.md), which carries constructor injection through ports/adapters, repositories, error contracts, and tests at each seam.

---

<div align="right">

[Chapter 12 →](lld-chapter-12.md)

</div>
