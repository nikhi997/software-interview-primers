# Software Interview Primers — LLD · HLD · DSA · Behavioural · AI/ML · Foundations · Interview-Topics

Seven companion primers that prepare you for the full software engineering interview loop — *and* for where the loop is going — all written in the same conversational style.

They share one teaching philosophy: **start with the simple, obvious thing, feel exactly where it hurts, then add the one move that fixes the pain.** No memorized templates, no patterns for their own sake — you *derive* each technique from the problem it solves, which is what lets you recognize it on something unfamiliar.

New here? Read the [Preface](PREFACE.md) first — why these exist, who they're for, and the attitude to read them with.

```
.
├── LLD/          Low-Level Design  — classes, objects, design patterns, SOLID
│   ├── lld-README.md          start here for LLD
│   ├── lld-chapter-1.md … lld-chapter-20.md
│   ├── lld-appendix.md
│   ├── lld-code-evolution.md       companion: one system, twenty requirement waves
│   ├── lld-cold-rebuild-drills.md  companion: solution-free rebuild drills
│   └── code/                  runnable Python (ch6.py, ch7.py, …)
│
├── HLD/          High-Level Design — scaling, distributed systems, architecture
│   ├── hld-README.md          start here for HLD
│   ├── hld-chapter-1.md … hld-chapter-16.md
│   ├── hld-appendix.md
│   ├── hld-visual-deepdive.md      companion: all 16 chapters as one diagram-led story
│   └── code/                  runnable Python (consistent_hashing, rate_limiter, estimate)
│
├── DSA/          Data Structures & Algorithms — the coding round
│   ├── dsa-README.md          start here for DSA
│   ├── dsa-chapter-1.md … dsa-chapter-15.md
│   ├── dsa-appendix.md
│   ├── dsa-waste-map.md            companion: naive → tempting patch → optimization ledger
│   ├── dsa-mixed-cold-drills.md    companion: unlabelled timed drill packets
│   └── code/                  runnable Python (sliding_window, binary_search_answer, dynamic_programming)
│
├── Behavioural/  Behavioural — the "tell me about a time" round
│   ├── behavioural-README.md  start here for Behavioural
│   ├── chapter-01/ … chapter-10/   chapters + try-it worksheets
│   ├── behavioural-appendix.md
│   ├── behavioural-signal-router.md  companion: question → hidden signal → which story
│   └── behavioural-mock-deck.md      companion: timed mocks with follow-up trees
│
├── AI-ML/        AI & Machine Learning — the future-proofing track
│   ├── aiml-README.md         start here for AI/ML
│   ├── aiml-chapter-1.md … aiml-chapter-18.md
│   ├── aiml-appendix.md
│   ├── aiml-model-to-product.md    companion: one product traced across 18 chapters
│   ├── aiml-rebuild-labs.md        companion: fixture-first Session 2 labs
│   └── code/                  runnable Python (gradient_descent, embeddings_similarity, rag_retrieval)
│
├── Foundations/  CS Fundamentals — SQL, databases, OS, networking (the pop-quiz round)
│   ├── foundations-README.md  start here for Foundations
│   ├── 1-sql-and-databases/ … 5-bonus/   chapters, grouped by domain
│   ├── foundations-appendix.md
│   ├── foundations-mechanism-maps.md   companion: causal flow maps per domain
│   ├── foundations-60-second-recall.md companion: timed spoken answer skeletons
│   └── code/                  runnable Python (sql_demo, stdlib sqlite3)
│
└── Interview-Topics/  Named tech — Java, Spring Boot, Postgres, Kafka, Redis, cloud (the "have you used X?" layer)
    ├── interview-topics-README.md  start here for Interview-Topics
    ├── interview-topics-chapter-1.md … interview-topics-chapter-9.md
    ├── interview-topics-appendix.md
    ├── interview-topics-stack-map.md     companion: one request across the whole stack
    └── interview-topics-honest-pivots.md companion: scored gap-bridging drills
```

## Companions

Each track ships **companion files** alongside its chapters. They are not extra chapters and they teach nothing new — they exist for the *second* pass, when you're rebuilding from memory rather than reading for the first time.

The role split is the same everywhere: **chapters teach**, the **appendix is lookup**, and the **companions make you produce something** — a diagram, code, a decision, a spoken answer.

