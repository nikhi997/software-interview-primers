# Software Interview Primers — LLD · HLD · DSA · Behavioural · AI/ML · Foundations · Interview-Topics

Seven companion primers that prepare you for the full software engineering interview loop — *and* for where the loop is going — all written in the same conversational style as Aditya Bhargava's *Grokking Algorithms* and Alex Xu's *System Design Interview*.

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
- **Best results:** DSA reps continuously in the background, LLD → HLD in sequence for design, Behavioural built up alongside, AI/ML layered in when the role calls for it, and Foundations skimmed for the fundamentals screen. The schedule below weaves them together.

## How to study (read this before starting)

All four primers share one non-negotiable rule: **each chapter is a few short sessions over a few days, not one sitting.** The spacing *is* the method — it's what moves things into long-term memory.

- **Session 1 (45–60 min):** read once, do the inline "try it" prompts. Don't take notes. Stop for the day.
- **Session 2 (45–60 min, next day):** rebuild from memory — and what "rebuild" means is track-specific:
  - **LLD:** re-type the code; **HLD:** redraw the architecture and say *why each box exists*.
  - **DSA:** *solve* 2–3 listed problems for the pattern from scratch (DSA is the one track where solving beats reading).
  - **Behavioural:** *write out* 2–3 of your own stories in the template, then say them aloud.
  - **AI/ML:** run/modify the chapter's code for the fundamentals, and for the GenAI chapters *actually call a real model API* — reading about hallucination teaches nothing; causing one teaches everything.
  - **Foundations:** close the file and *write each concept's answer from memory*, then *say it aloud* in four beats — this track is tested by speaking, so rehearse by speaking.
- **Session 3 (30 min, day after):** do the exercises, then explain the chapter to yourself in 4–5 sentences (the problem, the pain, the move, the next pain).

≈2.5 hours per chapter. Don't compress.

---

## The full study schedule

A realistic plan that weaves the tracks. DSA is 15 chapters, AI/ML is 18, HLD is 16, LLD is 20, Behavioural is 10, and Foundations is 14. Done sensibly with rest days, the classic four-track loop is about **3–4 months** — but you rarely need *all* tracks at full depth at once, so pick the option matching your situation. The AI/ML track is layered in via Option D (or run standalone) when the role calls for it; Foundations is skimmed as a reference whenever a fundamentals screen looms.

### Option A — Full loop, sequential (recommended; ~14–16 weeks)
DSA reps run *continuously in the background* the whole time. The weekly focus moves through the design and behavioural tracks.

| Weeks | Primary focus | DSA (ongoing) | Behavioural (slow burn) |
|---|---|---|---|
| **1–2** | DSA Ch 1–5 (array/string patterns) | — (this *is* the focus) | Read Behavioural Ch 1–3, start the story bank |
| **3–4** | DSA Ch 6–10 (structures) | grind listed problems | Write 4–6 stories |
| **5–6** | DSA Ch 11–15 (graphs, DP, ritual) | grind listed problems | Behavioural Ch 4–7, tag stories by signal |
| **7–8** | LLD Ch 1–8 | 3–5 problems/week to retain | Behavioural Ch 8–10, first mock |
| **9** | LLD Ch 9–20 | maintenance reps | Coverage-matrix check |
| **10–11** | HLD Ch 1–9 | maintenance reps | Refine bank, run mocks |
| **12** | HLD Ch 10–16 | maintenance reps | Final mock with follow-ups |
| **13+** | Mixed drills: one DSA problem + one design ritual + one behavioural question, daily | — | — |

### Option B — Design-focused (already strong at DSA; ~8 weeks)
Skip the DSA deep-dive (keep light maintenance reps), focus on the design and behavioural rounds.

| Weeks | Focus | Milestone |
|---|---|---|
| **1–2** | LLD Ch 1–8 | Predict which 2–3 patterns a new problem needs |
| **3** | LLD Ch 9–20 | Full LLD ritual on an unseen problem in 30 min |
| **4–5** | HLD Ch 1–9 | Justify each component from a *number*, not habit |
| **6** | HLD Ch 10–16 | Full HLD 6-step ritual on an unseen problem in 35 min |
| **7** | Behavioural Ch 1–7 + build the story bank | 6+ written stories, every signal covered twice |
| **8** | Behavioural Ch 8–10 + mocks | Cold question → story → STAR in under 3 min |

### Option C — Crunch (interview in 2–3 weeks)
Only if you've seen this material before and need a fast refresh. You lose the spacing benefit — expect shallower retention. Triage to the rounds you'll actually face.

- **Days 1–6:** DSA — read Ch 1–15 once, and *solve* the appendix's top 2–3 problems per pattern (the solving is non-negotiable even in crunch).
- **Days 7–9:** LLD Ch 1–20 (read once, attempt the worked problems cold).
- **Days 10–12:** HLD Ch 1–16 (read once, run the 6-step ritual out loud, timed).
- **Days 13–14:** Behavioural — read all chapters, write your bank (8–12 stories), rehearse out loud with follow-ups.
- **Days 15+:** daily mixed drill — one DSA problem, one design ritual, three behavioural questions — until the interview.

### Option D — AI/ML focus (targeting an AI Engineer / ML role; ~6–8 weeks)
For when AI is central to the role. Runs largely independently; keep light DSA reps in the background since AI roles still include a coding round.

| Weeks | Focus | Milestone |
|---|---|---|
| **1–2** | AI/ML Ch 1–5 (ML fundamentals) | Decide if a problem is ML, name the data + model class + metric — *and* when ML is the wrong tool |
| **3** | AI/ML Ch 6–8 (deep learning, embeddings, Transformers) | Explain an embedding and why Transformers made LLMs possible, no hand-waving |
| **4–5** | AI/ML Ch 9–16 (the GenAI applied layer) | Build a small RAG app + an eval set; *call a real model API* each chapter |
| **6** | AI/ML Ch 17–18 + appendix projects | Run the DRESS ritual on "design an AI feature" cold; aim at a role archetype |
| **alongside** | Light DSA maintenance reps + Behavioural story bank | Ready for the coding + behavioural rounds AI loops still include |

### Weekly rhythm (any option)
- **5 study days** + **1 review day** (redo a past chapter's exercises / re-solve a hard problem cold) + **1 rest day.** Rest is part of the method.
- At every **checkpoint**, if you can't do the milestone, *stop and redo* the prior chapters. Don't proceed on a shaky foundation.
- **DSA is volume-driven:** the 15 chapters teach the patterns, but fluency comes from the appendix's problem list. Budget steady reps over 2–3 months alongside everything else.

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
