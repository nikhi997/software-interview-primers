# Chapter 9: The classes under the patterns — Try it

*Answers for the Try it questions in [lld-chapter-9.md](../lld-chapter-9.md).*

1. Model a shopping **cart** with plain classes only — no patterns. Start from this blurb: *"A cart holds line items. Each item has a product name, unit price, and quantity. The cart can add an item, remove an item by product name, and report its total. Premium customers get free shipping; everyone else pays a flat fee."* Name your classes, their attributes, and their methods *before* writing code.


2. In your cart model, is "premium customer" an `is-a` (a subclass of Customer) or a `has-a` (a flag/role the customer holds)? Argue both, then pick one and justify it.


3. You have `Circle`, `Rectangle`, and `Triangle`, each with an `area()`. Write the one base class they should share and the loop that prints every shape's area without checking its type. Which methods go in the base, and which must each subclass override?


4. Someone models `class Stack(list)` so a stack inherits all of `list`'s methods. Why is that a tempting but dangerous `is-a`? What could a caller do to your "stack" that breaks its meaning, and how would composition (`has-a` a list) fix it?


5. Take the `Employee` hierarchy and add a `Contractor` who is paid an hourly rate, not a salary. Does `Contractor` belong under `Employee`? What does it inherit cleanly, and what does it have to override — and does that tell you the hierarchy is right or strained?


6. Turn the `Circle`/`Rectangle`/`Triangle` shapes from Q3 into an abstract base class `Shape`. Which import and which decorator do you need, why can no one create a bare `Shape()` anymore, and at what exact moment does someone who writes `class Hexagon(Shape)` *without* an `area()` find out they forgot it?
