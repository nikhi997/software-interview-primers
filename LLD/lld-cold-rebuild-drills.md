# Companion: Cold Rebuild Drills

*[Contents](lld-README.md) · [Appendix](lld-appendix.md)*

This is a workbook, not a lesson. The twenty chapters teach a move each; the [appendix](lld-appendix.md) looks a move up after you already know its name; the [code evolution companion](lld-code-evolution.md) shows all twenty moves living together in one system. This page does the fourth job: **retrieval practice**. You already read the chapter. Can you rebuild the shape of its idea, cold, in a domain the book never used, without anyone reminding you which pattern applies?

That last part is deliberate. Every drill below hides its target move's name. If a chapter taught you a named move and its drill said "implement that move," you wouldn't be practicing recognition — you'd just be transcribing. Real interviews and real tickets never announce the pattern either. The skill worth drilling is **feeling the pressure that a specific shape relieves**, before you've been told what the shape is called.

**How to use this workbook.** Do a drill *after* finishing its paired chapter, cold — no notes open, no rereading the chapter first. Set a timer to the target time. If you finish early, you probably reached for something heavier than needed; if you blow way past the target, that's useful data too — it tells you which move hasn't landed yet. Use the hints only in order, one at a time, only after you're genuinely stuck for a few minutes — each one costs you a little of the "cold" in "cold rebuild." The rubric at the end of each drill is for grading yourself honestly, not for peeking at before you start.

**No solutions are provided anywhere in this file, on purpose.** If you want to check your work, compare it against the acceptance checks and the rubric, or reread the paired chapter and see if your instinct matches its worked example. A workbook with answer keys stops being retrieval practice.

Five interleaved drills mix two or more chapters' ideas in one fresh domain, on purpose, so the chapter number stops being a hint. This mirrors real work: nobody hands you a ticket labeled with the move it needs.

None of this changes the 20-chapter, ~58-day study plan in the [README](lld-README.md) — treat each drill as the retrieval check for the chapter you just finished, not extra syllabus.

---

## Drill 1 — Recipe Box


**Build this.** A small script that logs recipes (name, ingredients, cook time) using module-level lists/dicts and plain functions only — `add_recipe(...)`, `recipes_under(minutes)`, `scale_recipe(name, factor)`. Get it working, then add one more requirement mid-way: track a *currently selected* recipe across two different functions that both need to read and update it.

**Forbidden shortcuts.** No classes, no closures capturing state, no external libraries. The point is to build this the "obvious" way and feel exactly where it strains — not to avoid the strain.

**Target time.** 20 minutes.

**Acceptance checks.**
- All three functions work correctly against a handful of test recipes.
- The "currently selected recipe" requirement is implemented using shared module state, not passed explicitly everywhere.
- You can point to the exact line where a function silently depends on a global being set by a *different* function first.

<details><summary>Hint 1</summary>
Don't fight the assignment — write it as badly as the requirements naturally push you to. The pain is the data point.
</details>
<details><summary>Hint 2</summary>
After it works, try adding a second "currently selected recipe" concept (e.g., for a second user). Notice how many places assume there's only ever one.
</details>

**Rubric.**
- *Model* — recipes are represented consistently (same shape every time), even without a class.
- *Invariant* — scaling never produces a negative or zero cook time.
- *Seam* — n/a this drill; there's deliberately no seam yet.
- *Flow* — you can trace, out loud, which function reads state that a different function wrote.
- *Explanation* — in 2–3 sentences, name the specific coupling that made the second requirement (second selected recipe) awkward.


<details><summary>Pairing metadata</summary>

Pairs with: [Chapter 1](lld-chapter-1.md)

</details>
---

## Drill 2 — Habit Tracker


**Build this.** Track daily habits: mark a habit done for today, compute its current streak (consecutive days done, ending today or yesterday), and list habits whose streak has broken. Fold everything into one cohesive unit that owns its own data — no module-level state.

**Forbidden shortcuts.** Don't reach for a database or file yet — in-memory only. Don't expose the internal data structure directly; callers should only ever go through named operations.

**Target time.** 20 minutes.

**Acceptance checks.**
- Marking a habit done twice in one day doesn't double-count it.
- Streak calculation is correct across a gap (missed day breaks the streak; today or yesterday still counts as "current").
- At least one internal helper is clearly separated from the public operations it supports.

<details><summary>Hint 1</summary>
Ask: what data does "compute streak" need that "mark done" also touches? That overlap is what belongs together.
</details>
<details><summary>Hint 2</summary>
If you find yourself passing the same three arguments into every function, that's the signal the enclosing unit should hold them instead.
</details>

**Rubric.**
- *Model* — one unit owns both the habit data and the operations on it; nothing external reaches in and mutates fields directly.
- *Invariant* — "done today" is idempotent — marking twice has the same effect as marking once.
- *Seam* — none required yet; note where one *could* go (e.g., how streaks are stored) without building it.
- *Flow* — trace marking a habit done, then immediately asking for its streak, end to end.
- *Explanation* — say in one sentence why grouping this data and these functions together removed a whole category of bug from Drill 1.


<details><summary>Pairing metadata</summary>

Pairs with: [Chapter 2](lld-chapter-2.md)

</details>
---

## Drill 3 — Weather Source Swap


**Build this.** A `WeatherReport` that answers "what's the temperature in this city right now?" but must work against at least two different backing sources with the same question-answering shape — a canned in-memory source (for tests) and a second source that simulates an external lookup (a dict of pre-baked responses is fine, keyed differently to force a real interface, not just a copy-paste). The report shouldn't know or care which source it's using.

**Forbidden shortcuts.** No `if source_type == "..."` branching inside `WeatherReport`. No inheriting from a shared base class if a shared method name is enough (duck typing is allowed and encouraged).

**Target time.** 20 minutes.

**Acceptance checks.**
- Swapping which source object gets passed in changes nothing about `WeatherReport`'s own code.
- Both sources expose the exact same method name and return shape.
- A third, hypothetical source could be added without touching `WeatherReport` at all.

<details><summary>Hint 1</summary>
Write the two sources first, on paper, before writing `WeatherReport`. What's the one method name both must share?
</details>
<details><summary>Hint 2</summary>
If `WeatherReport`'s constructor takes anything other than "a source object," that's a smell — it shouldn't know source-specific configuration.
</details>

**Rubric.**
- *Model* — `WeatherReport` and each source are separate classes with a clean boundary between them.
- *Invariant* — asking for a city not known to a source fails the same way (same exception type) regardless of which source is active.
- *Seam* — the constructor injection point is the seam; verify it's the *only* place source choice is decided.
- *Flow* — trace one lookup end-to-end through each of the two sources.
- *Explanation* — name the one method signature every source must implement, and why that specific shape (not a bigger one) is enough.


