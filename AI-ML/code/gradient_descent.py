"""
Chapter 3 — How a model actually learns.

Gradient descent, from scratch, in pure Python (no numpy).
We fit a straight line  y = w*x + b  to noisy data by:
  1. making a prediction,
  2. measuring how wrong we are (the loss),
  3. stepping the parameters downhill (gradient descent),
  4. repeating.

This is the SAME engine that trains neural networks and LLMs,
just with two knobs instead of billions.

Run:  python3 gradient_descent.py
"""


def make_data():
    # True relationship we're pretending not to know: y = 2x + 5
    # (a little hand-added "noise" so it's not a perfect line)
    xs = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    noise = [0.3, -0.2, 0.1, -0.4, 0.2, 0.0, -0.1, 0.3, -0.2, 0.1]
    ys = [2 * x + 5 + n for x, n in zip(xs, noise)]
    return xs, ys


def predict(x, w, b):
    return w * x + b


def mse_loss(xs, ys, w, b):
    # Mean squared error: average of (prediction - actual)^2
    total = 0.0
    for x, y in zip(xs, ys):
        error = predict(x, w, b) - y
        total += error * error
    return total / len(xs)


def gradients(xs, ys, w, b):
    # Partial derivatives of MSE with respect to w and b.
    # You don't need the calculus memorized — this is "which way is uphill,
    # for each knob." Gradient descent then steps the OTHER way (downhill).
    n = len(xs)
    grad_w = 0.0
    grad_b = 0.0
    for x, y in zip(xs, ys):
        error = predict(x, w, b) - y
        grad_w += 2 * error * x
        grad_b += 2 * error
    return grad_w / n, grad_b / n


def train(xs, ys, learning_rate=0.01, epochs=2000):
    w, b = 0.0, 0.0  # start the knobs anywhere
    for epoch in range(epochs):
        grad_w, grad_b = gradients(xs, ys, w, b)
        # The core step: nudge each parameter a little way downhill.
        w -= learning_rate * grad_w
        b -= learning_rate * grad_b
        if epoch % 400 == 0:
            print(f"epoch {epoch:4d}  loss={mse_loss(xs, ys, w, b):7.4f}  "
                  f"w={w:.3f}  b={b:.3f}")
    return w, b


if __name__ == "__main__":
    xs, ys = make_data()
    print("Training a line y = w*x + b by gradient descent")
    print("(true answer is roughly w=2, b=5)\n")
    w, b = train(xs, ys)
    print(f"\nLearned:  w={w:.3f}  b={b:.3f}")
    print(f"Final loss: {mse_loss(xs, ys, w, b):.4f}")
    print(f"Prediction for x=10: {predict(10, w, b):.2f}  (true ~25)")
