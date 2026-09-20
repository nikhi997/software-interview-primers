# Chapter 5: When one thing happens, many things need to know

*[← Chapter 4](lld-chapter-4.md) · [Contents](lld-README.md)*

- [ ] **Mark as read**

New problem. New chapter.

> "When a user places an order, send them a confirmation email."

Trivial. Function. Call it after order placement. Done.

```python
class OrderService:
    def place_order(self, user, items):
        # ... create the order ...
        self._send_email(user, "Order confirmed")

    def _send_email(self, user, message):
        print(f"Email to {user.email}: {message}")
```

Works.

## The growth

Few days later: *"Also send an SMS confirmation."*

Add `_send_sms`. Call it. Fine.

Then: *"Push notification too."*

Add `_send_push`. Fine.

Then: *"Update analytics. Ping inventory. Tell the warehouse system. Run fraud detection."*

`place_order` now:

```python
def place_order(self, user, items):
    # ... create the order ...
    self._send_email(user, "Order confirmed")
    self._send_sms(user, "Order confirmed")
    self._send_push(user, "Order confirmed")
    self._update_analytics(user, items)
    self._notify_inventory(items)
    self._notify_warehouse(items)
    self._check_fraud(user, items)
```

The actual "place order" logic is one line. The other seven lines are *things that happen because* an order was placed. They're not part of placing. They're reactions to it.

## Is this Strategy?

Quick check. Strategy was *one-of-N*. Here we want *all* of these to happen. Different shape.

You might think: "make a list of reactions, loop through them."

That's the right instinct. Let's write it properly.

## The move

Each reaction becomes its own class. The order service keeps a list. When an order happens, it tells everyone on the list.

```python
class EmailNotifier:
    def handle(self, user, items):
        print(f"Email to {user.email}: order confirmed")


class SMSNotifier:
    def handle(self, user, items):
        print(f"SMS to {user.phone}: order confirmed")


class InventoryService:
    def handle(self, user, items):
        for item in items:
            print(f"Decrement inventory: {item}")


class FraudDetector:
    def handle(self, user, items):
        print(f"Checking fraud for {user}")


class OrderService:
    def __init__(self):
        self.listeners = []

    def subscribe(self, listener):
        self.listeners.append(listener)

    def unsubscribe(self, listener):
        self.listeners.remove(listener)

    def place_order(self, user, items):
        # ... create the order ...
        print(f"Order placed for {user}")
        for listener in self.listeners:
            listener.handle(user, items)
```

Usage:

```python
>>> orders = OrderService()
>>> orders.subscribe(EmailNotifier())
>>> orders.subscribe(SMSNotifier())
>>> orders.subscribe(InventoryService())
>>> orders.subscribe(FraudDetector())
>>> orders.place_order(some_user, ["spaghetti", "tomatoes"])
Order placed for ...
Email to ...
SMS to ...
Decrement inventory: spaghetti
Decrement inventory: tomatoes
Checking fraud for ...
```

The order service doesn't know what its listeners *do*. It just knows there are some, and they want to be told.

## Strategy vs this — the difference

Both extract logic into separate classes. Both let you add new behavior without touching the core class. But:

**Strategy** — *"I have a job. I delegate it to **one** of several implementations. The strategy does the job for me."*

**This new shape** — *"Something just happened to me. I tell **all** my listeners. Each one decides what to do."*

Storage was Strategy. The shortener delegates "save data" to *one* storage.

Notifications are this new shape. The order service announces "an order happened." Multiple listeners react. The order service doesn't depend on any of them.

The shapes:
- Strategy = "use this one to do the job"
- This = "tell everyone something happened"

## What this bought us

**1. Adding a reaction is one new class.** Write a `WarehouseNotifier` with a `handle` method. Subscribe it. The order service doesn't change.

**2. Removing a reaction is one line.** `orders.unsubscribe(sms_notifier)`. The order service didn't know which one it was.

**3. The order service kept its job.** Placing an order. All the unrelated work (emails, fraud, inventory) lives in separate classes — own files, own tests, possibly own teams.

**4. Order of reactions is controllable.** Subscribe in the order you want. Or sort before iterating. Or fan them out to threads.

## A Python note

> 💡 **Duck typing, again**
> Same as Chapter 3. The order service calls `listener.handle(user, items)`. As long as the object passed to `subscribe` has a `handle` method with those arguments, it works. No formal base class. The convention is the contract.
> Pick a method name (`handle`, `on_event`, `notify`, `update`) and stick with it across all subscribers in a codebase.

## The name

This shape is the **Observer pattern**. Also called "Publish-Subscribe" or "Event Listener" — same shape, different names depending on the framework.

Vocabulary you'll see in real codebases:
- The announcer is the *subject* or *publisher* (here, `OrderService`)
- The listeners are *observers* or *subscribers* (the notifier classes)
- "I want to know" is *subscribing*
- The announcement is the *event*

You'll meet these terms in Redux, RxJS, every UI framework, Kafka, every messaging system. They're all Observer in different clothes.

## Before you turn the page

**Exercise 1:** Add a `LoggingNotifier` that writes events to a log file. Subscribe it alongside the others.

**Exercise 2:** Right now, every notifier gets *every* event. What if `FraudDetector` should only run for orders above $1000? Two options:
- (a) FraudDetector checks the order itself and returns early when it doesn't apply
- (b) The order service filters which listeners get called based on the event

Which is cleaner? Why? Sit with it.

**Exercise 3 (real-world rep):** Find a function in your work code that does one thing, then five other unrelated-but-triggered-by-it things. Don't refactor — just identify. That's an Observer candidate.

---

<div align="right">

[Chapter 6 →](lld-chapter-6.md)

</div>