<details><summary>Pairing metadata</summary>

Pairs with: [Chapter 3](lld-chapter-3.md)

</details>
---

## Drill 4 — Password Strength Meter


**Build this.** Score a password's strength using a chosen rule — "length-based" (longer is better, thresholds for weak/medium/strong) or "character-variety-based" (counts distinct character classes present). The caller picks which rule applies at construction time; you're not told these two rules should share a shape — notice that on your own.

**Forbidden shortcuts.** Don't write one function with an internal `if rule == "length"` branch. If you catch yourself writing that branch, stop and restructure before continuing.

**Target time.** 20 minutes.

**Acceptance checks.**
- Both rules expose the identical method name/signature for "score this password."
- Swapping rules requires zero changes to whatever calls the scorer.
- You noticed, unprompted, that this is the same shape as a previous drill — write one sentence naming which one.

<details><summary>Hint 1</summary>
You've solved this exact *shape* of problem already, in an earlier drill, in a different domain. Which one?
</details>
<details><summary>Hint 2</summary>
The lesson this time isn't building the shape from scratch — it's noticing you already know it before you start typing.
</details>

**Rubric.**
- *Model* — two rule classes, one shared method name, zero conditional branching on rule identity anywhere in caller code.
- *Invariant* — every rule returns a score from the same fixed set of buckets (e.g., weak/medium/strong), never a rule-specific label.
- *Seam* — the point where a rule object is chosen and handed to the scorer.
- *Flow* — trace scoring the same password under both rules and confirm they can disagree without either being "wrong."
- *Explanation* — name the earlier drill that used this same shape, and what was different about the *reason* it was needed there versus here.


<details><summary>Pairing metadata</summary>

Pairs with: [Chapter 4](lld-chapter-4.md)

</details>
---

## Cumulative Drill A — Grocery List Keeper


**Build this.** One cohesive unit that manages a shopping list (add item with quantity, remove item, total estimated cost) *and* supports swapping how items get sorted for display — alphabetical, by aisle number, or by estimated cost — chosen by whoever creates the list.

