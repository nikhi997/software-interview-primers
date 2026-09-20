# Chapter 2: The data is the model

*[← Chapter 1](aiml-chapter-1.md) · [Contents](aiml-README.md)*

- [ ] **Mark as read**

Beginners obsess over the model — "should I use a neural network or a random forest?" Practitioners know a secret that the obsession hides: **the data matters far more than the model.** A simple model trained on clean, representative, leak-free data will crush a sophisticated model trained on garbage. Most real ML failures aren't modeling failures; they're *data* failures. This chapter is about developing the data-first instinct that the whole track is named for.

---

## Why the data dominates

The model can only learn the patterns that are *in the data.* If the data is biased, the model is biased. If the data has a leak, the model looks brilliant in testing and falls apart in production. If the data doesn't represent the real world the model will face, the model is confidently wrong. You cannot out-model bad data — and you'd be amazed how often a struggling project is fixed not by a fancier algorithm but by *looking at the data and finding the problem.*

> 💡 **Concept notes — "garbage in, garbage out," with teeth**
> The model is a mirror of its training data. It learns correlations present in the examples — *all* of them, including the ones you didn't intend. Train a résumé-screener on a decade of a company's hires and it learns that company's historical biases. Train an image classifier on photos that all happen to have grass behind the animal and it may learn "green background = cow." The model has no common sense to override the data; the data *is* its entire world. This is why the first thing a good ML engineer does with a new problem is not pick a model — it's *look at the data.*

---

## Features: what the model actually sees

A model doesn't see "an email" or "a house." It sees **features** — numbers (or things turned into numbers) that represent the input. Choosing and shaping these is **feature engineering**, and historically it was where most of the work (and the winning) happened.

