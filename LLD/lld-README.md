# LLD Primer — Reading order and study contract

A 20-chapter primer on Low-Level Design, built around a single principle: *feel the pain before naming the pattern.*

## Reading order

Read in sequence. Each chapter assumes the previous ones. Tick each box as you finish a chapter — your own mark-as-read progress tracker.

**Part 1 — Foundation**
- [ ] Chapter 1: The shortest URL shortener that could possibly work
- [ ] Chapter 2: One folder for the loose papers
- [ ] Chapter 3: When the class needs to stop knowing *(Strategy)*
- [ ] Chapter 4: The same shape, different problem *(Strategy variation rep)*

**Part 2 — Patterns through problems**
- [ ] Chapter 5: When one thing happens, many things need to know *(Observer)*
- [ ] Chapter 6: The thing there's only ever one of *(Singleton + Factory)*
- [ ] Chapter 7: When the same action means different things *(State)*
- [ ] Chapter 8: Wrapping behavior around existing classes *(Decorator)*
- [ ] Chapter 9: The classes under the patterns *(plain-class modeling, inheritance vs composition)*
- [ ] Chapter 10: Many patterns, one problem *(Parking lot integration)*

**Part 3 — Naming what you know**
- [ ] Chapter 11: Names for things you already do *(SOLID)*
- [ ] Chapter 12: Smells, names, and refactoring *(code craft, ubiquitous language)*
- [ ] Chapter 13: Drawing what you've been building *(UML)*

**Part 4 — Interview-shaped**
- [ ] Chapter 14: The interview ritual *(Splitwise walkthrough)*
- [ ] Chapter 15: Worked problem — Library Management
- [ ] Chapter 16: Worked problem — Online Shopping
- [ ] Chapter 17: Worked problem — Ride-sharing

**Part 5 — Beyond the core**
- [ ] Chapter 18: A class in front of a class *(Proxy, Facade, Chain of Responsibility)*
- [ ] Chapter 19: Worked problem — LRU Cache *(data-structure-driven design)*
- [ ] Chapter 20: Worked problem — Movie ticket booking *(concurrency + seat locking)*

**Appendix:** Pattern catalog, concurrency basics, common pitfalls.

## Companion tracks

Five different documents live in this folder, and each does a different job. **Chapters teach** — one move per chapter, derived from one pain, in its own toy domain. **The [appendix](lld-appendix.md) looks up** — one-line reference cards for after you already know a move's name. **The [code evolution companion](lld-code-evolution.md) synthesizes** — one running helpdesk system, evolved across all 20 chapters in order, so you can see every move living together instead of in twenty disconnected examples. **The [cold rebuild drills](lld-cold-rebuild-drills.md) retrieve** — 25 short, solution-free drills in fresh domains the book never used, for practicing recognition without a chapter number telling you which pattern applies. **The [boundaries and testing companion](lld-boundaries-and-testing.md) hardens** — one reservation use case separated into ports/adapters, repository and error contracts, then proved with unit, integration, contract, and concurrency tests.

Use them like this:
- Read **lld-code-evolution.md** once, after finishing all 20 chapters, as an end-to-end fidelity check — if a section doesn't click, that's a signal to reopen its paired chapter, not to keep reading past it.
- Work through **lld-cold-rebuild-drills.md** continuously, one drill right after its paired chapter (Session 3 of that chapter's study contract, below, is a natural slot), plus the five cumulative drills at the Ch4/9/10/14/20 checkpoints.
- Read **lld-boundaries-and-testing.md** after Chapters 11 and 20, then use its checklist on one worked problem: identify policy, ports, adapters, error contracts, and the test at each boundary.
- **The drills workbook has no solutions, anywhere, on purpose.** Grade yourself against each drill's acceptance checks and rubric instead of looking for an answer key — an answer key would turn retrieval practice back into transcription.

Neither companion changes the 20-chapter, ~58-day estimate below — they ride alongside it, not on top of it.

## Study contract — do not skip

Each chapter is designed for **3 mini-sessions, NOT one sitting:**

**Session 1 (45–60 min):**
Read the chapter once. Do the inline "try it" prompts in your Python REPL as you go. Don't take notes. Don't move to Session 2 the same day.

**Session 2 (45–60 min, next day):**
Open a *new* empty file. From memory, rebuild the code the chapter ended with. No peeking. When stuck, peek at the *minimum* needed, close again, continue. Diff against the chapter. Note 2–3 things that slipped.

**Session 3 (30 min, day after):**
Do the end-of-chapter exercises. Then explain the chapter to yourself in 4–5 sentences: what was the problem, what was the pain, what was the move, what's the next pain. Only after this, move to the next chapter.

Total: ~2.5 hours per chapter, over 3 days. 20 chapters → ~58 days of focused work. Don't compress.

## Checkpoints

Every 4 chapters, stop and assess:

- **After Ch4:** Can you design a brand-new tiny system with a class + Strategy from scratch?
- **After Ch9:** Can you take a plain requirements blurb, find the classes, and decide each relationship as is-a (inherit) or has-a (compose)?
- **After Ch10:** Can you look at a new problem and predict which 2–3 patterns it needs?
- **After Ch14:** Can you do the full interview ritual on an unfamiliar problem in 30 minutes?
- **After Ch20:** Can you tell when the crux is a data structure or a concurrency lock rather than a pattern — and still name the patterns you held in reserve?

If a checkpoint fails, **stop and redo the previous chapters.** Don't proceed.

## The bumper sticker

> *Patterns are about whether your code bends or breaks when a new requirement lands.*

Not maintenance. Not organization. Response to change. That's the whole game.

---

<div align="right">

[Chapter 1 →](lld-chapter-1.md)

</div>
