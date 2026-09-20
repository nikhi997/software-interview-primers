# Chapter 18: A class in front of a class

*[← Chapter 17](lld-chapter-17.md) · [Contents](lld-README.md)*

- [ ] **Mark as read**

By now you've met six patterns: Strategy, Observer, State, Decorator, Singleton, Factory. Three more show up constantly in interviews, and they share a family resemblance. Each one is *a class that sits in front of other classes.*

- **Proxy** stands in front of *one* object and controls when and whether you reach it.
- **Facade** stands in front of *many* objects and turns them into one simple door.
- **Chain of Responsibility** lines objects up so a request walks past them until one acts.

All three will remind you of Decorator from Ch8 — they wrap, they share an interface, they delegate. The work of this chapter is feeling the *difference* in each one's pain, so you reach for the right name instead of the nearest name.

## Proxy — when the real thing is expensive or off-limits

A photo gallery. Each image is a big file — slow to read off disk, slow to decode.

```python
class RealImage:
    def __init__(self, filename):
        self.filename = filename
        self._load_from_disk()

    def _load_from_disk(self):
        print(f"loading {self.filename} from disk")  # pretend: slow and heavy

    def display(self):
        print(f"displaying {self.filename}")


class Gallery:
    def __init__(self, filenames):
        self.images = [RealImage(f) for f in filenames]

    def show(self, index):
        self.images[index].display()
```

Open a gallery of 500 photos and every single file loads off disk in `__init__` — before you've looked at one of them. You scroll past 490 and view 10. You paid for 500.

The obvious patch is to make the caller lazy: `if not loaded: load()` scattered wherever an image might get shown. But now every caller knows about the two-step "check, then load" dance. The laziness has leaked out of the image and into everyone who touches it.

### The move

Put a stand-in object in front of the real one. Same method — `display()` — but it doesn't build the `RealImage` until someone actually calls it.

```python
class LazyImage:
    def __init__(self, filename):
        self.filename = filename
        self._real = None

    def display(self):
        if self._real is None:
            self._real = RealImage(self.filename)
        self._real.display()
```

Now the gallery holds `LazyImage` objects. Constructing it loads nothing. The disk read happens on the first `display()` of each image and never for the ones you skip. The gallery code didn't change — a `LazyImage` looks identical to a `RealImage` from outside.

That's a *virtual proxy*: it stands in for an object that's expensive to create. The same shape covers two other jobs:

```python
class ProtectedImage:
    def __init__(self, real_image, user):
        self.inner = real_image
        self.user = user

    def display(self):
        if not self.user.is_admin:
            raise PermissionError("admins only")
        self.inner.display()
```

A *protection proxy* — same interface, but it guards access. Swap the check for "return a saved result if I've seen this call before" and you have a *caching proxy*. Three jobs, one shape.

### The name

This is the **Proxy pattern**. A proxy has the same interface as the real object and holds a reference to it (or to the information needed to make it). Callers can't tell the difference. The proxy decides *when*, *whether*, or *for whom* the real call happens.

It looks like Decorator, and people mix them up. The split is about intent:

- **Decorator** always has its inner object and *adds behavior* to it. Every layer runs. (Logging *and* the save both happen.)
- **Proxy** *controls access* to its inner object — which might not exist yet (virtual), might be forbidden (protection), or might be skippable (caching). The real call might not happen at all.

> 💡 **Concept note — Proxy vs Decorator**
> Same structure (wrap an object, keep its interface), opposite questions. Decorator asks *"what else should happen when this runs?"* Proxy asks *"should this run at all, and when?"* If you're adding a feature, it's a decorator. If you're standing guard — gatekeeping, deferring, caching — it's a proxy.

## Facade — when the client has to know too much

Placing an order touches four subsystems: reserve inventory, charge payment, schedule shipping, send a notification. Each is its own class, which is good — separate concerns.

```python
class InventoryService:
    def reserve(self, item): print(f"reserved {item}")

class PaymentService:
    def charge(self, user, amount): print(f"charged {user} ${amount}")

class ShippingService:
    def schedule(self, item, address): print(f"shipping {item} to {address}")

class NotificationService:
    def send(self, user, message): print(f"[to {user}] {message}")
```

But now look at what it takes to *use* them. Every place that places an order does this:

```python
inventory.reserve(item)
payment.charge(user, amount)
shipping.schedule(item, address)
notifier.send(user, f"your {item} is on the way")
```

Four calls, in the right order, every time. The checkout page does it. The admin "create order" tool does it. The mobile API does it. Three callers, each coupled to four subsystems and to the exact sequence. Change the order of steps — say, charge *before* you reserve — and you hunt down every caller.

### The move

One class with one method that hides the dance.

```python
class OrderFacade:
    def __init__(self, inventory, payment, shipping, notifier):
        self.inventory = inventory
        self.payment = payment
        self.shipping = shipping
        self.notifier = notifier

    def place_order(self, user, item, amount, address):
        self.inventory.reserve(item)
        self.payment.charge(user, amount)
        self.shipping.schedule(item, address)
        self.notifier.send(user, f"your {item} is on the way")
```

Every caller collapses to:

```python
facade.place_order("alice", "book", 20, "1 Main St")
```

