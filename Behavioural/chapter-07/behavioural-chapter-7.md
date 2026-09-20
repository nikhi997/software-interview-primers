# Chapter 7: Ambiguity, prioritization, and deadlines

*[← Chapter 6](../chapter-06/behavioural-chapter-6.md) · [Contents](../behavioural-README.md)*

- [ ] **Mark as read**

Junior engineers want a clear ticket: well-defined inputs, expected output, acceptance criteria. Senior engineers get handed a vague goal — "figure out why users are churning" or "make checkout faster" — with no spec, conflicting opinions, and a deadline. The behavioural round probes which of those two you are, because the gap between them is most of what "seniority" means.

This family — ambiguity, prioritization, competing demands, deadline pressure — screens for whether you can **make confident progress without complete information.** It's the family that most directly predicts how you'll perform on real, messy work.

---

## The signal behind the question

Variants: *"A time you worked with unclear requirements / had to make a decision without all the information / juggled competing priorities / dealt with a tight deadline / had to say no or cut scope."*

> 💡 **Concept notes — what ambiguity questions actually score**
> (1) **Bias for action under uncertainty** — do you freeze waiting for clarity, or do you make reasonable assumptions and move, adjusting as you learn? (2) **Structured thinking** — do you break a fuzzy problem into tackleable pieces, or flail? (3) **Judgment in prioritization** — when you can't do everything, do you choose based on *impact*, and can you justify the choice? (4) **Communication under pressure** — do you keep stakeholders informed and renegotiate scope honestly, or go quiet and miss the deadline silently? The worst signal here is paralysis: someone who needs everything specified before they can start does not scale.

---

## The core move: progress despite uncertainty

The trait being measured is a *bias for action* — but a *thoughtful* one, not recklessness. The pattern that signals it:

1. **Make the ambiguity explicit** — name what's unclear instead of pretending it's clear.
2. **Reduce it cheaply where you can** — ask the few highest-value clarifying questions, talk to a user, look at data. You don't need *all* the information, just enough.
3. **Make explicit assumptions** — state "I'm going to assume X; if that's wrong we'll revisit," and *write them down* so they're visible and correctable.
4. **Start with the smallest thing that creates learning** — a prototype, a spike, a slice that tests the riskiest assumption.
5. **Adjust as reality comes in** — iterate rather than committing fully to a guess.

> 💡 **Concept notes — assumptions are how you turn ambiguity into action**
> The key insight engineers miss: you don't resolve ambiguity by *waiting* for it to resolve — you resolve it by making **explicit, stated assumptions** and proceeding, then correcting. "We didn't know which segment was churning, so I assumed it was new users based on the funnel data, built a quick analysis for that segment, and was ready to pivot if the numbers said otherwise" signals exactly the right thing: you moved, but reversibly and transparently. Compare "I couldn't really start because the requirements weren't clear" — that's the failing answer. Making assumptions *visible* is what makes acting on them safe.

---

## Prioritization: choosing by impact

The prioritization variant ("too many things, not enough time — how did you choose?") wants to see that you optimize for **impact**, not for whatever's easiest or loudest.