| Track | Companion | What it makes you do |
|---|---|---|
| HLD | [Visual deepdive](HLD/hld-visual-deepdive.md) | Redraw an architecture that grows one move at a time |
| LLD | [Code evolution](LLD/lld-code-evolution.md) · [Cold rebuild drills](LLD/lld-cold-rebuild-drills.md) | Watch one system bend through 20 requirement waves; then rebuild cold |
| DSA | [Waste map](DSA/dsa-waste-map.md) · [Mixed cold drills](DSA/dsa-mixed-cold-drills.md) | Name the waste, try the tempting patch, then solve unlabelled problems on a clock |
| Behavioural | [Signal router](Behavioural/behavioural-signal-router.md) · [Mock deck](Behavioural/behavioural-mock-deck.md) | Hear the hidden signal, pick a story, survive the follow-ups |
| AI/ML | [Model to product](AI-ML/aiml-model-to-product.md) · [Rebuild labs](AI-ML/aiml-rebuild-labs.md) | Trace one product through every chapter; cause the failures yourself |
| Foundations | [Mechanism maps](Foundations/foundations-mechanism-maps.md) · [60-second recall](Foundations/foundations-60-second-recall.md) | Follow the causal chain; then say it out loud, on a timer |
| Interview-Topics | [Stack map](Interview-Topics/interview-topics-stack-map.md) · [Honest pivots](Interview-Topics/interview-topics-honest-pivots.md) | Trace one request across every named tool; rehearse bridging a gap honestly |

Read a track's chapters first. The companions are worth little until you have something to reconstruct.

## The seven tracks

| | **LLD** | **HLD** | **DSA** | **Behavioural** | **AI/ML** | **Foundations** | **Interview-Topics** |
|---|---|---|---|---|---|---|---|
| Question it answers | *Does your **code** bend or break when a requirement lands?* | *Does your **system** bend or break when the traffic lands?* | *Can you turn the slow obvious solution into a fast one?* | *Will a team **want** to work with you?* | *Can you build with AI without treating it as magic?* | *Do you know what's happening one level below where you code?* | *Do you know the named tools a JD lists — and the concepts beneath them?* |
| Core principle | Feel the pain before naming the pattern | Feel the bottleneck before reaching for the component | Feel the brute force before reaching for the pattern | Hear the signal before telling the story | Feel the data before reaching for the model | Feel the mechanism before trusting the abstraction | Feel the concept beneath the brand name |
| Unit of thought | Classes, responsibilities | Servers, data stores, network | Patterns over arrays, trees, graphs | Stories, signals | Data, models, LLMs | Queries, threads, packets | Named technologies (Spring, Kafka, Redis…) |
| Interview round | "Design the classes for X" (45 min) | "Design X at scale" (45 min) | "Solve this on the whiteboard" (45 min) | "Tell me about a time..." (45 min) | "Design an AI feature / explain a concept" (45 min) | "Pop-quiz: what's an index? TCP or UDP?" (rapid-fire) | "Have you used Kafka / Redis / Spring?" (woven through screens) |
| Length | 20 ch + appendix | 16 ch + appendix | 15 ch + appendix | 10 ch + appendix | 18 ch + appendix | 14 ch + appendix | 9 ch + appendix |
| Start here | [LLD/lld-README.md](LLD/lld-README.md) | [HLD/hld-README.md](HLD/hld-README.md) | [DSA/dsa-README.md](DSA/dsa-README.md) | [Behavioural/behavioural-README.md](Behavioural/behavioural-README.md) | [AI-ML/aiml-README.md](AI-ML/aiml-README.md) | [Foundations/foundations-README.md](Foundations/foundations-README.md) | [Interview-Topics/interview-topics-README.md](Interview-Topics/interview-topics-README.md) |

The first four are the classic loop: almost every software interview is some mix of a coding round (DSA), one or two design rounds (LLD and/or HLD), and a behavioural round. **AI/ML** is the future-proofing track — the one the market is increasingly adding as "AI Engineer" becomes a mainstream title and ordinary postings start listing "experience integrating LLMs." **Foundations** is the breadth track: the rapid-fire CS fundamentals (SQL, databases, OS, networking) that surface as screening questions and woven into other rounds — a "pick the chapters your role needs" reference rather than a strict read-through. **Interview-Topics** is the named-technology layer: the brands a JD lists by name (Java, Spring Boot, Postgres, Kafka, Redis, GCP) and the "have you used X?" questions, each pointing down to the concept tracks for the *why*. Prepare them all and very little can surprise you.

## The one shared idea

Read the six core principles in the table again — they're the same sentence six times. *Understand what's actually being asked before you reach for the answer.* In code, that's the brute force before the pattern. In systems, the bottleneck before the component. In classes, the pain before the pattern. In the behavioural room, the hidden signal before the story. In AI, the data before the model. In fundamentals, the mechanism before the abstraction. And with named technologies, the concept beneath the brand. The habit transfers; that's why these belong together.