> 💡 **Concept notes — features and feature engineering**
> A **feature** is one measurable input signal. For predicting house price: square footage, number of bedrooms, zip code, age. For an email: counts of certain words, number of links, sender reputation. **Feature engineering** is the craft of turning raw data into features that expose the pattern — e.g., from a raw timestamp you might derive "hour of day" and "is weekend," because *those* are what actually predict the target. In classic ML this craft is decisive. (A big part of deep learning's appeal, Chapter 6, is that it *learns* features automatically from raw data — but understanding the concept is still essential.)

A practical note: models need *numbers*. Categories ("city = Mumbai") get converted to numeric form (e.g., one-hot encoding); text becomes word counts or, better, embeddings (Chapter 7); images become pixel arrays. "Turn everything into numbers the model can work with" is half of data preparation.

---

## The split: train, validation, test

Here is the single most important discipline in all of ML, and the one beginners most often get wrong. You must **hold out data the model never sees during training**, so you can honestly measure whether it learned the real pattern or just memorized the examples.

> 💡 **Concept notes — the three splits and why each exists**
> You divide your labeled data into three disjoint sets:
> - **Training set** (~70–80%): the model learns from this.
> - **Validation set** (~10–15%): you use this to *tune* choices (which model, which settings) and check progress *during* development. The model doesn't train on it, but *you* peek at it to make decisions.
> - **Test set** (~10–15%): locked in a vault, touched **once**, at the very end, to get an honest final score. If you make decisions based on the test set, you've contaminated it — it's no longer a fair measure.
> The reason: a model's performance *on data it trained on* is meaningless (it could just memorize). Only performance on *unseen* data predicts real-world behavior. Reporting training accuracy as if it means something is the most common rookie mistake.

---

## Data leakage: the silent killer

If there's one failure that makes a model look amazing in development and then collapse in production, it's **leakage**. So let's not define it yet — let's feel it.

You're predicting which patients have a disease. You train, you test, you get **99.4% accuracy**. You're thrilled. You ship it. In production it's barely better than a coin flip. What happened?

You go back and look at the data — the reflex from earlier in this chapter. One of your features was `prescribed_drug_X`, and drug X is *only* given to people who already have the disease. Your model didn't learn to *predict* the disease; it learned to *read the answer off a feature that only exists after diagnosis.* In training and testing that feature was always there, so the score looked brilliant. But at real prediction time — when you're trying to diagnose someone *new* — that field is empty. The signal the model leaned on doesn't exist yet.

That's leakage: **information sneaks into training that won't actually be available at prediction time, or that secretly encodes the answer.** The model isn't "wrong" on your test set — your test set was lying to you. And the cruel part is the symptom looks exactly like success.

> 💡 **Concept notes — the tell-tale sign: too-good-to-be-true**
> The signature of leakage is **suspiciously high accuracy** — 99%+ on a problem that should be hard. When a result looks too good to be true on real-world data, your first move is not to celebrate; it's to *suspect a leak and go hunting.* Ask of every strong feature: *"Would I actually have this value, with this meaning, at the moment I need to predict — before the outcome is known?"* If the honest answer is "no, this only gets filled in afterward," you've found your leak.

Leakage isn't one bug — it's a family. They all share the same root (future or answer information bleeding backward into training) but they sneak in through different doors. Here are the four you must be able to name in an interview.

> 💡 **Concept notes — the four ways leakage sneaks in**
> - **Target leakage** (a feature encodes the answer): a column that is a *consequence* of the outcome, not a cause you'd have beforehand. `prescribed_drug_X` above; `collections_agency_assigned` for loan default (only set *after* default); `account_closed_reason` for churn. The fix: for every feature, ask *when* it gets populated. If it's populated at or after the moment the label becomes known, drop it.
> - **Train/test contamination** (the same rows, or near-duplicates, in both sets): the model "memorizes" examples it then gets tested on. Duplicate records, or augmented copies of the same image landing on both sides of the split, both do this. The fix: deduplicate *before* splitting.
> - **Temporal / look-ahead leakage** (using the future to predict the past): you predict tomorrow's price but your training rows include features computed from data that, in real time, only existed *after* the prediction moment — a rolling average that peeks forward, or a random shuffle that puts June's data in the training set and May's in the test set. The fix: split by *time*, never randomly, for any time-ordered problem — train on the past, test on the strictly later future.
> - **Group / member leakage** (the same entity on both sides): three photos of the same patient, one in train and two in test; or several transactions from one user split across sets. The model recognizes the *entity*, not the *pattern*, and your test score is inflated. The fix: split by group (patient, user, account), so every record for one entity stays on one side.

There's also a quieter, mechanical version that has nothing to do with your feature choices and everything to do with the *order* you do things in.

> 💡 **Concept notes — preprocess-after-split, always**
> If you scale, normalize, or fill missing values using statistics computed over the *whole* dataset, the mean/variance/median you used carry information from the test rows into training — the test set bleeds into the model before you ever "test" on it. It's leakage even though no single feature is suspicious. The discipline is rigid and worth memorizing: **split first, then fit every transformation on the training set only, and apply those fitted numbers to validation and test.** Same rule for choosing which features to keep, imputing, or learning an encoding — fit on train, apply to the rest.

---

## The data problems you'll actually hit

Beyond leakage, a few data issues recur constantly. Knowing their names lets you spot and discuss them:

> 💡 **Concept notes — common data ailments**
> - **Class imbalance:** 99% of transactions are legitimate, 1% fraud. A model that always says "legit" is 99% accurate and useless. (This is why accuracy alone lies — Chapter 5.) Fixes: resample, reweight, or change the metric.
> - **Distribution shift:** the world changes after you train. A model trained on pre-2020 shopping behavior broke in 2020. The data the model meets in production drifts away from its training data, and accuracy quietly decays. (You monitor for this — Chapter 14.)
> - **Missing values & noise:** real data has holes and errors. You decide how to fill or drop them — carefully, and *after* splitting.
> - **Insufficient or unrepresentative data:** too few examples, or examples that don't cover the real range of inputs (trained only on daytime photos, deployed at night).
> - **Labeling errors:** humans label inconsistently. Your "ground truth" is often itself a little wrong, which caps how good the model can get.

---

## The data-first workflow

Putting it together, the start of any ML project looks like this — and notice how *late* the model choice comes:

1. **Define the target.** What exactly are you predicting, and is it the right thing?
2. **Look at the data.** Actually open it. Plot it. Find the weirdness, the imbalance, the holes.
3. **Split it** (train/val/test) *before* any processing, to avoid leakage.
4. **Engineer features** and clean the data — fitting any transformations on *train only*.
5. **Then** pick a simple model and train (Chapters 3–4).
6. **Evaluate honestly** on held-out data, hunting for leaks if it looks too good (Chapter 5).

> 💡 **Concept notes — "look at the data" is not a cliché**
> Senior ML engineers spend a startling fraction of their time just *examining data* — eyeballing examples, plotting distributions, checking labels by hand. It's not glamorous and it's where the wins are. When a model underperforms, the move is rarely "try a fancier architecture"; it's "go look at what the model is getting wrong and *why*" — which almost always traces back to the data. Make "look at the data" your reflex and you'll be ahead of most people who can recite far more algorithms than you.

---

## Try it

1. You build a model to predict which customers will churn, and it hits 99.5% accuracy on the test set. What's your *first* reaction, and what specifically would you go looking for?
2. You're predicting delivery time. List three features you'd engineer from a raw "order placed at" timestamp.
3. Why must you split your data *before* filling in missing values or scaling features — not after? What leaks if you do it after?
4. Your fraud dataset is 99.8% legitimate transactions. Why is "accuracy" a dangerous metric here, and what could a useless model score?
5. A model works great in testing and poorly after launch, with no leak. What data problem (from the ailments list) might explain it?
6. Name the *type* of leakage in each case: (a) you predict stock price and split the rows randomly into train/test; (b) your churn model uses an `account_closed_date` feature; (c) your medical model has several scans of the same patient, some in train and some in test. For each, give the one-line fix.


---

## The bumper sticker

> *The model only knows what's in its data, so the data is the real lever. Split before you process, hunt for leakage when results look too good, and when a model struggles, look at the data before you touch the model.*

Next: the machinery under "training" — how a model actually turns examples into a learned function, using loss and gradient descent.

---

<div align="right">

[Chapter 3 →](aiml-chapter-3.md)

</div>
