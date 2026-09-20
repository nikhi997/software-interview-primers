# Chapter 5: Failure, mistakes, and feedback

*[← Chapter 4](../chapter-04/behavioural-chapter-4.md) · [Contents](../behavioural-README.md)*

- [ ] **Mark as read**

"Tell me about your biggest failure" makes people panic, so they do one of two self-defeating things: they pick a fake failure that's secretly a brag ("I work too hard"), or they confess a real disaster and then just... sit in it, looking defeated. Both fail the question, because neither shows the thing it's actually screening for: **whether you learn.**

This family is not a trap to survive — it's the easiest place to score the *growth and self-awareness* signal, *if* you understand that the failure is just the setup. The learning is the answer.

---

## The signal behind the question

Variants: *"Your biggest failure / a mistake you made / a time you broke something / a project that didn't go well / a time you got critical feedback."*

> 💡 **Concept notes — what failure questions actually score**
> Three things, in order of importance: (1) **Self-awareness** — can you honestly identify a real shortcoming without deflecting blame? (2) **Growth** — what did you *change* as a result, and is there evidence it stuck? (3) **Accountability** — do you own your part, or does every "failure" turn out to be someone else's fault? The failure itself is almost irrelevant — it's the *arc from mistake to lesson to changed behavior* that scores. Interviewers are specifically screening *out* people who can't admit fault, because those people don't improve and are painful to work with.

---

## Why the fake failure backfires

"My biggest weakness is that I care too much / work too hard / am a perfectionist" is so common that interviewers hear it as *"I'm not self-aware enough to name a real flaw, or I don't trust you enough to be honest."* It signals the *opposite* of what the question wants. The same goes for failures that are humblebrags ("I took on too much because I'm so driven").

A *real* failure — a genuine mistake with real consequences that you genuinely own — is what builds trust. Counterintuitively, admitting a substantive failure makes you look *more* hireable, because it shows the security and honesty of someone who learns.

> 💡 **Concept notes — picking the right failure**
> Choose a failure that is: **real** (actual consequences), **yours** (you owned a meaningful part of it), **resolved** (you recovered or learned, so it doesn't end in disaster), and **safe** (not a catastrophic ethics/judgment red flag — don't confess you got someone fired through negligence). The sweet spot: a mistake serious enough to be credible, from which you visibly grew, that you can discuss without defensiveness. "I shipped a bug that caused an outage" is great; "I once committed fraud" is not; "I'm a perfectionist" is not a failure at all.

---

## The arc that scores: mistake → ownership → lesson → changed behavior

A strong failure story moves through four beats, and spends the *most* energy on the last two:

1. **The mistake** (brief) — what went wrong and the real consequence. Don't minimize it.
2. **Ownership** — your specific part, stated plainly, without deflecting. "I didn't test the edge case" not "the requirements were unclear."
3. **The recovery** — what you did *in the moment* to limit damage and fix it. (This itself signals competence under pressure.)
4. **The lasting lesson** — what you changed *going forward*, ideally with evidence it stuck.

> 💡 **Concept notes — the lesson must have teeth**
> A vague lesson ("I learned to be more careful") signals nothing. A concrete, behavioral change signals real growth: *"I instituted a pre-deploy checklist for the team," "I now always write the failure-path test first," "I started asking for the rollback plan before any migration."* The best evidence is that the change **prevented a recurrence** — "and we haven't had that class of outage since." The mistake earns its place in your bank only because of how specific and durable the lesson is.

---

## A worked example

*Question: "Tell me about a time you made a significant mistake."*

> **(S)** *Early in my second year, I was responsible for a database migration on a service used by the whole company.* **(T)** *I'd done smaller migrations before and felt confident, so I ran this one during the day without a tested rollback.* **(A)** *The migration locked a table I hadn't realized was hot, and writes started failing — we had about twenty minutes of partial downtime. The moment I saw the errors, I owned it in the incident channel immediately rather than trying to quietly fix it, pulled in a senior engineer, and we manually unblocked the writes and reverted. I wrote the postmortem myself and didn't soften my role in it.* **(R)** *We recovered in under half an hour with no data loss. The real outcome was what I changed: I wrote a migration runbook for the team requiring a tested rollback and an off-peak window for anything touching a hot table, and it became our standard. We haven't had a migration-caused outage since. I learned that confidence from small successes is exactly what makes you skip the safeguards on the big one.*

The mistake is real and owned (no blame deflected), the recovery shows composure (owned it publicly, pulled in help), and the lesson has teeth (a runbook that became standard and prevented recurrence). That arc scores the growth signal cleanly.

---

## The feedback variant

*"Tell me about critical feedback you received"* is the same signal from a different angle — it scores whether you can *hear* hard truths and act on them, not just whether you learn from your own mistakes.

> 💡 **Concept notes — handling the feedback question**
> The arc mirrors the failure arc: **the feedback** (something genuinely critical, not "they said I should speak up more in a good way"), **your initial reaction honestly** (it's fine to admit it stung — that's human and self-aware), **what you did with it** (the concrete change), and **the result** (you improved, the relationship/work got better). The trap is picking feedback that's secretly flattering. Pick feedback that was *hard to hear* — "a senior engineer told me my code reviews were so nitpicky they were demoralizing the team" — and show you took it seriously. The willingness to receive hard feedback gracefully is itself a strong collaboration signal.

---

## What sinks a failure answer

- **The non-failure** — perfectionism, working too hard, caring too much. Reads as evasion.
- **The blame deflection** — "the requirements were bad / my teammate dropped the ball / management..." Even if partly true, owning *your* part is the whole point.
- **No lesson, or a toothless one** — "I learned to be more careful." Useless.
- **Sitting in the disaster** — narrating the failure with no recovery and no growth. Leaves the interviewer worried.
- **The catastrophic red-flag failure** — something revealing terrible judgment or ethics. Pick a *recoverable* mistake.
- **Minimizing** — "it wasn't really a big deal." If it's not real, it doesn't show real growth.

---



## Try it

1. From your bank, pick a *real* failure you genuinely own. Write the consequence in one honest sentence — no softening, no "but it was actually fine."
2. State your specific part in it using "I," with zero blame deflection. If your story blames circumstances or others, you've picked the wrong story or the wrong framing.
3. Name the *concrete behavioral change* the failure produced. Is there evidence it stuck (prevented a recurrence, became a team practice)? If the lesson is vague, dig deeper.
4. Find a piece of genuinely hard feedback you've received and draft its arc: feedback → honest reaction → what you changed → result.

*Write your answers in [behavioural-chapter-5-tryit.md](behavioural-chapter-5-tryit.md).*

---

## The bumper sticker

> *Failure questions screen for whether you learn. Pick a real mistake you own, show the recovery, and spend your words on a lesson with teeth — a concrete change that stuck. Admitting a substantive failure makes you more hireable, not less.*

Next: the family where you get to shine — leadership, ownership, and initiative, especially the kind you show without any authority at all.

---

<div align="right">

[Chapter 6 →](../chapter-06/behavioural-chapter-6.md)

</div>
