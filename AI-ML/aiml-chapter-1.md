# Chapter 1: Learning a function instead of writing it

*[Contents](aiml-README.md)*

- [ ] **Mark as read**

Here is the entire idea of machine learning, and if you hold onto it, nothing in this book will feel like magic:

> **Normally you write a function. In ML, you *learn* one from examples.**

That's it. When the rules are simple enough to write by hand — "if the cart total is over $50, free shipping" — you just write the code. But some rules are hopeless to write by hand. Write me t[...]

---

## Code you write vs. functions you learn

A normal program is a function *you* author: you know the logic, you type the rules.

```python
def shipping_is_free(cart_total):
    return cart_total > 50          # YOU wrote the rule
```

A machine-learned model is a function whose *rules were derived from data*:

```python
# You never wrote the rule for "is this email spam?"
# You showed the model 50,000 emails labeled spam / not-spam,
# and it learned a function:  email_text -> probability_of_spam
spam_probability = model.predict(email_text)
```

You didn't write "if it contains the word 'viagra' and three exclamation marks and a suspicious link, then spam." You couldn't have — spammers change tactics, and the real rule is a tangle of th[...]

> 💡 **Concept notes — the core vocabulary**
> - **Model:** the learned function. It takes an input and produces an output (a number, a category, some text).
> - **Training:** the process of *finding* that function from labeled examples. (Chapter 3 shows how.)
> - **Inference (or prediction):** *using* the trained model on new, unseen input. Training is done once (expensive); inference happens millions of times (cheap-ish).
> - **Features:** the input signals the model looks at (the words in the email, the pixels in the photo). (Chapter 2.)
> - **Label (or target):** the right answer for a training example (spam / not-spam). Data with labels is what makes "learning" possible.
> Memorize these five — they're the load-bearing words for the whole field.

---

## The three flavors of "learning"

Not all learning uses labeled answers. There are three classic setups, and knowing which one a problem is tells you a lot.