> 💡 **Concept notes — how to talk about prioritization**
> Show an explicit basis for your choices, not vibes. Strong frames: **impact vs effort** (do the high-impact, low-effort things first), **what's blocking others** (unblocking three teammates beats a solo task), **reversibility and risk** (do the risky, hard-to-reverse thing early when there's time to recover), **deadline-driven** (what *must* ship vs what's nice-to-have). And critically: show you **communicated the tradeoff** — "I told the PM we could hit the date with the core flow but the analytics dashboard would slip a week, and we agreed that was the right call." Prioritization isn't just choosing; it's choosing *and aligning stakeholders on the choice.*

---

## A worked example

*Question: "Tell me about a time you had to deliver under a tight deadline with unclear requirements."*

> **(S)** *We committed to a demo for a big prospective customer in two weeks, but the ask was vague — "show them the analytics features" — and half of those features didn't exist yet.* **(T)** *I was the engineer on point, and there was no way to build everything, so I had to figure out what to actually build and ship something compelling in time.* **(A)** *Rather than wait for a perfect spec, I spent the first half-day with the sales lead figuring out what this specific customer actually cared about — turned out it was two specific reports, not the whole suite. I wrote down that assumption and confirmed it with them. Then I prioritized ruthlessly: I built the two reports for real and faked the rest of the dashboard with static mockups, and I told the sales lead exactly which parts were live versus demo-only so no one over-promised. When I realized one report wouldn't be ready, I flagged it three days early so we could adjust the demo script instead of discovering it the morning of.* **(R)** *The demo landed — the customer signed — and because I'd been explicit about what was real, sales set accurate expectations. I learned that under a deadline, the most valuable early work is figuring out what you can *not* do.*

The signals are all there: reduced ambiguity cheaply (half-day with sales), explicit assumptions (confirmed the two reports), impact-based prioritization (real where it mattered, mocked elsewhere), and communication under pressure (flagged the slip early). No flailing, no silent miss.

---

## The deadline-pressure variant

*"A time you were going to miss a deadline"* specifically tests whether you handle slippage like an adult: **early, transparent communication and renegotiation** — not a silent miss or a death-march that burns the team.

> 💡 **Concept notes — the right way to handle a slipping deadline**
> The signal is: you saw it coming *early*, you *raised it* rather than hiding it, and you came with *options* not just a problem — "we can hit the date if we cut feature X, or slip three days for the full scope; here's my recommendation." The worst answers are "I just worked nights and weekends until it was done" (signals poor planning and that you'll burn out) and "we missed it" with no early warning (signals you let stakeholders get blindsided). Raising a slip early with options is a *strength* — it shows ownership and communication, which is why a story about a deadline you *almost* missed but managed well can score better than one you hit by heroics.

> 💡 **Concept notes — Brooks's Law (the senior signal on staffing a late project)**
> When a project is late, the instinct is "throw more people at it." **Brooks's Law** — from *The Mythical Man-Month* — says the opposite often happens: *adding people to a late software project makes it later.* New people need ramp-up (someone productive has to stop and onboard them), and more people means more communication paths, which grow roughly as the square of team size. So the team gets slower before it gets faster, and a deadline that's already close just slips further. Knowing this lets you give a sharper answer than "we added engineers": the mature move is usually to **cut scope, not add bodies** — renegotiate what ships, protect the few people who hold context, and only add help where the work genuinely splits into independent parallel pieces. Naming Brooks's Law in a deadline story signals you think about delivery like someone who's run one, not just coded on one.

---

## What sinks an ambiguity answer

- **Paralysis** — "I couldn't start until the requirements were clear." The exact opposite of the signal.
- **No structure** — the story is just "it was chaotic and somehow it worked out." Show *how* you imposed order.
- **Recklessness** — charging ahead with no assumptions stated, no stakeholder check. Bias for action ≠ cowboy.
- **Heroics as the solution** — "I worked 80-hour weeks." Signals bad planning, not resilience.
- **The silent miss** — a deadline blown with no early communication. The communication *is* the signal.
- **No prioritization basis** — "I just did everything." If you didn't have to choose, the question wasn't really answered.

---



## Try it

1. Recall a time you started something genuinely under-specified. What **explicit assumptions** did you make to get moving? If you can't name them, reconstruct what they must have been — that's the heart of the story.
2. Take a time you had too much to do. Write the *basis* on which you prioritized (impact? unblocking others? risk? deadline?). "I just worked hard" isn't a basis.
3. Find a deadline you nearly missed. Did you raise it early with options? If you handled it by heroics, that's a *weaker* story — do you have one where you renegotiated scope instead?
4. For your best ambiguity story, identify the cheapest thing you did to *reduce* the uncertainty (a question, a user conversation, a data pull, a spike). Make that beat explicit.
5. Recall a late project you were on. Did the response add people or cut scope? Using Brooks's Law, explain what the staffing change actually cost in ramp-up and communication — and what the sharper move would have been.

*Write your answers in [behavioural-chapter-7-tryit.md](behavioural-chapter-7-tryit.md).*

---

## The bumper sticker

> *Ambiguity questions screen for confident progress without complete information. Make the unknowns explicit, reduce them cheaply, state your assumptions out loud, and move — adjusting as you learn. Prioritize by impact, and when a deadline slips, raise it early with options. Paralysis and silent misses are the only real failures.*

That closes the question families. Part 3 turns to delivery — starting with the part candidates most underuse: the questions *you* get to ask.

---

<div align="right">

[Chapter 8 →](../chapter-08/behavioural-chapter-8.md)

</div>
