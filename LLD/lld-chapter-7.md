# Chapter 7: When the same action means different things

*[← Chapter 6](lld-chapter-6.md) · [Contents](lld-README.md)*

- [ ] **Mark as read**

A vending machine.

States it can be in:
- **Idle** — waiting for someone to insert money
- **HasMoney** — money inserted, waiting for selection
- **Dispensing** — selection made, dispensing item
- **OutOfStock** — empty, can't sell anything

User actions:
- Insert money
- Select an item
- Take the item

What "insert money" *does* depends on the state:
- Idle → transition to HasMoney, store the amount
- HasMoney → add to existing money
- Dispensing → reject (can't insert during dispense)
- OutOfStock → reject and refund

You see where this is going.

## The obvious move

If/elif on a `state` variable.

```python
class VendingMachine:
    def __init__(self):
        self.state = "idle"
        self.money = 0
        self.stock = {"chips": 5, "soda": 3}
        self.prices = {"chips": 2, "soda": 3}

    def insert_money(self, amount):
        if self.state == "idle":
            self.money = amount
            self.state = "has_money"
        elif self.state == "has_money":
            self.money += amount
        elif self.state == "dispensing":
            print("Wait, currently dispensing")
        elif self.state == "out_of_stock":
            print(f"Machine empty, refunding {amount}")

    def select_item(self, item):
        if self.state == "idle":
            print("Insert money first")
        elif self.state == "has_money":
            if self.stock.get(item, 0) == 0:
                print("Out of that item")
                return
            if self.money < self.prices[item]:
                print("Not enough money")
                return
            self.money -= self.prices[item]
            self.stock[item] -= 1
            self.state = "dispensing"
            print(f"Dispensing {item}")
        elif self.state == "dispensing":
            print("Already dispensing")
        elif self.state == "out_of_stock":
            print("Machine empty")

    def take_item(self):
        if self.state == "dispensing":
            self.state = "idle" if any(self.stock.values()) else "out_of_stock"
            print("Item taken")
        else:
            print("Nothing to take")
```

It works. Let it work for a minute. Then look at it.

## What's wrong

Every method has the same shape: `if self.state == "X" do this elif state == "Y" do that`. The state is the dispatcher in every method.

Adding a new state — say, "Maintenance" — means touching every method to add a new `elif`. Adding a new action — say, "cancel" — means writing a method that *also* has the if/elif ladder for every state.

The number of branches is *states × actions*. Today: 4 × 3 = 12 branches. Add Maintenance and Cancel: 5 × 4 = 20. It grows multiplicatively.

Worse: the logic for *one state* is scattered across all the methods. To understand HasMoney, you have to read every method and find the `elif state == "has_money"` branch. The state's behavior is spread out instead of together.

Different smell than Ch3 and Ch5. Not "swap algorithms" or "notify everyone." This is: *behavior depends on what mode I'm in.*

## The move

Each state becomes its own class. The machine *holds* its current state. Actions get forwarded.

```python
class IdleState:
    def insert_money(self, machine, amount):
        machine.money = amount
        machine.set_state(HasMoneyState())

    def select_item(self, machine, item):
        print("Insert money first")

    def take_item(self, machine):
        print("Nothing to take")


class HasMoneyState:
    def insert_money(self, machine, amount):
        machine.money += amount

    def select_item(self, machine, item):
        if machine.stock.get(item, 0) == 0:
            print("Out of that item")
            return
        if machine.money < machine.prices[item]:
            print("Not enough money")
            return
        machine.money -= machine.prices[item]
        machine.stock[item] -= 1
        machine.set_state(DispensingState(item))
        print(f"Dispensing {item}")

    def take_item(self, machine):
        print("Nothing to take yet")


class DispensingState:
    def __init__(self, item):
        self.item = item

    def insert_money(self, machine, amount):
        print("Wait, currently dispensing")

    def select_item(self, machine, item):
        print("Already dispensing")

    def take_item(self, machine):
        next_state = IdleState() if any(machine.stock.values()) else OutOfStockState()
        machine.set_state(next_state)
        print(f"{self.item} taken")


class OutOfStockState:
    def insert_money(self, machine, amount):
        print(f"Machine empty, refunding {amount}")

    def select_item(self, machine, item):
        print("Machine empty")

    def take_item(self, machine):
        print("Nothing to take")


class VendingMachine:
    def __init__(self):
        self.money = 0
        self.stock = {"chips": 5, "soda": 3}
        self.prices = {"chips": 2, "soda": 3}
        self.state = IdleState()

    def set_state(self, state):
        self.state = state

    def insert_money(self, amount):
        self.state.insert_money(self, amount)

    def select_item(self, item):
        self.state.select_item(self, item)

    def take_item(self):
        self.state.take_item(self)
```

Machine methods became one line each: forward to the current state.

State classes each contain *all the behavior for that one state*. Want to know what HasMoney does? Open HasMoneyState. Everything is there.

Adding "Maintenance" is now one new class. The machine doesn't change. Existing states don't change. You write one file.

## What this bought us

**1. Behavior grouped by state, not method.** All HasMoney logic lives in HasMoneyState. Reading one state's code shows everything it does.

**2. State transitions are explicit.** `machine.set_state(HasMoneyState())` is right there, in the method causing the transition. No hidden state-string mutation buried in an elif branch.

**3. The machine got tiny.** It holds data (money, stock, prices) and a current state. Actions forward. The machine doesn't dispatch — it just holds.

**4. New states don't cascade.** Add Maintenance, Refunding, ServiceMode — each is one new class, zero modifications to anything else.

## The name

This is the **State pattern**. The shape:

1. The object can be in different states, each with different behavior
2. Each state becomes a class with the same set of methods
3. The object holds a reference to its current state
4. Actions are forwarded to the current state, which decides what to do
5. States can transition the object to a different state

State and Strategy look similar from outside — both delegate to objects. The difference:

- **Strategy:** the algorithm is chosen at construction and usually stays. *You* pick the strategy.
- **State:** the state changes as the object's lifecycle progresses. The *object itself* changes its state based on what happens.

## Before you turn the page

**Exercise 1:** Add a `MaintenanceState`. When in maintenance, all actions print "Out of service." Add `enter_maintenance()` and `exit_maintenance()` methods on the machine.

**Exercise 2:** Add a `cancel()` action. Calling it refunds money and returns to Idle, but only from HasMoneyState. From other states, it does nothing.

**Exercise 3 (recognition):** Find a class in your work code with a `status` or `state` field whose methods branch on it. Order processing usually has this (Draft / Pending / Confirmed / Shipped / Delivered / Cancelled). That's a State candidate.

---

<div align="right">

[Chapter 8 →](lld-chapter-8.md)

</div>
