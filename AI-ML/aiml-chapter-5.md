# Chapter 5: Knowing if it works

*[← Chapter 4](aiml-chapter-4.md) · [Contents](aiml-README.md)*

- [ ] **Mark as read**

You've trained a model. It says it's "95% accurate." Ship it? **Not yet** — because that single number can hide a model that's useless or even dangerous. Knowing whether a model actually works, and choosing a metric that matches what you truly care about, is one of the highest-leverage skills in ML, and one interviewers lean on hard. This chapter closes Part 1 with the discipline that ties the data and the model together: honest evaluation.

The principle here: **the metric must match the goal.** Optimize the wrong number and you'll build a model that's excellent at the wrong thing.

---

## Why accuracy lies

**Accuracy** is the fraction of predictions you got right. It feels like the obvious metric — and it's a trap whenever the classes are imbalanced.

Recall the fraud example from Chapter 2: 99.8% of transactions are legitimate. A model that predicts "legitimate" for *everything* — catching zero fraud — scores **99.8% accuracy**. It's worthless, and accuracy calls it nearly perfect. Whenever one class is rare (fraud, disease, churn — usually the very thing you care about), accuracy is misleading. You need metrics that look at the *kinds* of mistakes.

---

## The confusion matrix: four kinds of outcome

Every classification prediction lands in one of four buckets, and naming them unlocks every other metric.

> 💡 **Concept notes — the confusion matrix**
> For a yes/no classifier, each prediction is one of:
> - **True Positive (TP):** predicted yes, actually yes. ✅ (caught the fraud)
> - **True Negative (TN):** predicted no, actually no. ✅ (cleared a clean transaction)
> - **False Positive (FP):** predicted yes, actually no. ❌ (flagged a legit transaction — a *false alarm*)
> - **False Negative (FN):** predicted no, actually yes. ❌ (*missed* a real fraud)
> The key insight: **the two errors are not equal.** A false positive (annoy a customer) and a false negative (let fraud through) have wildly different costs, and which one you fear more determines which metric you optimize. Confusing the two types of error, or treating them as equally bad, is a classic mistake.

---

## Precision and recall: the two questions

From those four buckets come the two most important classification metrics. They answer different questions, and they trade off against each other.

