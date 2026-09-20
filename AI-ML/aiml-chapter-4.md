# Chapter 4: The classic toolbox

*[← Chapter 3](aiml-chapter-3.md) · [Contents](aiml-README.md)*

- [ ] **Mark as read**

Before neural networks ate the headlines, a handful of simpler models did — and still do — most of the world's real ML work. They're fast, they're interpretable, they need far less data, and for tabular problems (rows and columns, like a spreadsheet) they often *beat* deep learning. Knowing this toolbox matters for two reasons: it's what you'd actually reach for on a normal business problem, and interviewers use these models to test whether you understand *fit* — picking the right tool, not the fanciest one.

The guiding principle of this chapter is the track's principle applied to models: **start simple.** A simple model you understand beats a complex one you don't.

---

## Linear and logistic regression: the honest baseline

The simplest useful models draw a straight relationship between features and the answer. They're your *baseline* — the thing you build first to see if the problem is even tractable, and to have something to beat.

> 💡 **Concept notes — linear vs logistic regression**
> - **Linear regression** predicts a **number** by fitting a weighted line through the data: `price = w₁·sqft + w₂·bedrooms + ... + b`. It's regression (continuous output). Trained by gradient descent minimizing squared error (Chapter 3).
> - **Logistic regression** predicts a **probability** for **classification**, despite the name. It computes the same weighted sum, then squashes it through a function (the *sigmoid*) into a 0–1 probability. "70% spam" → classify as spam. It's the default first model for yes/no problems.
> Both are **linear models**: they assume the answer is roughly a weighted sum of the features. Their superpower is **interpretability** — each weight tells you how much each feature pushes the answer, which matters enormously when you must *explain* a decision (loans, medicine, hiring).

Why start here: linear models train in milliseconds, need little data, rarely overfit badly, and give you a number to beat. If a giant neural network can't beat logistic regression on your problem, the network isn't earning its complexity.

---

## Decision trees: asking yes/no questions

A **decision tree** learns a flowchart of yes/no questions that funnel an input to an answer. "Is income > $50k? → yes → is age > 30? → no → ..." It mirrors how humans actually reason, which makes it intuitive and easy to explain.

> 💡 **Concept notes — decision trees**
> A **decision tree** splits the data by asking the most informative question at each step, recursively, until it reaches a prediction at the leaves. It handles both classification and regression, needs no feature scaling, captures non-linear patterns and feature interactions naturally, and you can *read* the tree to see exactly why it decided. Downside: a single deep tree **overfits** easily — it'll grow a branch to memorize every training quirk. Which leads directly to the most important practical models...

> 💡 **Concept notes — random forests and gradient boosting (the workhorses)**
> Combining many trees fixes the overfitting and produces some of the best models for tabular data:
> - **Random forest:** train *many* trees, each on a random slice of the data/features, and average their votes. The randomness makes their errors cancel out. Robust, hard to misuse, a fantastic default.
> - **Gradient boosting** (XGBoost, LightGBM): train trees in *sequence*, each one fixing the previous ones' mistakes. Often the **best-performing** approach on tabular/structured data — these win a large share of real-world ML competitions on spreadsheet-like data.
> The headline most beginners miss: **for tabular data, tree ensembles usually beat deep learning.** Deep learning's dominance is in images, text, and audio — not your typical business CSV. Saying "for this tabular problem I'd start with gradient boosting, not a neural network" is a strong, knowledgeable signal.

> 💡 **Concept notes — ensembles**
> An **ensemble** combines many models so their individual errors cancel, producing a stronger whole. Random forests and gradient boosting are ensembles of trees. The intuition: a crowd of diverse, decent predictors outperforms a single brilliant-but-quirky one.

---

## k-Nearest Neighbors: just look at similar examples

The most intuitive model of all barely "learns" — it just *remembers* the training data and answers new questions by finding the most similar past examples.

> 💡 **Concept notes — k-Nearest Neighbors (kNN)**
> **kNN** classifies a new point by looking at its **k** closest training examples (by some distance measure) and taking a majority vote (or average, for regression). "What were the 5 most similar houses' prices? Average them." No real training step — it stores everything and does the work at prediction time (a *lazy* learner). Simple and surprisingly effective for small datasets, but slow and memory-hungry at scale, and it degrades when there are many features. Its real importance for *this* track: it's the seed of how modern AI search works — embeddings + nearest-neighbor lookup is the engine behind semantic search and RAG (Chapters 7 and 11). "Find the most similar things" is a bigger idea than it looks.

---

## How to actually pick

You don't memorize a model; you match it to the situation. A rough field guide:

| Situation | Reach for |
|---|---|
| Need a fast, explainable baseline | Logistic / linear regression |
| Tabular data, want best accuracy | Gradient boosting (XGBoost/LightGBM) |
| Tabular, want robust + low-effort | Random forest |
| Must explain every decision | Linear model or a shallow single tree |
| Small dataset, "find similar" framing | kNN |
| Images, text, audio, huge data | Neural networks (Chapters 6–8) |

> 💡 **Concept notes — Occam's razor for models**
> Always try the simple model first. It sets a baseline, it's easier to debug, it ships faster, and often it's *good enough* — in which case you've saved yourself enormous complexity. Only climb the ladder of sophistication when the simpler rung demonstrably isn't enough. Reaching for a neural network on a 500-row spreadsheet is a beginner tell; reaching for logistic regression first and *earning* your way up is a practitioner tell.

---

## Try it

1. You must predict house prices and *explain to a regulator* how each prediction is made. Which model, and why does interpretability point you there?
2. You have a 200,000-row spreadsheet of customer features and want the highest churn-prediction accuracy. What's your first serious model, and why not a deep neural network?
3. Explain why a single deep decision tree overfits, and how a random forest fixes it.
4. For kNN, what happens to prediction speed as your training set grows to millions of rows? Why is that its weakness?
5. Someone proposes a 12-layer neural network for a 300-row dataset. What's your objection, and what would you try first?


---

## The bumper sticker

> *Most real ML runs on simple tools: linear/logistic regression for an honest baseline, tree ensembles for tabular wins, kNN for "find similar." Start simple, earn your way up, and remember — for spreadsheets, boosting usually beats deep learning.*

Next: how you actually know if any of these models *works* — the metrics, and the trap of trusting accuracy.

---

<div align="right">

[Chapter 5 →](aiml-chapter-5.md)

</div>
