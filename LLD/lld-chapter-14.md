# Chapter 14: The interview ritual

*[← Chapter 13](lld-chapter-13.md) · [Contents](lld-README.md)*

- [ ] **Mark as read**

You know patterns. You know SOLID. You can draw UML. Now: how do you actually *do* an LLD interview?

There's a workflow. Five steps. Use it every time. It works because it's how senior engineers actually think when designing things — not because it's a memorized routine.

The five steps:

1. **Clarify requirements** — ask questions before designing
2. **Identify entities** — what are the nouns?
3. **Sketch the class diagram** — boxes and lines
4. **Walk through one flow** — pick a use case, trace it
5. **Discuss tradeoffs** — what would change for X?

Let's apply this to a real problem.

## The problem: Splitwise

*"Design Splitwise. It tracks expenses between friends. You add an expense, split it among people, and it tells everyone who owes whom."*

Don't start coding. Don't draw classes. **Step 1.**

## Step 1: Clarify

Ask these *out loud* in a real interview. The interviewer wants to see this exact behavior — they want to know you don't just assume.

Functional:
- Can users create groups, or are expenses person-to-person?
- How are expenses split? Equally? Custom amounts? Percentages?
- One currency, or multi-currency?
- Can expenses be edited? Deleted?
- Simplified debts (A→B, not A→B and B→C separately)?

Non-functional:
- Roughly how many users? Toy or production?
- Mobile-only, or web with multiple devices?
- Real-time updates, or eventual?

For this exercise, assume the answers:
- Groups exist; expenses are within groups
- Splits: equal, exact amounts, or percentage
- Single currency
- Expenses can be edited and deleted
- Simplified debts: yes
- ~1000 users, mobile + web
- Eventual updates (within seconds) are fine

Write these down. They're your scope now.

## Step 2: Entities

What are the nouns? List them.

- **User** — a person
- **Group** — a set of users
- **Expense** — a charge in a group, paid by someone, split among others
- **Split** — how one expense is divided
- **Balance** — who owes whom in a group

Five entities. Simple problem. Real interviews often have 6–10.

Not every noun survives as a class. `name`, `email`, and `amount` are single values something else carries — they stay attributes, not classes. The ones that made the list each bundle state *and* behavior: a `Group` knows its members and can total what's owed; an `Expense` knows its amount and can divide itself. Watch one noun earn its keep the other way — *how* an expense is split is itself a thing with behavior (equal, exact, percentage), so it becomes its own class, `SplitStrategy`.

For each, jot responsibilities:

```
User: id, name, email
Group: id, name, members, expenses
Expense: id, amount, paid_by, split_strategy, splits
Split: user, amount_owed
SplitStrategy: knows how to divide an expense
```

The relationships fall out of those lines: a `Group` *has* many `User`s and many `Expense`s, an `Expense` *has* one `SplitStrategy` that produces the `Split`s. All `has-a` — nothing here is a true `is-a`, so no inheritance yet.

Notice "SplitStrategy" — Strategy pattern jumping out. Multiple ways to split (equal, exact, percentage), caller picks one per expense.

## Step 3: Class diagram

```
[User]───*───[Group]───*───[Expense]
                                │ 1
                                ▼
                         [SplitStrategy] ◁── EqualSplit
                                          ◁── ExactSplit
                                          ◁── PercentageSplit
                                │
                                │ produces
                                ▼
                          [Split (user, amount)]
```

Verbalize while drawing: "Users belong to many Groups. A Group has many Expenses. Each Expense has one SplitStrategy that produces the actual Splits."

## Step 4: Code skeleton

You won't write full code in an interview. Just skeletons. Here's what's expected:

```python
class User:
    def __init__(self, user_id, name, email):
        self.id = user_id
        self.name = name
        self.email = email


class Split:
    def __init__(self, user, amount):
        self.user = user
        self.amount = amount


class EqualSplit:
    def split(self, total_amount, users):
        per_person = total_amount / len(users)
        return [Split(u, per_person) for u in users]


class ExactSplit:
    def __init__(self, amounts):
        self.amounts = amounts  # {user: amount}

    def split(self, total_amount, users):
        if sum(self.amounts.values()) != total_amount:
            raise ValueError("Exact amounts must sum to total")
        return [Split(u, self.amounts[u]) for u in users]


class PercentageSplit:
    def __init__(self, percentages):
        self.percentages = percentages  # {user: percentage}

    def split(self, total_amount, users):
        if sum(self.percentages.values()) != 100:
            raise ValueError("Percentages must sum to 100")
        return [Split(u, total_amount * self.percentages[u] / 100) for u in users]


class Expense:
    def __init__(self, expense_id, amount, paid_by, users, split_strategy):
        self.id = expense_id
        self.amount = amount
        self.paid_by = paid_by
        self.splits = split_strategy.split(amount, users)


class Group:
    def __init__(self, group_id, name):
        self.id = group_id
        self.name = name
        self.members = []
        self.expenses = []

    def add_member(self, user):
        self.members.append(user)

    def add_expense(self, expense):
        self.expenses.append(expense)

    def get_balances(self):
        # positive = others owe this user; negative = this user owes others
        net = {member: 0 for member in self.members}
        for expense in self.expenses:
            net[expense.paid_by] += expense.amount
            for split in expense.splits:
                net[split.user] -= split.amount
        return net
```

## Step 5: Walk a flow

Pick a use case. Walk through it out loud.

*"Alice, Bob, and Charlie are in a group. Alice pays $90 for dinner, split equally."*

```python
alice = User(1, "Alice", "a@x.com")
bob = User(2, "Bob", "b@x.com")
charlie = User(3, "Charlie", "c@x.com")

group = Group(1, "Trip")
group.add_member(alice)
group.add_member(bob)
group.add_member(charlie)

expense = Expense(
    1, 90, paid_by=alice,
    users=[alice, bob, charlie],
    split_strategy=EqualSplit()
)
group.add_expense(expense)

balances = group.get_balances()
# alice: +60 (paid 90, owes 30 of her share)
# bob: -30
# charlie: -30
```

The interviewer can follow your code from this trace. That's the goal.

## Step 6: Tradeoffs

The interviewer almost always asks "What would you change if...?"

Common follow-ups:

- **"Millions of users."** → In-memory lists won't scale. Move to a database. `get_balances` becomes a SQL query (sum of paid minus sum of owed). Discuss caching balances.

- **"Multi-currency."** → Add `currency` to Expense. Conversion at calculation time or at addition time? Tradeoffs.

- **"Settle a debt — A pays B."** → Add a `Payment` class (reduces a balance). Or model payments as a special expense type.

- **"Simplified debts."** → After computing pairwise balances, run an algorithm to minimize transactions. Greedy: largest creditor pays largest debtor, repeat.

- **"Audit log."** → Observer pattern. Subscribe a logger to expense additions/edits/deletions.

You don't have to *implement* these. You have to *explain* how the design absorbs them. Often the right answer is "this pattern, applied here." If you used Strategy for splits, adding a new split type is "one new class, no other changes." That's the answer.

## The thing nobody tells you about LLD interviews

The interviewer is not grading the final design. They're grading the *process*. Did you clarify? Did you name the patterns when you used them? Did you discuss tradeoffs?

A messy diagram with clear thinking beats a perfect diagram with no narration.

Talk constantly. Narrate your choices. *"I'm using Strategy here because splitting has multiple algorithms and we want to add new ones without changing Expense."*

If you say nothing and write perfect code, you'll get a worse signal than someone with mediocre code who clearly explains the *why*.

## Before you turn the page

**Exercise 1:** Practice the five-step ritual on a new problem. Pick one:
- Design Twitter (simplified — tweet, follow, timeline)
- Design a chess game (board, pieces, moves)
- Design a movie ticket booking system

Don't write full code. Five-minute budget per step: requirements, entities, class diagram, one flow, one tradeoff. Total 25 minutes. That's the real interview budget.

**Exercise 2:** Record yourself (audio) doing one of these. Listen back. Did you sound like you were thinking, or performing? Did you narrate the *why* or only the *what*?

The next three chapters are worked examples — me doing this ritual on three classic LLD problems. Read them *after* you've tried Exercise 1 cold. Otherwise you'll just memorize my solutions.

---

<div align="right">

[Chapter 15 →](lld-chapter-15.md)

</div>
