# Chapter 6: Neural networks from the perceptron up

*[← Chapter 5](aiml-chapter-5.md) · [Contents](aiml-README.md)*

- [ ] **Mark as read**

Everything so far — regression, trees, kNN — works beautifully on tabular data but hits a wall on images, audio, and language, where the patterns are too tangled for a weighted sum or a flowchart. **Neural networks** are what broke through that wall, and they power essentially all modern AI, including the LLMs you came here for. The good news: a neural network is *not* a new idea. It's the exact learning machinery from Chapter 3 — parameters, loss, gradient descent — wired up in a way that lets it learn its own features. Let's build one up from a single neuron.

---

## The perceptron: one artificial neuron

The atom of a neural network is the **neuron** (or perceptron), and it's almost insultingly simple: it takes several inputs, multiplies each by a weight, adds them up with a bias, and passes the result through one more function. That's it — it's logistic regression (Chapter 4) wearing a different hat.

$$\text{output} = \text{activation}(w_1 x_1 + w_2 x_2 + \dots + w_n x_n + b)$$

> 💡 **Concept notes — the artificial neuron**
> A **neuron** computes a *weighted sum* of its inputs plus a bias, then applies an **activation function**. The weights are the knobs that get learned (Chapter 3). One neuron alone can only draw a straight dividing line — it's no more powerful than logistic regression. The magic appears when you stack *many* neurons into *layers* and connect them. The biological "neuron" analogy is loose and mostly historical; think of it as a tiny tunable function, not a brain cell.

---

## Why you need activation functions

If you just chained weighted sums together, the whole network would collapse back into a single weighted sum — a straight line, no matter how many layers. The thing that lets networks learn *curvy, complex* patterns is a small dose of non-linearity between layers: the **activation function.**

> 💡 **Concept notes — activation functions and non-linearity**
> An **activation function** is a simple non-linear function applied to each neuron's output. Without it, stacking layers is pointless (math collapses to one linear layer). With it, stacking layers lets the network approximate *any* function — bending and folding the input space into complex shapes. The most common one today is **ReLU** ("output the value if positive, else zero") — dead simple and trains fast. Older ones (sigmoid, tanh) squash into a fixed range. The takeaway: **non-linearity is what gives deep networks their power**; activations are how you inject it.

---

## Layers: stacking neurons into depth

Put many neurons side by side and you have a **layer**. Stack layers so each one's outputs feed the next, and you have a **deep neural network** — "deep" just means "more than a couple of layers."

> 💡 **Concept notes — layers and what "deep" buys you**
> - **Input layer:** your features (pixels, word vectors, etc.).
> - **Hidden layers:** the middle layers where the real computation happens — each transforms its input into a more useful representation.
> - **Output layer:** produces the final answer (a probability, a number, a word).
> The profound part is what the hidden layers *do*: **they learn features automatically.** In image recognition, early layers learn to detect edges, middle layers assemble edges into shapes (an eye, a wheel), later layers assemble shapes into objects (a face, a car). Nobody programmed "look for edges" — the network discovered that this is a useful intermediate representation, because it reduced the loss. This is the headline difference from Chapter 4: classic ML needs *you* to engineer features; deep learning **learns the features itself**, given enough data. That's why it dominates images, audio, and text, where good features are nearly impossible to hand-craft.

---

## Backpropagation: gradient descent through the layers

How does a network with millions of weights across many layers learn? The same engine as Chapter 3 — gradient descent — plus one clever idea for computing all those gradients efficiently: **backpropagation.**

> 💡 **Concept notes — backpropagation**
> After the network makes a prediction and the loss measures how wrong it was, **backpropagation** works *backward* from the output through each layer, using the chain rule of calculus to compute how much each individual weight contributed to the error — i.e., the gradient for every weight. Then gradient descent nudges each weight downhill (Chapter 3). Forward pass to predict, backward pass to assign blame, step the weights, repeat millions of times. You don't need the calculus; you need the picture: **backprop is just "figure out how much each knob was responsible for the error, then turn each knob a little." It's gradient descent made to work across many layers.** This algorithm, plus lots of data and fast GPUs, is what made deep learning explode.

---

## Why now? Data + compute

Neural networks were invented decades ago and then mostly languished. Three things changed in the 2010s and set off the modern AI boom — worth knowing as context:

> 💡 **Concept notes — the three ingredients that unlocked deep learning**
> 1. **Data:** the internet produced massive labeled datasets (millions of images, the whole web of text). Deep networks are data-hungry, and finally there was enough.
> 2. **Compute:** **GPUs** (graphics chips) turn out to be perfect for the parallel math of neural networks, making it feasible to train huge models. (This is why a GPU company became one of the most valuable in the world.)
> 3. **Algorithmic improvements:** better activations (ReLU), better training tricks, and eventually the Transformer architecture (Chapter 8).
> The lesson echoes the track's theme: the model ideas were old; **data and compute** were the unlock. When people ask "why is AI suddenly everywhere," this is the honest answer.

---

## When (not) to reach for deep learning

Deep learning is powerful but not free — it needs lots of data, lots of compute, and it's a black box that's hard to interpret. The Chapter 4 wisdom still holds:

> 💡 **Concept notes — deep learning's sweet spot**
> Use deep learning when the input is **unstructured and high-dimensional** — images, audio, text — where features are impossible to hand-craft and you have lots of data. For **tabular** data, tree ensembles usually still win with far less effort (Chapter 4). And deep models are **opaque**: you can't easily read *why* they decided, which matters in regulated settings. "Neural network for the image problem, gradient boosting for the spreadsheet" is the instinct to carry forward.

---

## Try it

1. Why can't a single neuron (or a stack of them with no activation functions) learn a curved decision boundary? What does the activation function add?
2. In an image classifier, what kinds of features do early layers tend to learn versus later layers? Who told them to?
3. Explain backpropagation in one sentence to a friend, using the word "blame."
4. Someone says "deep learning made feature engineering obsolete." In what domains is that roughly true, and where is it still false?
5. Why did neural networks suddenly become dominant in the 2010s when the core ideas were decades old? Name the three ingredients.


---

## The bumper sticker

> *A neural network is the same learn-by-gradient-descent engine, stacked into layers with a dash of non-linearity — and that depth lets it learn its own features instead of you engineering them. Backprop assigns blame across the layers; data and compute did the rest.*

Next: the single most important idea in modern AI — turning everything into vectors, so that *meaning* becomes math.

---

<div align="right">

[Chapter 7 →](aiml-chapter-7.md)

</div>
