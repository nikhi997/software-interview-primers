# Chapter 12: Smells, names, and refactoring — Try it

*Answers for the Try it questions in [lld-chapter-12.md](../lld-chapter-12.md).*

1. Take the original `proc` function. Without looking at the refactored version, add a "Texas at 6.25%" tax and "platinum tier at 30% off, free shipping." Time yourself. Then do the same on `checkout_total`. The gap between the two times *is* the value of refactoring — feel it.


2. Name the smell in each: (a) a function with eight parameters; (b) a `Vehicle` class with a `print_invoice()` method; (c) the literal `86400` appearing in five files; (d) a variable named `data2`.


3. Refactoring is "behavior-preserving." Why does that definition make tests (or REPL checks) essential to doing it safely? What goes wrong if you "refactor" and change behavior in the same step?


4. Name the anti-pattern: (a) a `SystemManager` class imported by 40 other files; (b) a codebase where every new type is added by subclassing a 12-level-deep hierarchy; (c) a 600-line function no one will touch because "it works." For each, what's the first small move to improve it?


5. Your team's code uses `user`, `customer`, `account`, and `member` interchangeably for the same concept. Walk through how you'd establish a ubiquitous language for it: who do you talk to, how do you pick the one word, and what do you change?


6. YAGNI vs "design for change" sound contradictory. Give one concrete example where adding flexibility now is *premature* (violates YAGNI), and one where *not* adding a seam now will clearly hurt. What distinguishes them?