## Which one first?

- **Coding interview soonest?** Start **DSA** — it's the most common first filter and the one that needs the most *volume* of practice, so begin the reps early.
- **New to design?** Do **LLD before HLD.** It builds the "respond to change" reflex on small, runnable code, then HLD applies the same reflex at system scale.
- **Already comfortable with OOP/patterns, targeting senior/system rounds?** Go straight to **HLD** — it only assumes client/server/database basics.
- **Behavioural** can run *in parallel* with any of the above from day one — building your story bank is slow-burn work that benefits from being started early and revisited.
- **Targeting an AI Engineer / ML role, or expecting AI questions in your loop?** Add **AI/ML**. It's largely independent of the other four (it only assumes the DSA primer's level of Python), so it can run alongside them — but if AI is central to your target role, give it primary focus rather than treating it as a side track.
- **Expecting a fundamentals screen, or a backend/infra/data role?** Skim **Foundations**. It's a reference, not a sequence — drill SQL (Ch 1–4) for almost any role, add OS (Ch 5–6) for systems/infra/FAANG, and networking (Ch 7–8) for infra/platform work. Each chapter is recall-focused and shorter (~1.5–2 hrs) than the other tracks.
- **Best results:** DSA reps continuously in the background, LLD → HLD in sequence for design, Behavioural built up alongside, AI/ML layered in when the role calls for it, and Foundations skimmed for the fundamentals screen.

## How to study (read this before starting)

All seven tracks share one non-negotiable rule: **each chapter is a few short sessions over a few days, not one sitting.** The spacing *is* the method — it's what moves things into long-term memory.

- **Session 1 (45–60 min):** read once, do the inline "try it" prompts. Don't take notes. Stop for the day.
- **Session 2 (45–60 min, next day):** rebuild from memory — and what "rebuild" means is track-specific:
  - **LLD:** re-type the code; **HLD:** redraw the architecture and say *why each box exists*.
  - **DSA:** *solve* 2–3 listed problems for the pattern from scratch (DSA is the one track where solving beats reading).
  - **Behavioural:** *write out* 2–3 of your own stories in the template, then say them aloud.
  - **AI/ML:** run and modify the fixture-based examples; deliberately cause the failure the chapter describes, then repair it.
  - **Foundations:** close the file and *write each concept's answer from memory*, then *say it aloud* in four beats — this track is tested by speaking, so rehearse by speaking.
- **Session 3 (30 min, day after):** do the exercises, then explain the chapter to yourself in 4–5 sentences (the problem, the pain, the move, the next pain).

≈2.5 hours per chapter. Don't compress.

---

## The bumper stickers

> **LLD:** *Patterns are about whether your code bends or breaks when a new requirement lands.*

> **HLD:** *Architecture is the set of moves you make so the system bends instead of breaks when the traffic lands.*

> **DSA:** *A pattern is just the thing that deletes the specific waste in your brute force. Find the waste, and the pattern names itself.*

> **Behavioural:** *Every question is reading a hidden signal. Tell the story that delivers the signal they're scoring — your actions, your numbers, at the center.*

> **AI/ML:** *Machine learning is learning a function from data instead of writing it by hand — so feel the data before reaching for the model, and an LLM stops being magic and becomes a component you can engineer.*

> **Foundations:** *Every pop-quiz question asks whether you know what's happening one level below where you normally code. Feel the mechanism — what the database does with your query, what the OS does with your thread, what TCP does with your bytes — and no pop quiz can catch you out.*

Seven tracks, one habit: understand what's actually being asked before you reach for the answer. That's the whole game.

---

## Further reading and attribution

This collection teaches standard software-engineering ideas in its own examples and
structure. Chapter 12 of the LLD track is informed by the code-craft vocabulary
popularized by Robert C. Martin's *Clean Code*, Martin Fowler's
[*Refactoring*](https://refactoring.com/), and David Thomas and Andrew Hunt's
[*The Pragmatic Programmer*](https://pragprog.com/titles/tpp20/the-pragmatic-programmer-20th-anniversary-edition/).
Named company interview frameworks link to their public sources where they appear.

The collection was developed with AI assistance and then selected, edited, and reviewed
by the maintainer. AI assistance does not remove the maintainer's responsibility for
accuracy, attribution, or third-party rights.

## License

Unless a file says otherwise:

- Prose, diagrams, and other documentation are licensed under
  [Creative Commons Attribution 4.0 International](LICENSE-CC-BY-4.0).
- Python source files are licensed under the [MIT License](LICENSE-MIT).

Copyright © 2026 nikhi997.
