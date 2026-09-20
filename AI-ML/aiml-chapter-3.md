# Chapter 3: How a model actually learns

*[← Chapter 2](aiml-chapter-2.md) · [Contents](aiml-README.md)*

- [ ] **Mark as read**

"The model learns from data" has been doing a lot of hand-waving for two chapters. Now we open the box. Learning, it turns out, is shockingly simple in principle: the model makes a guess, measures how wrong it was, and nudges itself to be slightly less wrong — then repeats that millions of times. The "measure how wrong" part is the **loss function**; the "nudge to be less wrong" part is **gradient descent**. Understand those two and you understand how *everything* in this book trains, from linear regression to GPT.

---

## A model is just numbers (parameters) you tune

Strip away the mystique and a model is a formula with adjustable knobs. The simplest example — a straight line:

$$\text{prediction} = w \times \text{input} + b$$

Here `w` (weight) and `b` (bias) are the **parameters** — the knobs. Training means *finding the values of `w` and `b` that make the predictions match the data.* A huge neural network is the same idea with millions or billions of knobs instead of two. "Training a model" = "searching for the parameter values that fit the data best."

> 💡 **Concept notes — parameters / weights**
> **Parameters** (often called **weights**) are the numbers *inside* the model that get adjusted during training — they *are* the learned function. GPT-style models are described as "175 billion parameters" etc.; that's literally how many tunable knobs they have. Contrast with **hyperparameters**, which are settings *you* choose before training (how fast to learn, how big the model, how many layers) and which are *not* learned. "Parameters are learned; hyperparameters are chosen" is a distinction interviewers like.

---

## Loss: a number for how wrong you are

To improve, the model needs to *measure* its wrongness as a single number. That's the **loss function**. Lower loss = better predictions. Training is, formally, the search for parameters that *minimize the loss.*

> 💡 **Concept notes — loss (the objective)**
> A **loss function** scores how far the model's predictions are from the true answers, as one number to minimize. For **regression**, a common loss is **mean squared error** — average the squared differences between predicted and actual (squaring punishes big misses harder and keeps everything positive). For **classification**, the standard is **cross-entropy** — roughly, how surprised the model was by the true answer; it's high when the model was confidently wrong. You don't need the formulas memorized, but you need the idea: *the loss turns "how good is this model" into a single number, and learning is minimizing it.* The choice of loss encodes what you care about.

```python
# Mean squared error, the idea in code:
def mse(predictions, actuals):
    return sum((p - a) ** 2 for p, a in zip(predictions, actuals)) / len(actuals)
# Lower is better. Training tries to make this as small as possible.
```

---

## Gradient descent: roll downhill

So we have knobs (`w`, `b`) and a wrongness score (loss). How do we find the knob settings that minimize loss? We can't try every combination — there are too many. Instead we use the most important algorithm in machine learning: **gradient descent.**

Picture the loss as a *landscape* — a hilly surface where each location is a setting of the parameters and the *height* is the loss. You want the lowest valley. You're standing somewhere in the fog and can't see the whole landscape, but you *can* feel which way is downhill right where you stand. So you take a small step downhill. Then feel again, step again. Repeat, and you descend toward a valley — a set of parameters with low loss.

> 💡 **Concept notes — gradient descent and the learning rate**
> The **gradient** is the direction of steepest *increase* of the loss (calculus gives it to us cheaply). So the *negative* gradient points downhill — toward lower loss. **Gradient descent** repeatedly: (1) computes the gradient of the loss with respect to each parameter, (2) nudges each parameter a small step in the downhill direction. The **learning rate** is the step size — a hyperparameter. Too small and training crawls; too large and you overshoot the valley and bounce around (or diverge). Tuning the learning rate is one of the most common practical knobs. Each full pass over the training data is an **epoch**; you usually do many.

```python
# Gradient descent, the shape of it (one parameter, schematically):
w = 0.0                      # start somewhere
learning_rate = 0.01
for epoch in range(1000):
    grad = gradient_of_loss(w)        # which way is uphill?
    w = w - learning_rate * grad      # step downhill
# After enough steps, w sits near the loss-minimizing value.
```

That loop — guess, measure loss, step downhill, repeat — is how linear regression trains, how neural networks train (via *backpropagation*, which is just gradient descent applied through many layers, Chapter 6), and how LLMs train. It is *the* engine of learning.

---

## The central tension: overfitting vs underfitting

A model that minimizes loss on the training data is not necessarily good — because it might minimize it by *cheating*: memorizing the training examples instead of learning the general pattern. This is the deepest idea in ML practice.

> 💡 **Concept notes — overfitting and underfitting**
> - **Overfitting:** the model learns the training data *too well*, including its noise and quirks, and fails on new data. It memorized instead of generalizing. Sign: great training score, poor validation/test score. Like a student who memorized the practice exam's answers but can't solve new problems.
> - **Underfitting:** the model is too simple (or undertrained) to capture the real pattern. Sign: poor scores on *both* training and validation. Like a student who didn't study enough.
> The goal is the sweet spot between them: **generalization** — learning the true pattern, not the noise. This is *why* the train/validation split (Chapter 2) exists: the gap between training performance and validation performance is your overfitting detector.

> 💡 **Concept notes — the bias–variance tradeoff**
> Two sources of error pull against each other. **Bias** is error from the model being too simple to capture reality (causes underfitting). **Variance** is error from the model being too sensitive to the specific training data (causes overfitting). Make the model more complex → bias drops but variance rises; simplify it → variance drops but bias rises. The art is balancing them. This "bias–variance tradeoff" is a classic interview phrase, and now you know it's just the formal name for the overfitting/underfitting balance.

---

## How we fight overfitting (the toolkit)

You don't need depth here yet, but know the names — they come up constantly:

> 💡 **Concept notes — regularization and friends**
> - **More data** — the best fix; harder to memorize a million examples than a hundred.
> - **Regularization** — penalize complexity directly: add a term to the loss that discourages large/elaborate parameters, nudging the model toward simpler functions that generalize better. (L1/L2 regularization, dropout in neural nets.)
> - **Simpler model** — fewer parameters, less room to memorize.
> - **Early stopping** — watch validation loss during training and stop when it starts *rising* (the moment memorization begins), even if training loss is still falling.
> All of these trade a little training-set performance for better real-world generalization — exactly the trade you want.

---

## Try it

1. In your own words, what are the two things gradient descent needs at each step, and what does it do with them?
2. Your model has near-perfect training accuracy but poor test accuracy. Name the problem and two things you'd try.
3. Your learning rate is set very high and the loss bounces around or blows up instead of decreasing. Explain why, using the "downhill in the fog" picture.
4. Is a deep neural network with millions of parameters more prone to high bias or high variance on a small dataset? Why?
5. What is the validation set's role in *detecting* overfitting, specifically? What signal are you watching?


---

## The bumper sticker

> *Training is a loop: guess, measure wrongness with a loss, step the parameters downhill via gradient descent, repeat. The whole skill is reaching the valley that generalizes — low loss on unseen data — without memorizing the training set on the way.*

Next: the classic models you'll actually reach for — regression, trees, and neighbors — and how to pick among them.

---

<div align="right">

[Chapter 4 →](aiml-chapter-4.md)

</div>