> 💡 **Concept notes — supervised, unsupervised, reinforcement**
> - **Supervised learning** — you have inputs *and* the right answers (labels), and the model learns input → answer. *Spam detection, price prediction, image classification.* This is ~90% of p[...]
> - **Unsupervised learning** — you have inputs but *no* answers; the model finds structure on its own. *Clustering customers into segments, finding anomalies, compressing data.* (Embeddings, Ch[...]
> - **Reinforcement learning** — an agent takes actions in an environment and learns from *rewards* over time. *Use when:* you don't have labeled "correct answers," but you can define a reward signal. *Examples: game-playing AI (AlphaGo), robot learning, self-driving cars, recommendation systems. Importantly, the "RLHF" step that fine-tunes ChatGPT uses RL ideas.*
> Most problems you'll meet are supervised. When someone says "we don't have labels," that's the tell for unsupervised — or for "we need to go label some data first." When someone says "we need an agent that learns by trying things," that's reinforcement learning.

---

## Two shapes of supervised problem

Within supervised learning, the output is either a *category* or a *number*, and this split decides your tools and metrics:

### Classification: Predict a category

> **"Is this X or Y?"** → **Classification**

The model outputs a *category* — one of a fixed set of choices. Think of it as the model placing your example into a bucket.

**Examples:**
- Email → spam / not-spam (2 categories)
- Photo → cat / dog / bird (3 categories)
- Customer review → positive / neutral / negative (3 categories)
- Loan application → approve / deny (2 categories)

**What the model outputs:** Usually a *probability for each category*. For spam detection, it might say "92% spam, 8% not-spam" — you pick the highest one. Some problems have "soft" outputs (probabilities), others have "hard" outputs (just the winning category).

**Metrics that matter:** accuracy (% correct), precision (of the ones you labeled positive, how many really were?), recall (of the true positives, how many did you catch?). False positives vs. false negatives matter differently depending on the problem.

**Intuition:** You're binning or sorting. Your output is *discrete* — 5 tiers of customer satisfaction, not 5.3 tiers.

> 💡 **Concept notes — sentiment analysis, the classic text classifier**
> **Sentiment analysis** is just classification with *text* as the input: feed in a sentence — a review, a tweet, a support ticket — and predict its emotional tone (*positive / negative*, sometimes *neutral*, or a finer scale). It's the "hello world" of applied NLP because the setup is so clean: the label is obvious to a human, data is everywhere (a star rating *is* a label), and it powers real products — brand monitoring, review triage, routing an angry customer to a person. Two ways to build it: the **classic** route turns text into features (bag-of-words / TF-IDF, Ch 7) and trains a plain classifier; the **modern** route hands the raw text to an embedding model or an LLM (Ch 8–10). Same question either way — *which bucket does this text belong to?*

### Regression: Predict a number

> **"How much / how many / what value?"** → **Regression**

The model outputs a *continuous number* from an infinite (or very large) range. Think of it as predicting a value on a number line.

**Examples:**
- House features → house price ($250,000? $1.2M?)
- Weather data → tomorrow's temperature (72.3°F)
- Customer data → expected lifetime value ($3,456)
- Order details → estimated delivery time (2.5 days)

**What the model outputs:** A single number (or sometimes a range/confidence interval). There's no "winning bucket" — the model guesses a value.

**Metrics that matter:** error magnitude — how far off were you? Average dollars wrong, average degrees wrong, average days wrong. Common metrics: MAE (mean absolute error), RMSE (root mean squared error).

**Intuition:** You're predicting a quantity. Your output is *continuous* — the house could be any price, not just one of 5 price tiers.

### The key difference at a glance

| | **Classification** | **Regression** |
|---|---|---|
| **Question** | "Which category?" | "What number?" |
| **Output** | One of N fixed buckets | Any number in a range |
| **Examples** | Spam/not-spam, disease/no-disease, dog/cat/bird | Stock price, temperature, sales revenue |
| **Metrics** | Accuracy, precision, recall, confusion matrix | MAE, RMSE, R² (how much variance explained) |
| **Tools** | Logistic regression, decision trees, neural networks for classification | Linear regression, neural networks for regression |

> **One of the first things you do with any ML problem is decide which it is, because everything downstream depends on it.** Wrong choice = wrong model = wrong metrics = wasted time.

---

## When to use each learning type: A quick decision tree

| **Situation** | **Learning Type** | **Use when...** | **Example** |
|---|---|---|---|
| You have inputs & labeled outputs; predicting a **category** | **Supervised + Classification** | You can label data as "right answers," output is discrete | Detect fraud (fraud/not-fraud) |
| You have inputs & labeled outputs; predicting a **number** | **Supervised + Regression** | You can label data as "right answers," output is continuous | Predict house price |
| You have *only* inputs; no labels | **Unsupervised** | No one labeled your data; find patterns yourself | Segment customers, anomaly detection |
| You have an agent & reward signals; no labeled examples | **Reinforcement** | Agent learns by trial/reward, no "right answer" dataset | Game AI, robot learning, self-driving car |

---

## The most important skill: knowing when *not* to use ML

This sounds backwards in an ML book, but it's a genuine senior signal and interviewers probe for it. ML is seductive and often the *wrong* tool. It adds enormous cost: you need data, the system be[...]

> 💡 **Concept notes — use ML only when the rules are unwritable**
> Good fit for ML — all three usually hold: (1) the rule is **too complex to write by hand** (image recognition, language understanding, fraud patterns); (2) you have **enough labeled data** to [...]

---

## Where LLMs fit (a preview)

You came here mostly for the ChatGPT-era stuff, so here's the bridge. A large language model is *exactly* this chapter's idea taken to an extreme: a function learned from data, where the data is m[...]

---

## Try it

1. For each, say whether it's a job for ML or for plain code, and why: (a) converting Celsius to Fahrenheit, (b) detecting whether a customer review is positive or negative, (c) calculating sales [...]
2. For each ML one above, is it classification or regression? What would the label be?
3. Name something you'd want ML for but probably *can't* get — because you lack the labeled data. What data would you need to collect first?
4. Think of a feature in an app you use that's "AI-powered." Is it supervised, unsupervised, or reinforcement learning? What do you think its input and output are?
5. **Bonus:** You're building a system where a robot arm learns to pick up objects. No one has labeled "correct arm positions." Is this supervised, unsupervised, or reinforcement learning? Why?


---

## The bumper sticker

> *Machine learning is learning a function from examples instead of writing it by hand — use it only when the rule is too messy to code, you have the data, and you can tolerate being wrong. Ever[...]

Next: the uncomfortable truth that the *data*, not the model, is where ML projects are really won and lost.

---

<div align="right">

[Chapter 2 →](aiml-chapter-2.md)

</div>