**Forbidden shortcuts.** No global state (that's the earlier lesson, already behind you). No sort-type string branching inside the list-keeper itself.

**Target time.** 40 minutes.

**Acceptance checks.**
- The list-keeper owns its own items; nothing external mutates them directly.
- At least two sort orders are implemented behind one shared method name.
- Adding a third sort order requires a new small class, not an edit to the list-keeper.

<details><summary>Hint 1</summary>
Two separate concerns are stacked here: "own the data" and "decide an order." Don't let one class do both jobs by accident.
</details>
<details><summary>Hint 2</summary>
The list-keeper should hold a sort-order object the same way Drill 3's report held a source object — as something handed in, not chosen internally.
</details>
<details><summary>Hint 3</summary>
If you're stuck on *where* the sort actually runs, it should be one line inside the list-keeper: delegate to the held object, don't reimplement the ordering logic there.
</details>

**Rubric.**
- *Model* — clean separation between "the list" (state + operations) and "the ordering rule" (swappable behavior).
- *Invariant* — the same set of items is present regardless of which sort order is active — sorting never drops or duplicates items.
- *Seam* — the constructor (or a setter) is the one place a sort-order object enters the list-keeper.
- *Flow* — trace adding three items and switching sort orders twice, confirming the underlying data never changes.
- *Explanation* — say which chapter's idea supplied "own your own state" and which supplied "make the behavior swappable," and why neither alone was enough here.


<details><summary>Pairing metadata</summary>

Interleaves: [Chapter 2](lld-chapter-2.md) + [Chapters 3–4](lld-chapter-4.md)

</details>
---

## Drill 5 — Smart Thermostat


**Build this.** A thermostat that, whenever its temperature reading changes, needs to: update a display string, append a line to a history log, and — only if the change crosses a configured alert threshold — trigger an alert. Different deployments want different combinations of these three reactions turned on.

**Forbidden shortcuts.** Don't hardcode all three reactions as sequential calls inside the temperature-setting method. The thermostat itself shouldn't know how many reactions exist or what they do.

**Target time.** 20 minutes.

**Acceptance checks.**
- Adding a fourth reaction (e.g., a counter of total readings) requires no change to the thermostat's own method bodies.
- Removing the alert reaction removes only that one reaction — the other two still fire.
- The thermostat's temperature-setting method is one clear action plus one clear announcement, not three tangled ones.

<details><summary>Hint 1</summary>
The thermostat's job is to say "something happened" — not to know or care who's listening or how many.
</details>
<details><summary>Hint 2</summary>
Each reaction should have the same method name/signature so the thermostat can treat all of them identically, in a loop.
</details>

**Rubric.**
- *Model* — thermostat holds a collection of reaction objects, not a fixed sequence of calls.
- *Invariant* — every registered reaction sees every temperature change — none are silently skipped.
- *Seam* — the subscribe/register point, where reactions are attached to the thermostat.
- *Flow* — trace one temperature change firing all three (or however many are registered) reactions in turn.
- *Explanation* — explain why the alert reaction's own threshold check belongs inside the alert reaction, not inside the thermostat.


<details><summary>Pairing metadata</summary>

Pairs with: [Chapter 5](lld-chapter-5.md)

</details>
---

## Drill 6 — Print Spooler


**Build this.** Given a config dict describing a printer ("inkjet", "laser", or "thermal-receipt"), produce the right driver object without the caller ever naming a concrete class. Separately: the spooler wants exactly one shared job-counter across the whole app, since job IDs must never collide. Build both, and write one sentence on what could go wrong with the second one if you're not careful.

**Forbidden shortcuts.** Don't let the config-based construction leak concrete class names to the caller. Don't skip building the shared counter the tempting-but-risky way — build it, then critique it in writing.

**Target time.** 20 minutes.

**Acceptance checks.**
- A caller only ever writes `create_driver(config)` — never `InkjetDriver()` directly.
- Adding a fourth printer type is a small addition, not a change to caller code.
- Your written critique names the specific failure mode of the shared-counter approach you chose (silent argument ignoring, hidden test coupling, or similar).

<details><summary>Hint 1</summary>
The config-to-object problem and the "exactly one" problem are two *different* problems, even though they can look similar at first glance. Don't solve them with the same trick.
</details>
<details><summary>Hint 2</summary>
Build the shared counter using whichever mechanism enforces "only one instance" most directly, then try constructing it twice with different starting values and see what happens on the second call.
</details>

**Rubric.**
- *Model* — one small function or method maps config to the correct concrete driver; the "only one counter" mechanism is a separate, clearly distinct piece of code.
- *Invariant* — every driver produced by the config function exposes the identical print method signature.
- *Seam* — the single function that all callers go through to obtain a driver.
- *Flow* — trace a config dict through to a working driver for at least two printer types.
- *Explanation* — name, precisely, what happens if two different parts of the app construct the "shared" counter expecting two different starting values.


<details><summary>Pairing metadata</summary>

Pairs with: [Chapter 6](lld-chapter-6.md)

</details>
---

## Drill 7 — Elevator Door Controller


**Build this.** An elevator door that can be Closed, Opening, Open, Closing, or Obstructed. Valid actions: `open()`, `close()`, `obstruction_detected()`, `obstruction_cleared()`. Closing while something is in the way must switch to Obstructed and reopen, not just fail. Attempting to close an already-closed door should be a no-op or a clear rejection — your call, but be consistent.

**Forbidden shortcuts.** No single `status` string checked with a long `if/elif` ladder scattered across all four action methods. Each door status's own rules for "what happens on each action" should live together, not be scattered by action.

**Target time.** 20 minutes.

**Acceptance checks.**
- Every illegal transition (e.g., `open()` while already `Opening`) either raises clearly or is explicitly defined as a no-op — never silently corrupts status.
- `obstruction_detected()` during `Closing` always results in `Obstructed`, then reopens.
- Adding a new status (e.g., `EmergencyStop`) touches one new small unit, not four existing methods.

<details><summary>Hint 1</summary>
Group by status, not by action — ask "what can happen while the door is Closing?" rather than "what does close() do?"
</details>
<details><summary>Hint 2</summary>
Each status-unit needs the same set of method names as every other one, even if most of them just reject the action for that particular status.
</details>

**Rubric.**
- *Model* — one small unit per door status, each implementing the same action method names.
- *Invariant* — the door is never in an undefined or contradictory status after any sequence of actions.
- *Seam* — the single place that swaps "current status" from one unit to another.
- *Flow* — trace `close()` → obstruction detected mid-close → reopens → clears → closes successfully.
- *Explanation* — explain why scattering these rules by action (rather than by status) would have made the obstruction-during-closing rule harder to find.


<details><summary>Pairing metadata</summary>

Pairs with: [Chapter 7](lld-chapter-7.md)

</details>
---

## Drill 8 — Terminal Text Renderer


**Build this.** Render plain text to a terminal-style string, then layer on: bold markers, a color code, and a timestamp prefix — in any combination, chosen per call site, without a giant parameter list on one render function.

**Forbidden shortcuts.** No `render(text, bold=False, color=None, timestamp=False)` mega-function with internal branching. Each enhancement should be its own small wrapper with the exact same "render this" method shape as the plain renderer.

**Target time.** 20 minutes.

**Acceptance checks.**
- Any subset and order of the three enhancements can be composed by nesting wrappers, without editing any existing wrapper.
- The plain renderer has zero knowledge that bold/color/timestamp wrapping exists.
- A caller holding a fully-wrapped renderer can call the exact same method name they'd call on the plain one.

<details><summary>Hint 1</summary>
Each wrapper should hold "the thing it wraps" and expose the same one method the wrapped thing exposes — then do its own small addition before or after delegating.
</details>
<details><summary>Hint 2</summary>
Try wrapping in a different order (timestamp-then-color vs. color-then-timestamp) and notice the output actually changes — that's expected, and worth naming.
</details>

**Rubric.**
- *Model* — every wrapper and the plain renderer share one method signature; wrappers hold a reference to what they wrap.
- *Invariant* — wrapping never changes what a *plain* render would have produced underneath — only adds around it.
- *Seam* — the shared method name every layer must implement identically.
- *Flow* — trace a call through three stacked wrappers down to the plain renderer and back up.
- *Explanation* — say in one sentence why the wrapping order changed the output, and whether that's a bug or expected.


<details><summary>Pairing metadata</summary>

Pairs with: [Chapter 8](lld-chapter-8.md)

</details>
---

## Drill 9 — Animal Shelter Roster


**Build this.** Model a shelter roster with at least two kinds of animals (say, Dog and Cat) that share common fields (name, age, intake date) but differ in one real behavior (a dog's `daily_care_summary()` mentions walks; a cat's mentions litter box cleaning). Animals live inside Kennels, which have a capacity. Decide, and justify, whether "kennel" should be a base class an animal inherits from, or something an animal simply belongs to.

**Forbidden shortcuts.** Don't make every animal the same class with an `animal_type` string field checked everywhere. Don't inherit `Kennel` behavior into `Animal` if a kennel is really just something an animal is housed in.

**Target time.** 40 minutes.

**Acceptance checks.**
- `Dog` and `Cat` both fulfill one shared contract (same base, same required method names) with different implementations of at least one method.
- A `Kennel` holds animals without any animal needing to know it's "a kennel-kind-of-thing" itself.
- You can state, in one sentence each, why the animal hierarchy is is-a and why kennel-membership is has-a.

<details><summary>Hint 1</summary>
Ask of each relationship: "is a Dog fundamentally a kind of X, permanently and totally?" versus "does a Dog merely have or belong to an X?"
</details>
<details><summary>Hint 2</summary>
If you're tempted to make an abstract base class that's never instantiated directly, that's usually a sign you've found a genuine is-a relationship — check whether that's true here.
</details>

**Rubric.**
- *Model* — a shared animal base/contract, two concrete subclasses, and kennel membership modeled as composition, not inheritance.
- *Invariant* — every concrete animal type fulfills the full shared contract — no subclass silently missing a required method.
- *Seam* — n/a directly; note instead where a *new* animal type would plug in.
- *Flow* — trace listing every animal in a kennel and calling each one's care summary polymorphically, without checking type first.
- *Explanation* — write the one-line is-a justification and the one-line has-a justification explicitly.


<details><summary>Pairing metadata</summary>

Pairs with: [Chapter 9](lld-chapter-9.md)

</details>
---

## Cumulative Drill B — Greenhouse Controller


**Build this.** Model a greenhouse with different plant types (say, Herb and Succulent) that share a contract but respond differently to a `needs_watering()` check based on their own thresholds. Whenever a moisture sensor reading is recorded, several things should react — updating a display, logging the reading, and (only for plants that report needing water) triggering a watering-due list.

**Forbidden shortcuts.** Don't check plant type by name anywhere outside each plant class's own method. Don't hardcode the reactions to a moisture reading as a fixed sequence of calls.

**Target time.** 40 minutes.

**Acceptance checks.**
- Plant types share one contract; each implements its own watering threshold logic.
- Recording a moisture reading fans out to an open-ended, registerable set of reactions.
- Adding a third plant type or a fourth reaction requires no edits to existing plant classes or existing reactions.

<details><summary>Hint 1</summary>
These are two separate ideas stacked in one domain — "different plants respond differently" is one; "a reading triggers several reactions" is the other. Solve them independently, then combine.
</details>
<details><summary>Hint 2</summary>
The reading-recorder doesn't need to know which plants exist — it announces "reading recorded," and something else (a reaction, or a loop over plants) decides what that means.
</details>
<details><summary>Hint 3</summary>
If your "watering-due list" reaction needs to know about every plant, it's fine for it to loop over them and call the shared `needs_watering()` method — that's the polymorphism doing the work, not the reaction hardcoding rules per plant.
</details>

**Rubric.**
- *Model* — a plant contract with two+ concrete types, and a separate, open-ended reaction list for sensor readings.
- *Invariant* — every registered reaction fires on every reading; every plant's watering decision uses only its own thresholds.
- *Seam* — both the plant-contract extension point and the reaction-registration point exist and are distinct from each other.
- *Flow* — trace one moisture reading through all reactions, and one `needs_watering()` check through both plant types.
- *Explanation* — name which chapter's idea handles "many things react to one event" and which handles "many kinds of the same underlying thing," and why this domain needed both at once.


<details><summary>Pairing metadata</summary>

Interleaves: [Chapter 5](lld-chapter-5.md) + [Chapter 9](lld-chapter-9.md)

</details>
---

## Drill 10 — Coworking Space Booker


**Build this.** A coworking space has Floors, each with Desks and Meeting Rooms. Booking a desk charges an hourly rate that varies by desk tier (standard vs. window-view); booking a meeting room charges a flat rate regardless of duration. When a booking is made, someone waiting on a notification list for that resource should be told it's now taken. Model the whole thing, using whichever ideas from chapters 1–9 actually earn their place here — and explicitly leave out any that don't.

**Forbidden shortcuts.** Don't build a full set of per-status lifecycle rules for "is a desk booked" if a simple boolean plus a booking record genuinely suffices — prove to yourself it does (or doesn't) before deciding. Don't skip splitting the pricing calculation by tier just because it feels like "too many classes" for two rate types.