> 💡 **Concept notes — precision and recall**
> - **Precision** = of everything I flagged as positive, what fraction *was* positive? `TP / (TP + FP)`. "When I raise the alarm, how often am I right?" High precision = few false alarms. **You want high precision when false positives are costly** (e.g., flagging a transaction blocks a real customer's card).
> - **Recall** (sensitivity) = of all the *actual* positives, what fraction did I catch? `TP / (TP + FN)`. "Of all the real fraud, how much did I catch?" High recall = few misses. **You want high recall when false negatives are costly** (e.g., missing a cancer diagnosis, or letting fraud through).
> The crucial part: **they trade off.** Flag more aggressively → catch more real positives (recall up) but also more false alarms (precision down). Flag conservatively → the reverse. There's a dial, and where you set it is a *business* decision, not a math one.

> 💡 **Concept notes — F1 and the threshold**
> - **F1 score** is the harmonic mean of precision and recall — one number that's high only when *both* are decent. Useful when you want a single balanced metric, but don't let it hide a deliberate lean toward one side.
> - Most classifiers output a **probability**; you choose a **threshold** (e.g., "flag if > 0.5") to turn it into a yes/no. *Moving the threshold slides you along the precision/recall tradeoff* without retraining. Lower the threshold → higher recall, lower precision. This is a knob you tune to the business cost of each error type.

---

## ROC, AUC, and ranking quality

Sometimes you want to judge a model *independent* of any single threshold — how well does it *rank* positives above negatives overall?

> 💡 **Concept notes — ROC curve and AUC**
> The **ROC curve** plots the tradeoff between catching positives and raising false alarms across *all* thresholds. The **AUC** (area under that curve) summarizes it as one number from 0.5 (useless, no better than coin flip) to 1.0 (perfect ranking). AUC roughly answers: "if I pick a random positive and a random negative, how often does the model score the positive higher?" It's a good threshold-independent measure of a classifier's overall discriminative power — popular precisely because it doesn't depend on where you set the threshold. (For heavily imbalanced data, the *precision-recall* curve is often more informative than ROC.)

---

## Measuring regression

For models that predict a *number*, the metrics measure how far off you are, on average.

> 💡 **Concept notes — regression metrics**
> - **MAE (mean absolute error):** average absolute difference. "On average, off by $12,000." Easy to interpret, in the units you care about.
> - **RMSE (root mean squared error):** like MAE but squares errors first, so it **punishes large misses harder**. Use it when big errors are especially bad.
> - **R²:** fraction of the variation in the target the model explains, 0 to 1. "0.85" ≈ the model captures 85% of what drives the outcome. A quick "is this model meaningful at all" gauge.
> Pick MAE when all errors hurt proportionally; pick RMSE when occasional large errors are unacceptable. The metric encodes what you punish.

---

## Don't trust one split: cross-validation

A single train/test split can be lucky or unlucky — maybe the test set happened to be easy. **Cross-validation** gives a more trustworthy estimate.

> 💡 **Concept notes — k-fold cross-validation**
> Split the data into **k** equal parts (folds). Train on k−1 of them, test on the held-out one, and *rotate* so every fold gets a turn as the test set. Average the k scores. This uses all your data for both training and testing (at different times) and tells you not just the average performance but how *stable* it is — a model whose score swings wildly across folds is fragile. Especially valuable when data is limited. (Note: the final **test set** from Chapter 2 still stays in the vault; cross-validation happens within train/validation.)

---

## The skill that ties it together: match the metric to the goal

This is the real lesson of the chapter and a senior-level signal. Before optimizing *anything*, ask: **what does being wrong actually cost, and in which direction?**

> 💡 **Concept notes — metric-goal alignment**
> - Cancer screening → **recall** matters most (missing a case is catastrophic; a false alarm just means another test).
> - Spam filter → **precision** matters most (a false positive sends a real, maybe important email to the spam folder).
> - Recommendations → ranking quality near the top of the list, not raw accuracy.
> - Imbalanced anything → never report accuracy alone; use precision/recall/F1/AUC.
> The failure mode: optimizing a convenient metric (accuracy) that doesn't reflect the real cost of errors, and shipping a model that's "great" on paper and harmful in practice. Always be able to say *why* you chose your metric in terms of what the wrong answers cost the business or the user.

---

## Checkpoint — end of Part 1

You now have the entire foundation of machine learning:
- **Ch 1:** ML learns a function from data instead of you writing it.
- **Ch 2:** the data, not the model, is the real lever — split it, guard against leakage.
- **Ch 3:** training = minimize loss via gradient descent, balancing overfitting and underfitting.
- **Ch 4:** the classic toolbox — start simple; tree ensembles win on tabular data.
- **Ch 5:** evaluate honestly; match the metric to the cost of being wrong.

If you can explain those five ideas to a friend without notes, you understand more ML than most people who can name twenty algorithms. Part 2 builds on this to reach neural networks, embeddings, and the architecture behind modern AI.

---

## Try it

1. A model predicts "no disease" for everyone and scores 97% accuracy because the disease is rare. What metric exposes how bad it is, and what would that metric score?
2. For a spam filter, is a false positive or a false negative worse? Which metric do you optimize, and why?
3. You move your classification threshold from 0.5 down to 0.3. What happens to precision and recall, and when would you do this deliberately?
4. Explain to a non-technical manager what AUC = 0.9 means.
5. You're predicting delivery time and occasional huge errors infuriate customers. MAE or RMSE — and why?
6. Why is 5-fold cross-validation more trustworthy than a single train/test split?


---

## The bumper sticker

> *A single accuracy number hides which mistakes a model makes — and the two mistakes rarely cost the same. Pick the metric that matches what being wrong actually costs, and evaluate on data the model never saw.*

Next, Part 2 opens the deep-learning era: neural networks, built up from a single artificial neuron.

---

<div align="right">

[Chapter 6 →](aiml-chapter-6.md)

</div>