One line. The caller no longer knows there *are* four subsystems, let alone the order to call them in. The sequence lives in exactly one place.

### The name

This is the **Facade pattern**: one simple interface over a complicated subsystem. A friendly front door to a building with a lot of rooms.

Two things keep a facade honest:

- It **delegates, it doesn't do**. The facade calls the four services; it doesn't reimplement inventory or payment logic inside itself. The moment it starts *doing* the work, it's turning into a God class (Ch12's smell), not a facade.
- It's a **convenience, not a wall**. The subsystems still exist and a caller with an unusual need can still use them directly. Facade differs from Proxy here: a proxy *controls* access (you go through it or not at all); a facade just offers an easier path.

## Chain of Responsibility — when a request needs to find its handler

Expense approvals. A team lead can approve up to \$100, a manager up to \$1,000, a director up to \$10,000. Anything more gets rejected.

```python
def approve(amount):
    if amount <= 100:
        print(f"team lead approves ${amount}")
    elif amount <= 1000:
        print(f"manager approves ${amount}")
    elif amount <= 10000:
        print(f"director approves ${amount}")
    else:
        print(f"${amount} exceeds all limits — rejected")
```

It works. Then someone adds a VP tier at \$50,000, and a new rule that the team-lead limit drops to \$50 on weekends. Each change reopens this one function. The knowledge of "who approves what" is welded into a single `if`-ladder, and no single approver's rule can be reused, reordered, or tested on its own.

This is a cousin of the State smell from Ch7 — behavior buried in a conditional — but the shape is different. Here a request needs to *travel* until something is willing to handle it.

### The move

Make each approver an object that either handles the request or passes it to the next one in line.

```python
class Approver:
    def __init__(self, name, limit):
        self.name = name
        self.limit = limit
        self.next = None

    def set_next(self, approver):
        self.next = approver
        return approver  # return it so we can chain set_next calls

    def approve(self, amount):
        if amount <= self.limit:
            print(f"{self.name} approves ${amount}")
        elif self.next is not None:
            self.next.approve(amount)
        else:
            print(f"${amount} exceeds all limits — rejected")
```

Build the chain once, then hand requests to the front:

```python
lead = Approver("team lead", 100)
manager = Approver("manager", 1000)
director = Approver("director", 10000)

lead.set_next(manager).set_next(director)

lead.approve(50)     # team lead approves $50
lead.approve(500)    # manager approves $500
lead.approve(5000)   # director approves $5000
lead.approve(50000)  # exceeds all limits — rejected
```

Adding the VP tier is now one new `Approver` and one `set_next` — no existing approver changes. Reordering is rewiring the links, not rewriting a ladder. Each approver's rule lives with the approver.

### The name

This is the **Chain of Responsibility pattern**: a request moves along a chain of handlers; each one either handles it or forwards it. The sender doesn't know which handler will end up doing the work — it just hands the request to the front of the chain.

This is the one most easily confused with Decorator, because both link objects that each do a bit of work and call the next. The difference is whether a link can *stop*:

- **Decorator** — every layer runs and then delegates inward. Nobody short-circuits; the point is that *all* of them contribute.
- **Chain of Responsibility** — a link can *handle and stop*. The request travels only until someone claims it. Many links may never run.

Request middleware sits right on this line, which is why people argue about it. If every middleware always calls the next (auth, then logging, then the handler), it's behaving like Decorator. If a middleware can reject and stop the request cold (auth fails → 401, chain ends), it's behaving like Chain of Responsibility.

## What ties these together

Four patterns now share the "wrap an object, keep its interface" structure. Hold them apart by their *intent*:

| Pattern | Stands in front of | The question it answers |
|---|---|---|
| **Decorator** | one object | "what *else* should happen when this runs?" |
| **Proxy** | one object | "should this run *at all*, and *when*?" |
| **Facade** | many objects | "can I make this *one simple call*?" |
| **Chain of Responsibility** | a line of objects | "who, if anyone, will *handle* this?" |

When a problem makes you want to "put something in front" of your classes, don't grab the first wrapper that fits. Name the pain first — adding behavior, guarding access, simplifying a subsystem, or routing a request — and the right pattern names itself.

## Before you turn the page

**Exercise 1 (Proxy):** Write a `CachingCalculator` proxy in front of a `SlowCalculator` whose `compute(n)` is deliberately expensive (e.g., sums `range(n)` after a `print("computing...")`). The proxy returns a stored result for repeat arguments and only forwards new ones. Confirm "computing..." prints once per distinct `n`.

**Exercise 2 (Facade):** Go back to the URL shortener. Wrap "generate a code, save it, log it, and bump a metric" behind a `ShortenerFacade.create_short_url(long_url)`. Check that a caller needs to know about none of the four steps.

**Exercise 3 (recognition):** Find a chain in code you already use — request middleware, a logging handler chain (Python's own `logging` propagates records up a chain of loggers), or a support-ticket escalation (tier 1 → tier 2 → engineering). Ask the key question: can a link *stop* the request, or does every link always run? That answer tells you Chain of Responsibility from Decorator.

---

<div align="right">

[Chapter 19 →](lld-chapter-19.md)

</div>