**Target time.** 40 minutes.

**Acceptance checks.**
- Desk pricing and meeting-room pricing are two implementations of one shared "price this booking" contract.
- Booking a resource notifies an open-ended set of interested listeners.
- You can name, in writing, one pattern-shaped idea you deliberately did *not* use here, and why it wasn't needed.

<details><summary>Hint 1</summary>
Start from the nouns: Floor, Desk, Meeting Room, Booking. Decide has-a relationships before reaching for any swappable-behavior idea.
</details>
<details><summary>Hint 2</summary>
Only two behaviors vary here (pricing, and "who gets told") — resist inventing more variation points than the requirements actually contain.
</details>

**Rubric.**
- *Model* — clean composition (Floor has Desks and Rooms) plus exactly the variation points the requirements demand, no more.
- *Invariant* — a resource can't be booked twice without the second booking either failing or explicitly queuing — pick one and enforce it.
- *Seam* — the pricing contract and the notification-registration point.
- *Flow* — trace booking a window-view desk end to end, including the notification fan-out.
- *Explanation* — the one thing you deliberately didn't build, and the specific requirement that would have to change before it'd be worth adding.


<details><summary>Pairing metadata</summary>

Pairs with: [Chapter 10](lld-chapter-10.md)

</details>
---

## Cumulative Drill C — Airport Gate Board


**Build this.** An airport gate board tracks Gates, each showing one Flight at a time. A flight has a lifecycle (Scheduled → Boarding → Closed → Departed, with a Delayed detour reachable from Scheduled or Boarding). Assigning a flight to a gate should pick from a swappable rule (nearest-to-checkpoint, or first-available). Whenever a flight's status changes, the physical display board and an airline ops log should both update. Model gates, flights, and their assignment as a small cohesive system — resist building anything the requirements above don't actually ask for.

**Forbidden shortcuts.** No status-string `if/elif` ladders for the flight lifecycle. No hardcoded sequence of "update the board, then log it" inside the status-change method. No premature abstraction for things this domain doesn't need (e.g., don't build a full plugin system for gates — there's no requirement asking for that).

**Target time.** 60 minutes.

**Acceptance checks.**
- Flight status transitions are each defined in one place per status, and illegal transitions are rejected clearly (e.g., Departed can't go back to Boarding).
- Gate assignment rule is swappable without touching the gate board's own code.
- A status change fans out to an open-ended set of reactions (board display, ops log, and a third one you add yourself to prove it's easy).
- You can name at least one idea from chapters 1–10 you deliberately left out, and why.

<details><summary>Hint 1</summary>
Build this in the same order the chapters did: get the plain classes right first (Gate, Flight, has-a relationships), then find the one or two places that are actually asking for swappable behavior, then find the one place that's actually asking for a lifecycle.
</details>
<details><summary>Hint 2</summary>
"Delayed reachable from two different statuses" is exactly the kind of rule that belongs inside the lifecycle units themselves, not in a shared board-level conditional.
</details>
<details><summary>Hint 3</summary>
If assignment strategy and status-change reactions start to feel like the same mechanism, look closer — one is "pick one thing from a list," the other is "notify everyone interested." Different shapes, even though both are swappable/pluggable in spirit.
</details>

**Rubric.**
- *Model* — Gate/Flight composition, a flight-lifecycle unit per status, and a separate assignment-strategy family.
- *Invariant* — no flight is ever displayed on two gates at once; no illegal lifecycle transition ever succeeds silently.
- *Seam* — both the assignment-strategy injection point and the status-change reaction registration point.
- *Flow* — trace one flight from Scheduled through a delay, through boarding, to departure, including every board/log update along the way.
- *Explanation* — name every chapter 1–10 idea you used, in the order you reached for it, and the one you skipped.


<details><summary>Pairing metadata</summary>

Interleaves: [Chapters 1–10](lld-chapter-10.md)

</details>
---

## Drill 11 — Freight Quote Calculator


**Build this.** You're handed (write it yourself, deliberately smelly) a `FreightQuoteCalculator` class that: computes quotes for three shipping modes via internal string checks, directly reads and writes a global rates dictionary, and has a `calculate()` method that also logs, also validates the input, and also formats the final display string. Then audit it.

**Forbidden shortcuts.** Don't refactor while you audit — finish the audit first, in writing, findings only. Refactoring is a different drill.

**Target time.** 20 minutes.

**Acceptance checks.**
- Your audit names at least four distinct violations, each tied to a specific letter of the five-part design-quality checklist.
- For each violation, you name the concrete symptom (a specific method, a specific branch) — not a vague "this violates X."
- At least one finding explains what *adding a fourth shipping mode* would currently require, concretely.

<details><summary>Hint 1</summary>
Go letter by letter rather than reading the class once and hoping violations jump out — check each one deliberately.
</details>
<details><summary>Hint 2</summary>
"How many reasons does this class have to change?" is the fastest way into the first violation.
</details>

**Rubric.**
- *Model* — n/a; this drill produces a written audit, not a new model.
- *Invariant* — n/a.
- *Seam* — you correctly identify where a seam is *missing* (e.g., no injected rates source).
- *Flow* — you can trace, for one shipping mode, every side effect `calculate()` currently causes.
- *Explanation* — the audit itself: four-plus findings, each concrete, each tied to a specific principle.


<details><summary>Pairing metadata</summary>

Pairs with: [Chapter 11](lld-chapter-11.md)

</details>
---

## Drill 12 — Gym Billing Function


**Build this.** Write (deliberately smelly, on purpose) a `proc(m, d, t)`-style function that bills gym members: `m` is membership type (magic numbers 1/2/3 for basic/premium/family), `d` is days-since-joined, `t` is a trainer-session count, with a hardcoded discount threshold buried mid-function and a duplicated fee calculation appearing twice under two different branches. Then refactor it through the same small steps chapter 12 walks through, in order, and stop after each step to note what got clearer.

**Forbidden shortcuts.** Don't do one big rewrite — apply the steps one at a time, in the order the chapter teaches them, and keep the intermediate versions visible (comments or a numbered sequence of snippets).

**Target time.** 40 minutes.

**Acceptance checks.**
- Final version has zero magic numbers — every one is a named constant.
- The duplicated fee calculation is extracted once and called from both branches.
- Function and parameter names are whole words describing intent, not `m`/`d`/`t`.
- You wrote one sentence per refactoring step naming exactly what got clearer.

<details><summary>Hint 1</summary>
Rename first, before anything else — it's the lowest-risk step and it usually reveals what the *next* step should be.
</details>
<details><summary>Hint 2</summary>
The duplicated calculation under two branches is easiest to spot once the magic numbers are gone and the branches read in English.
</details>

**Rubric.**
- *Model* — n/a; grading is on the refactoring sequence and its outcome.
- *Invariant* — the refactored function produces identical output to the original for every input you started with — behavior-preserving, not behavior-changing.
- *Seam* — the extracted duplicated-calculation function is a small, clearly named seam.
- *Flow* — you can trace one member's bill through the original and the refactored version and get the same number both times.
- *Explanation* — one sentence per step, in order, naming what got clearer.


<details><summary>Pairing metadata</summary>

Pairs with: [Chapter 12](lld-chapter-12.md)

</details>
---

## Drill 13 — Photo Album App


**Build this.** No code this time. Given this description — "A `PhotoAlbum` contains many `Photo`s, but photos live in the user's media library and can be moved between albums; deleting an album removes the album record, not the underlying photos. Each `Photo` has an optional `Location` where it was taken. A `User` owns many `PhotoAlbum`s. A `SharedAlbum` is a kind of `PhotoAlbum` that also tracks a list of collaborator `User`s. Deleting a `User` should not delete `Photo`s that live only inside a `SharedAlbum` they collaborate on but don't own." — draw the class diagram by hand (ASCII is fine) including every relationship type this description actually implies, with correct multiplicities.

**Forbidden shortcuts.** Don't use one relationship type (like a generic arrow) for everything — the description implies at least three different relationship types; find and label each correctly.

**Target time.** 20 minutes.

**Acceptance checks.**
- `SharedAlbum`–`PhotoAlbum` is drawn as inheritance, not composition or association.
- `PhotoAlbum`–`Photo` is drawn as aggregation or association, not composition, because photos can outlive and move between albums; `SharedAlbum`–collaborator-`User` is also a weaker association/aggregation for the same lifecycle reason.
- `Photo`–`Location` is drawn with the correct optional (0..1) multiplicity.
- Every box has at minimum a name — full attribute/method lists aren't required for this drill.

<details><summary>Hint 1</summary>
Ask, for every pair of boxes: if one is deleted, does the other necessarily get deleted too? That question is how you tell composition from aggregation/association.
</details>
<details><summary>Hint 2</summary>
The last sentence of the prompt is a direct multiplicity/ownership clue — it's telling you which relationship must NOT be composition.
</details>

**Rubric.**
- *Model* — every relevant relationship type present and correctly labeled (inheritance, aggregation/association, with composition only if your own stated deletion semantics justify it).
- *Invariant* — multiplicities match the prose exactly (album has many photos; photo has 0..1 location; shared album has many collaborators).
- *Seam* — n/a for a diagram drill.
- *Flow* — you can narrate "delete this user" against the diagram and get the same answer the prose states.
- *Explanation* — one sentence justifying why `PhotoAlbum`–`Photo` is not composition under the given deletion semantics.


<details><summary>Pairing metadata</summary>

Pairs with: [Chapter 13](lld-chapter-13.md)

</details>
---

## Drill 14 — Gear Rental Marketplace


**Build this.** Run the full five-step ritual, cold, on this fresh prompt: "Design a peer-to-peer outdoor-gear rental marketplace — owners list gear (tents, kayaks, etc.) with daily rates and availability windows; renters book a gear item for a date range; a booking that overlaps an already-booked window must be rejected." Do all five steps, in order, on paper/in a doc — don't skip to code.

**Forbidden shortcuts.** Don't jump to a class diagram before writing down your clarifying questions and assumptions. Don't jump to code before the diagram. Each step should visibly build on the previous one.

**Target time.** 40 minutes.

**Acceptance checks.**
- Step 1 lists at least three real clarifying questions (e.g., can an owner also rent gear? what happens to a pending booking if the owner delists the item?) with your own reasonable assumption for each.
- Step 2's entity list matches step 3's diagram exactly — no entity appears in one but not the other.
- Step 4 walks one booking attempt end to end, including the overlap-rejection check as a real method call or named responsibility, not a comment saying "check overlap here."
- Step 5 names at least two concrete tradeoffs (not generic ones like "scalability") specific to this domain.

<details><summary>Hint 1</summary>
"What happens if two renters try to book the same overlapping window at the exact same moment?" is a legitimate clarifying question *and* a legitimate tradeoff for step 5 — notice it could belong to either step, and pick one deliberately.
</details>
<details><summary>Hint 2</summary>
Step 4 is a flow, not a code dump: it should still name the overlap-checking method the flow calls, and that method should have a real condition behind it in your sketch.
</details>

**Rubric.**
- *Model* — entities and diagram agree; the overlap-checking responsibility is concrete enough that the flow can call it.
- *Invariant* — no two accepted bookings for the same gear item can have overlapping date ranges.
- *Seam* — the overlap-check is isolated enough that swapping its algorithm later wouldn't touch booking-creation code.
- *Flow* — you can walk one full booking attempt through your own skeleton, narrating each call.
- *Explanation* — the two concrete tradeoffs from step 5, and why they're specific to this domain rather than generic.


<details><summary>Pairing metadata</summary>

Pairs with: [Chapter 14](lld-chapter-14.md)

</details>
---

## Cumulative Drill D — Fitness Membership Perks


**Build this.** Run the five-step ritual on this prompt, and let the entities/diagram surface which earlier ideas actually apply — don't decide in advance: "A fitness studio has three membership tiers (Basic, Plus, Elite) each unlocking a different discount on class bookings and a different monthly free-guest-pass count. A member books classes; a class has a capacity and a waitlist. Different studios want different guest-pass policies (flat count vs. one-per-tier-level-per-month), configurable without code changes to the booking flow."

**Forbidden shortcuts.** Don't pre-decide "this needs pattern X" before step 2's entity list is done. Let step 3's diagram reveal where has-a composition is enough and where a swappable-policy shape actually earns its place.

**Target time.** 40 minutes.

**Acceptance checks.**
- Step 1's clarifying questions surface the ambiguity in "different studios want different... policies" explicitly.
- The guest-pass policy variation is modeled as a swappable, injected policy object — not a per-tier `if` ladder inside the booking flow.
- Membership tiers are modeled the way step 2/3 actually justifies (as data carried by a tier object, or as classes — your call, defensible either way, but state which and why).
- Step 5 names the tradeoff of the policy being per-studio-configurable versus hardcoded per tier.

<details><summary>Hint 1</summary>
"Configurable without code changes to the booking flow" is the prompt handing you the same seam you built in Drill 3 and Drill 4 — recognize it, don't rebuild the reasoning from zero.
</details>
<details><summary>Hint 2</summary>
Ask whether a membership tier really needs its *own class with different behavior*, the way Drill 9's animals did — or whether it's closer to a plain data holder. The prompt doesn't force one answer; defend whichever you pick.
</details>

**Rubric.**
- *Model* — entities/diagram agreement, with the guest-pass policy modeled as an injected, swappable object.
- *Invariant* — the booking flow produces identical results whether guest-pass policy is flat-count or per-tier, given equivalent inputs.
- *Seam* — the exact point the policy object is chosen and handed to the booking flow.
- *Flow* — one full class-booking trace, including a guest-pass check, narrated against your own skeleton.
- *Explanation* — which earlier chapter's idea you recognized fastest in this prompt, and what specifically triggered the recognition.


<details><summary>Pairing metadata</summary>

Interleaves: [Chapter 14](lld-chapter-14.md)'s ritual + [Chapters 3–4, 9](lld-chapter-9.md)

</details>
---

## Drill 15 — Hotel Room Booker


**Build this.** A hotel has room tiers (Standard, Suite) each with different cancellation-notice requirements (Standard: 24 hours; Suite: 72 hours) and a different late-cancellation fee. A guest books a room for a date range; cancelling within the notice window charges the fee, outside it doesn't. Model tiers and bookings, choosing deliberately whether the booking's status needs its own rich set of per-status rules or whether a simpler status field is enough — and be ready to defend the choice either way.

**Forbidden shortcuts.** Don't build five separate status-handling classes by default "because that's what a booking system probably needs" — check whether the actual requirements (book, cancel-with-fee, cancel-without-fee) justify that much structure first.

**Target time.** 40 minutes.

**Acceptance checks.**
- Cancellation-fee logic differs correctly by tier without an `if tier == "suite"` check living inside the booking's own cancel method.
- Your stated status-modeling decision (state machine vs. simple field) has a one-sentence justification tied to the actual requirements, not a general preference.
- A new room tier (e.g., Penthouse, 7-day notice) can be added as a small new unit, not an edit to existing cancel logic.

<details><summary>Hint 1</summary>
Count the realistic statuses a booking passes through here. Is that count and their transition complexity closer to a vending machine's, or closer to something that just needs a boolean plus a timestamp?
</details>
<details><summary>Hint 2</summary>
The tier-specific fee-and-notice-window logic is exactly the same shape you've already built at least twice this workbook — under a different name each time.
</details>

**Rubric.**
- *Model* — tier-specific rules live on a small tier object/class, not in conditionals inside the booking.
- *Invariant* — a cancellation exactly at the notice-window boundary is handled consistently (pick and enforce one rule: boundary counts as "within" or "outside," not sometimes either).
- *Seam* — the point where a booking is given its tier's rules.
- *Flow* — trace booking a Suite, cancelling 80 hours before, then trace cancelling 10 hours before, and confirm the fee outcome differs correctly.
- *Explanation* — your state-machine-vs-simple-field justification, tied to the specific requirements given.


<details><summary>Pairing metadata</summary>

Pairs with: [Chapter 15](lld-chapter-15.md)

</details>
---

## Drill 16 — Courier Dispatch Network


**Build this.** Couriers deliver packages; pricing varies by method (bike-courier flat fee, van-courier per-kilometer) chosen per delivery request. Whenever a delivery's status changes (picked up, in transit, delivered), a customer-facing tracker display and an internal ops dashboard should both update. Separately, a scheduler publishes an elapsed-time tick for active deliveries every few minutes; a delayed-delivery alert should fire on that tick only if a delivery has been "in transit" longer than a configured threshold.

**Forbidden shortcuts.** Don't compute pricing with a method-name `if/elif` inside the dispatch class. Don't hardcode the tracker/dashboard/alert updates as a fixed three-line sequence — the alert in particular has a condition the other two don't.

**Target time.** 40 minutes.

**Acceptance checks.**
- Pricing methods share one contract; adding a third (e.g., drone) requires no dispatch-class edit.
- Every status change reaches an open-ended set of reactions; elapsed-time ticks reach the same reaction mechanism, so the delayed-alert reaction can evaluate "currently delayed" even when no status changed.
- You can swap one reaction out (say, silence the ops dashboard for test deliveries) without touching the other two.

<details><summary>Hint 1</summary>
This drill deliberately stacks two ideas you've each drilled solo already (Drill 3/4-style swappable pricing, Drill 5-style fan-out reactions) — solve them as two separate, small pieces, then wire them into one dispatch class.
</details>
<details><summary>Hint 2</summary>
The delayed-alert reaction needs both the timestamp from entering "in transit" and the current time from the scheduler tick. A status-change announcement alone can only say "became in transit," not "has now been in transit too long."
</details>

**Rubric.**
- *Model* — a pricing-method family (shared contract) plus a separate, open-ended reaction list for status changes.
- *Invariant* — every reaction sees every status change and every elapsed-time tick; pricing never depends on which reactions are currently registered.
- *Seam* — both the pricing-method injection point and the reaction-registration point.
- *Flow* — trace one delivery from request through pickup, transit, a scheduler tick that is not late yet, a later tick that is late, and delivered.
- *Explanation* — one sentence naming why the alert reaction's threshold logic must not live in the dispatch class.


<details><summary>Pairing metadata</summary>

Pairs with: [Chapter 16](lld-chapter-16.md)

</details>
---

## Drill 17 — Bike-Share Station Network


**Build this.** A bike rental has its own richer lifecycle: Reserved → Unlocked → InUse → Returned, with a Reserved rental that isn't unlocked within 10 minutes auto-cancelling. Separately, matching a rider's rental request to an actual bike varies by a swappable rule — nearest-station-first, or most-charged-battery-first (for e-bikes). Model both, deciding whether the rental lifecycle here is rich enough to earn its own full set of per-status rules (compare against Drill 15's decision, and be ready to say why this one is or isn't different).

**Forbidden shortcuts.** Don't skip the auto-cancel-on-timeout rule — it's an actual transition, not an edge case to hand-wave. Don't let the bike-matching rule's own logic leak into the rental lifecycle code.

**Target time.** 40 minutes.

**Acceptance checks.**
- The rental lifecycle correctly rejects `return_bike()` from `Reserved` (never unlocked yet) with a clear error, not a silent state change.
- Auto-cancel-on-timeout is modeled as a real transition, reachable only from `Reserved`.
- Matching strategies share one contract; swapping one for the other requires no rental-lifecycle changes.
- You directly compare this lifecycle's richness to Drill 15's and state which one justified a full state machine and why.

<details><summary>Hint 1</summary>
Count the transitions here versus Drill 15's hotel booking — four statuses plus a timeout-triggered detour is a meaningfully different shape than "booked, maybe cancelled."
</details>
<details><summary>Hint 2</summary>
The auto-cancel timeout isn't something a user calls — think about it as a transition that some external clock-check triggers, but it should still be implemented as a normal method on the Reserved status, just like every other transition.
</details>

**Rubric.**
- *Model* — a per-status unit for the rental lifecycle, and a separate matching-strategy family.
- *Invariant* — a rental can only ever be in exactly one status; the timeout-driven cancellation only fires from Reserved, never from any other status.
- *Seam* — the matching-strategy injection point, kept fully separate from the lifecycle's own transition methods.
- *Flow* — trace a full happy path (Reserved → Unlocked → InUse → Returned) and the timeout path (Reserved → auto-cancelled) separately.
- *Explanation* — the direct comparison to Drill 15: what made this lifecycle "richer enough" to justify the fuller machinery, in your own words.


<details><summary>Pairing metadata</summary>

Pairs with: [Chapter 17](lld-chapter-17.md)

</details>
---

## Drill 18 — Campus Print Center


**Build this.** Three separate needs on one print center: (1) only students with a paid printing-credit balance may submit a job — enforce this without the print center's core submission logic containing the balance check; (2) submitting a job today means calling three subsystems in sequence (reserve paper stock, queue the job, notify the student) — give callers one simple call instead; (3) an oversized job (200+ pages) should be offered to the express printer first, then the standard printer, then a staff-assisted manual queue, in that order, stopping at whichever accepts it first.

**Forbidden shortcuts.** Don't solve all three needs with the same wrapper shape — they're three different intents (should-this-call-happen-at-all, one-call-instead-of-many, who-eventually-handles-this-in-order) and conflating them is the exact mistake this drill is designed to catch.

**Target time.** 40 minutes.

**Acceptance checks.**
- The balance check happens *before* the real submission logic runs at all, for an unauthorized student — never after, never partially.
- The one-simple-call wrapper performs all three subsystem calls in the same order every time, and a caller never sees the three individual subsystems.
- The express → standard → manual-queue offering stops at the first acceptor and never asks a later option after an earlier one accepted.
- You can state, in one sentence each, why each of the three needs got a structurally different piece of code.

<details><summary>Hint 1</summary>
Ask of each need: "is this about permission, about simplifying a multi-step call, or about trying candidates in order until one works?" Each answer points at a differently-shaped small wrapper.
</details>
<details><summary>Hint 2</summary>
The third need's "in order until one accepts" shape should let you add a fourth fallback option later without touching the first three.
</details>

**Rubric.**
- *Model* — three structurally distinct wrapper shapes, each matched to its actual intent, none reused where it doesn't fit.
- *Invariant* — the balance-check wrapper never lets the real submission logic execute for an unauthorized student, under any call path.
- *Seam* — three distinct seams: the balance-check point, the one-call entry point, and the link between fallback options.
- *Flow* — trace an authorized 250-page job through balance-check, the one-call submission, and the express→standard→manual chain.
- *Explanation* — the three one-sentence justifications for why each need got a different shape.


<details><summary>Pairing metadata</summary>

Pairs with: [Chapter 18](lld-chapter-18.md)

</details>
---

## Drill 19 — ER Triage Board


**Build this.** An emergency room needs "who's the single most urgent waiting patient right now," in better than linear time, even as patients arrive constantly, get re-triaged (severity can change after a second look), or get called back and removed from waiting. No pattern is the answer here — this is a data-structure problem, feel that before reaching for anything object-oriented.

**Forbidden shortcuts.** Don't solve this with a sorted list you re-sort on every change — that's the naive rung, useful to feel first, but not the acceptance-check-passing answer. Don't skip the "re-triage changes an existing patient's urgency" requirement — it's the hard part.

**Target time.** 40 minutes.

**Acceptance checks.**
- Getting the most urgent patient is meaningfully faster than a full linear scan once the waiting list is reasonably large (demonstrate with a rough timing comparison against the naive version, or reason about it in Big-O terms if you'd rather not benchmark).
- Re-triaging a patient already in the structure never requires scanning the whole structure to find and fix their old entry.
- Removing a called-back patient is handled correctly even if their entry isn't at a position you can find in O(1).

<details><summary>Hint 1</summary>
Feel the naive version's actual cost first: build the plain linear-scan version, time it (or reason through it) against a few hundred simulated patients, and write down the specific number or complexity that hurts.
</details>
<details><summary>Hint 2</summary>
Two different questions are in tension: "always know the current most-urgent one, fast" wants one kind of structure; "find and update a specific patient, fast" wants a different one. You likely need both, working together.
</details>
<details><summary>Hint 3</summary>
If removing or re-triaging an arbitrary entry from your fast-urgency structure feels expensive or awkward to do directly, consider not doing it directly — mark the old entry as no-longer-valid instead, and let your "get the most urgent" operation skip past invalid entries when it encounters them.
</details>

**Rubric.**
- *Model* — two complementary structures working together (one for fast "most urgent" retrieval, one for fast "find this specific patient" lookup).
- *Invariant* — the most-urgent retrieval never returns a patient who has already been called back or whose severity is stale.
- *Seam* — n/a in the OOP sense; the "seam" here is the lazy-invalidation boundary — where a stale entry gets recognized and skipped.
- *Flow* — trace: patient arrives, a second patient re-triages more severe, most-urgent is requested, the first patient is called back, most-urgent is requested again.
- *Explanation* — name, in your own words, the specific cost the naive linear-scan version paid, and the specific cost your structure pays instead (don't claim you eliminated cost — name what it moved to).


<details><summary>Pairing metadata</summary>

Pairs with: [Chapter 19](lld-chapter-19.md)

</details>
---

## Drill 20 — Flash-Sale Checkout


**Build this.** A flash sale has exactly N units of one item. Many concurrent checkout attempts race to claim a unit. Exactly N of them should succeed; every attempt beyond N must fail cleanly, never oversell, never leave the count in an inconsistent state, and never let two different checkouts believe they got the *same* unit number.

**Forbidden shortcuts.** Don't just wrap the final decrement in a lock while leaving the "is there still stock" check outside it — that's the exact trap this chapter warns about. Don't test this with a single thread and call it done; you must actually race concurrent attempts against each other to prove it.

**Target time.** 40 minutes.

**Acceptance checks.**
- A stress test that starts many threads (or async tasks) at effectively the same instant, all attempting to claim, results in exactly N successes and the rest failing cleanly — run it enough times to trust it, not just once.
- The check ("is stock available") and the write ("decrement stock, assign a unit number") happen inside the same guarded critical section — not as two separate guarded (or worse, unguarded) steps.
- No two successful checkouts ever receive the same assigned unit number.

<details><summary>Hint 1</summary>
Use something that releases many waiting threads at exactly the same moment (rather than starting them one after another) to actually force the race — starting threads sequentially rarely reproduces the bug.
</details>
<details><summary>Hint 2</summary>
Write the buggy version on purpose first — lock only around the decrement, leave the availability check outside it — and prove to yourself it oversells under real concurrent load before fixing it.
</details>

**Rubric.**
- *Model* — one shared guarded resource (the stock count plus unit-number assignment) with a single, well-defined critical section.
- *Invariant* — total successful claims never exceeds N, under any interleaving, proven by an actual concurrent stress test, not just reasoning.
- *Seam* — the exact boundary of the critical section — everything between the availability check and the write must be inside it, nothing more, nothing less.
- *Flow* — trace two racing attempts through the critical section conceptually: one enters, checks, writes, exits; the other must wait for exactly that to finish before it can even check.
- *Explanation* — describe the buggy version you deliberately built first, and the precise interleaving that made it oversell.


<details><summary>Pairing metadata</summary>

Pairs with: [Chapter 20](lld-chapter-20.md)

</details>
---

## Cumulative Drill E — Emergency Supply Depot


**Build this.** A disaster-response supply depot allocates scarce items to field teams. Requirements, all at once: (1) supplies are modeled with at least two real kinds (medical cold-chain kits needing an expiry and temperature check before allocation; durable radio kits that don't); (2) requesting organizations have tiers (Local: 24-hour hold window; Critical-response: 7-day hold window) affecting hold length and replacement fee; (3) given many teams waiting for scarce supply types, the depot needs "who's next in line for this supply type" answerable fast, even as teams join or leave a waitlist constantly; (4) when two coordinators try to allocate the last available unit of the same supply type at the same moment, exactly one must succeed.

**Forbidden shortcuts.** Don't skip any of the four requirements — this drill is explicitly testing whether you can tell, unaided, which requirement wants which idea, with nothing labeling them for you. Don't force requirement 3 into an object-oriented pattern, and don't force requirement 4 into anything other than a guarded critical section around a check-then-write span.

**Target time.** 60 minutes.

**Acceptance checks.**
- Cold-chain kits and radio kits share a contract; only cold-chain kits implement real expiry/temperature checks.
- Organization tier affects hold length and replacement fee without a tier-name conditional living inside allocation logic.
- Waitlist "who's next" is answerable without a full linear scan, and correctly handles a team leaving the waitlist before its turn.
- A concurrent-allocation stress test on the last unit of one supply type produces exactly one success.
- You can state which chapter's idea addressed each of the four requirements, in your own words, without re-reading any chapter first.

<details><summary>Hint 1</summary>
Handle each of the four requirements as its own small, mostly-independent piece before worrying about how they fit together — the integration is the last step, not the first.
</details>
<details><summary>Hint 2</summary>
Requirement 3 and requirement 4 can look similar ("multiple things wanting one resource") but they're solving different problems — one is about ordering and fast lookup over time, the other is about an instant of true concurrency. Don't reach for the same mechanism for both.
</details>
<details><summary>Hint 3</summary>
If you're unsure whether requirement 3 needs the same lazy-invalidation trick as an earlier drill, ask: does a waitlisted team's position ever need to change based on something other than "they joined earlier"? If not, a plain ordered queue may be all requirement 3 needs — don't over-build.
</details>

**Rubric.**
- *Model* — a supply contract with two real kinds, tier objects carrying hold rules, a waitlist structure, and a guarded allocation critical section — four distinct, correctly-scoped pieces.
- *Invariant* — no supply type is ever allocated past its available unit count, under concurrent load; no waitlisted team is ever skipped or double-counted.
- *Seam* — at minimum: the supply-kind extension point, the tier-rules injection point, and the allocation critical-section boundary.
- *Flow* — trace one full scenario touching all four requirements: a Critical-response organization allocates the last available cold-chain kit while a Local team is waitlisted for the same supply type and a second Critical-response coordinator is racing to allocate that same last unit at the same instant.
- *Explanation* — the four-requirement-to-chapter-idea mapping, stated confidently and correctly, unaided.


<details><summary>Pairing metadata</summary>

Interleaves: [Chapters 9, 15–17](lld-chapter-17.md), [19](lld-chapter-19.md), and [20](lld-chapter-20.md) — a capstone

</details>
---

## Closing note

Twenty-five drills, twenty-five domains, and not one of them was the helpdesk from the [evolution companion](lld-code-evolution.md) or a book chapter's own example. That's the whole exercise: the pattern isn't in the domain, it's in the pressure. If you could feel the pressure here without being told its name, you'll feel it in whatever domain an actual interview or an actual ticket hands you next.

<div align="right">

[Code Evolution →](lld-code-evolution.md) · [Appendix](lld-appendix.md) · [Contents](lld-README.md)

</div>
