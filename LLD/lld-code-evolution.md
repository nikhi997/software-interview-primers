# Companion: One system, twenty chapters — the helpdesk that grew up

*[Contents](lld-README.md) · [Appendix](lld-appendix.md)*

Three kinds of document live in this folder now. The **chapters** teach — each one derives a single move from a single pain, in its own toy domain (a URL shortener, a parking lot, Splitwise). The **appendix** looks up — one-line reference cards for after you've already learned the thing. This page does neither. It **synthesizes**: one running system, evolving requirement by requirement, in the exact order the twenty chapters taught their moves — so you can see the whole skeleton stand up at once instead of twenty disconnected examples.

Read this *after* you've done the chapters (and ideally the [cold rebuild drills](lld-cold-rebuild-drills.md)) — it's a reconstruction check, not a first introduction. If a section here doesn't click, that's a signal to reopen the chapter it's paired with, not to keep reading past it.

The running system is a small internal **helpdesk** — call it Bramble Desk. Tickets come in, agents work them, teams own them, SLAs govern them. It's deliberately *not* any of the book's own worked domains, so you're pattern-matching the shape, not recognizing the words.

Every section below is a compact ledger, five lines, always in the same order:

- **Requirement** — what landed on your desk
- **Failing pressure** — exactly how the current code starts to hurt
- **Smallest change** — the diff that relieves it, no more
- **Invariant / tests** — the one thing that must stay true after the change
- **Cost / deferred** — what this doesn't solve yet, named honestly

Code fragments are small and partial — diffs, not re-dumps. By the end you'll have watched one system absorb twenty chapters of pressure without pretending every migration is free.

---

## Ch 1–2 · From loose functions to one ticket tracker

*Pairs with: [Chapter 1](lld-chapter-1.md) · [Chapter 2](lld-chapter-2.md)*

**Requirement.** "Track support tickets. Open one, close one, list the open ones."

**Failing pressure.** The obvious first pass is exactly Ch1's shape: a global dict and some functions.

```python
tickets = {}
next_id = 1

def open_ticket(subject, requester):
    global next_id
    tickets[next_id] = {"subject": subject, "requester": requester, "open": True}
    next_id += 1
    return next_id - 1

def close_ticket(ticket_id):
    tickets[ticket_id]["open"] = False
```

It works, right up until "also persist to disk" and "also track which agent owns each ticket" land in the same week. Now every function that touches `tickets` has to remember to save, and a new teammate opening this file has no single answer to "what *is* the helpdesk?" — same feeling Ch1 named over the URL shortener's globals.

**Smallest change.** Fold state and behavior into one class — nothing about the logic changes, only where it lives (Ch2's whole point: *classes don't add logic, they add a home*).

```python
class HelpDesk:
    def __init__(self):
        self.tickets = {}
        self.next_id = 1

    def open_ticket(self, subject, requester):
        ticket_id = self.next_id
        self.tickets[ticket_id] = {"subject": subject, "requester": requester, "open": True}
        self.next_id += 1
        return ticket_id

    def close_ticket(self, ticket_id):
        self.tickets[ticket_id]["open"] = False

    def open_tickets(self):
        return [t for t in self.tickets.values() if t["open"]]
```

**Invariant / tests.** `open_ticket` always returns a fresh, previously-unused id; `close_ticket` on an unknown id should raise (`KeyError` is fine for now) rather than silently doing nothing.

**Cost / deferred.** Storage is still nothing — restart and every ticket vanishes. Tickets are plain dicts, not their own class, so there's nothing yet to stop someone writing `tickets[5]["subject"] = 42`. Both are next.

---

## Ch 3–4 · Swappable storage, then swappable routing

*Pairs with: [Chapter 3](lld-chapter-3.md) · [Chapter 4](lld-chapter-4.md)*

**Requirement.** "Tickets must survive a restart." Two weeks later: "New tickets should route to an agent automatically — round robin for now, but ops wants to try least-loaded assignment too."

**Failing pressure.** First instinct for persistence: a `backend` flag and an `if/elif` inside `_save`/`_load` — the exact shape Ch3 built and then took apart. Second instinct for routing: a `rule` flag and a second, unrelated `if/elif` inside `assign()` — Ch4's whole lesson is *recognizing* that this is the same smell showing up again, in a different member of the class, for a different reason.

**Smallest change.** Two independent Strategy families, not one. Storage varies along one axis (where bytes live); routing varies along a completely different axis (who gets the next ticket) — they don't belong in the same abstraction just because both showed up as `if` ladders.

```python
class FileStorage:
    def save(self, data): ...   # writes {ticket_id: {...}} to disk
    def load(self): ...

class MemoryStorage:
    def save(self, data): self.data = data
    def load(self): return getattr(self, "data", {})


class RoundRobinRouting:
    def __init__(self):
        self._last_index = -1

    def assign(self, ticket, agents):
        self._last_index = (self._last_index + 1) % len(agents)
        return agents[self._last_index]

class LeastLoadedRouting:
    def assign(self, ticket, agents):
        return min(agents, key=lambda agent: len(agent.current_tickets))


class HelpDesk:
    def __init__(self, storage, routing):
        self.storage = storage
        self.routing = routing
        self.tickets = self.storage.load()
```

**Invariant / tests.** Swap `storage` and nothing about `open_ticket`/`close_ticket` changes; swap `routing` and nothing about `open_ticket` changes either. Any routing strategy must return an agent who's actually available — never `None` silently absorbed downstream.

**Cost / deferred.** Ticket status is still a bare `"open": True/False` — no lifecycle yet (Ch7). No one is told when a ticket opens or gets assigned (Ch5). Both storage and routing are wired only through the constructor — that's Dependency Inversion (Ch11) a chapter before it has a name.

---

## Ch 5 · When a ticket changes, who needs to know

*Pairs with: [Chapter 5](lld-chapter-5.md)*

**Requirement.** "When a ticket opens, assign, or closes, email the requester, write an audit log line, and bump a metrics counter."

**Failing pressure.** Bolted onto the end of each method, this is three unrelated calls per method — six total across `open_ticket` and `close_ticket`, more once `assign` joins in. The actual "open a ticket" logic is one line; the other three are *reactions* to it, not part of it. Identical shape to Ch5's order service growing seven trailing calls off a one-line `place_order`.

**Smallest change.** Extract each reaction into its own listener; `HelpDesk` announces events and stops caring who's listening.

```python
class TicketEvent:
    def __init__(self, name, ticket_id, subject, requester):
        self.name = name
        self.ticket_id = ticket_id
        self.subject = subject
        self.requester = requester


class EmailNotifier:
    def handle(self, event):
        print(f"EMAIL to {event.requester}: ticket {event.name}")

class AuditLogger:
    def handle(self, event):
        print(f"[audit] {event.name} — {event.subject}")

class MetricsCollector:
    def __init__(self):
        self.counts = {}

    def handle(self, event):
        self.counts[event.name] = self.counts.get(event.name, 0) + 1


class HelpDesk:
    def __init__(self, storage, routing):
        self.storage, self.routing = storage, routing
        self.tickets = self.storage.load()
        self.listeners = []

    def subscribe(self, listener):
        self.listeners.append(listener)

    def _notify(self, event_name, ticket_id, ticket):
        event = TicketEvent(
            event_name,
            ticket_id,
            ticket["subject"],
            ticket["requester"],
        )
        for listener in self.listeners:
            listener.handle(event)

    def open_ticket(self, subject, requester):
        ticket = {"subject": subject, "requester": requester, "open": True}
        ticket_id = self._store(ticket)
        self._notify("opened", ticket_id, ticket)
        return ticket_id
```

The stable thing listeners receive is the `TicketEvent`, not the ticket's storage shape. Today `HelpDesk` builds the event from a dict. Later, when tickets become real objects, only `_notify` changes its extraction; listeners keep reading `event.subject` and `event.requester`.

**Invariant / tests.** Adding or removing a listener never touches `open_ticket`/`close_ticket`. Every listener sees every event — if `MetricsCollector` only cares about `"closed"`, that filter lives inside `MetricsCollector`, not inside `HelpDesk`.

**Cost / deferred.** Listeners run synchronously, in the caller's thread — a slow email send blocks the ticket operation. Named as a tradeoff, not fixed here (a real system would queue events). Notifiers are still hardcoded classes; config-driven construction is next.

---

## Ch 6 · Configured notifiers, and a Singleton we regret almost immediately

*Pairs with: [Chapter 6](lld-chapter-6.md)*

**Requirement.** "Notifiers should be built from config — email, Slack, or SMS — without `HelpDesk` knowing the concrete classes. Also: ops wants exactly one shared outbound mail client for the whole app, since it's rate-limited by the mail provider."

**Failing pressure.** Two different problems that sound similar. The first — "build the right notifier from config" — is Ch6's factory function, plain and correct. The second — "exactly one shared mail client" — is the Singleton *temptation*, and it's worth walking into the trap on purpose so you feel why Ch6 calls it controversial.

**Smallest change, part one (the factory — keep this).**

```python
def create_notifier(config):
    if config["type"] == "email":
        return EmailNotifier()
    elif config["type"] == "slack":
        return SlackNotifier(config["webhook"])
    elif config["type"] == "sms":
        return SMSNotifier(config["gateway"])
    raise ValueError(f"unknown notifier type: {config['type']}")
```

**Smallest change, part two (the Singleton — build it, then read the receipt).**

```python
class MailClient:
    _instance = None

    def __new__(cls, rate_limit=100):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.rate_limit = rate_limit
        return cls._instance
```

Try it: `MailClient(rate_limit=100)` then `MailClient(rate_limit=5)` — the second call's argument is silently ignored, exactly like Ch6's `Logger` filename trap. Worse, any test that constructs a `MailClient` leaks its state into the next test unless something explicitly resets `_instance`.

**Invariant / tests.** `create_notifier({"type": "slack", "webhook": "..."})` returns something with the same `.handle(event)` shape as every other notifier — swapping the config never requires a new caller-side branch. Separately: the mail client's send counter only increases when something actually called `send` — never on construction.

**Cost / deferred.** The class stays in the codebase, but the *design* doesn't lean on "only one can ever exist" — it leans on "we build one `MailClient` at startup and inject it into every notifier that needs it," which is dependency injection wearing Singleton's clothes without its silent-argument bug. The honest note, carried forward: if you ever see `MailClient()` called from three different places expecting three different rate limits, that's this chapter's regret resurfacing.

---

## Ch 7 · The ticket's own lifecycle

*Pairs with: [Chapter 7](lld-chapter-7.md)*

**Requirement.** "A ticket isn't just open or closed. It moves: New → Assigned → InProgress → WaitingOnCustomer → Resolved → Closed — and it can reopen from Resolved or Closed if the customer replies."

**Failing pressure.** Every method that touches status — `assign`, `start_work`, `wait_on_customer`, `resolve`, `close`, `reopen` — becomes an `if self.status == "X" elif self.status == "Y"` ladder, six actions × six states, the exact vending-machine shape from Ch7. Behavior for "what does WaitingOnCustomer do on every action" is scattered across all six methods instead of living together.

**Smallest change.** Each status becomes a class with the same method names; `Ticket` holds its current state and forwards.

```python
class NewState:
    def assign(self, ticket, agent):
        ticket.agent = agent
        ticket.set_state(AssignedState())
    def resolve(self, ticket):
        raise ValueError("cannot resolve a ticket with no work started")

class WaitingOnCustomerState:
    def resolve(self, ticket):
        ticket.set_state(ResolvedState())
    def reopen(self, ticket):
        raise ValueError("cannot reopen a ticket that's still open")

class ResolvedState:
    def reopen(self, ticket):
        ticket.set_state(InProgressState())

class Ticket:
    def __init__(self, subject, requester):
        self.subject, self.requester = subject, requester
        self.agent = None
        self.state = NewState()

    def set_state(self, state):
        self.state = state

    def assign(self, agent):
        self.state.assign(self, agent)

    def resolve(self):
        self.state.resolve(self)
```

**Invariant / tests.** Illegal transitions raise rather than silently succeed — `resolve()` on a brand-new, unassigned ticket must fail loudly. `reopen()` is legal only from `ResolvedState`/`ClosedState`.

**Cost / deferred.** States don't yet know about the Ch5 listeners — a transition doesn't (yet) announce itself. SLA timers aren't wired to any of this. Both arrive when everything gets integrated in Ch9–10.

---

## Ch 8 · Wrapping the ticket operations without touching them

*Pairs with: [Chapter 8](lld-chapter-8.md)*

**Requirement.** "Every ticket-changing call must be logged with a timestamp. Only agents with the `support` role may assign or close a ticket. Notification sends should get two retries before giving up."

**Failing pressure.** Sprinkling `if not agent.has_role("support"): raise` and `print(f"[{now}] ...")` inside every `HelpDesk` method — and a retry loop inside every notifier's `handle` — duplicates the same guard/log/retry shape across many unrelated places. Two cross-cutting concerns (auth, logging) times N operations, plus retry times M notifiers, is the same combinatorial mess Ch8's encryption-and-logging storages hit.

**Smallest change.** Logging and retry are true Ch8 wrappers: every legal call still reaches the real object, and the wrapper adds behavior around it. The support-role guard has the same outer shape, but don't name it yet — because it can stop the real call entirely, Ch18 will give it the more precise name.

```python
class LoggingTicketOps:
    def __init__(self, inner):
        self.inner = inner
    def assign(self, ticket, agent):
        print(f"[log] assign({ticket.subject!r}, {agent.name})")
        return self.inner.assign(ticket, agent)
    def close(self, ticket, agent):
        print(f"[log] close({ticket.subject!r}, {agent.name})")
        return self.inner.close(ticket, agent)

class SupportRoleGuard:
    def __init__(self, inner):
        self.inner = inner
    def assign(self, ticket, agent):
        if "support" not in agent.roles:
            raise PermissionError(f"{agent.name} cannot assign tickets")
        return self.inner.assign(ticket, agent)
    def close(self, ticket, agent):
        if "support" not in agent.roles:
            raise PermissionError(f"{agent.name} cannot close tickets")
        return self.inner.close(ticket, agent)

class RetryingNotifier:
    def __init__(self, inner, attempts=3):
        self.inner, self.attempts = inner, attempts
    def handle(self, event):
        for attempt in range(self.attempts):
            try:
                return self.inner.handle(event)
            except ConnectionError:
                if attempt == self.attempts - 1:
                    raise
```

`ops = LoggingTicketOps(SupportRoleGuard(real_ops))` — the log wrapper adds a timestamp-shaped side effect; the guard may prevent the real assign logic from running at all. That distinction matters, so for now we only say "same wrapper shape, different intent."

**Invariant / tests.** Wrapping never changes what a *legal* call does — only adds a check, a log line, or a retry around it. An unauthorized agent's `assign` call is stopped by `SupportRoleGuard` before `HelpDesk`'s real logic runs at all.

**Cost / deferred.** Wrapping order is a real decision: put logging outside the guard if unauthorized attempts must be logged, or put the guard outside logging if they should leave no operation log. Retry has no backoff yet.

---

## Ch 9–10 · Modeling the desk properly, then wiring it whole

*Pairs with: [Chapter 9](lld-chapter-9.md) · [Chapter 10](lld-chapter-10.md)*

**Requirement.** "Not all tickets are the same — an `IncidentTicket` (a live outage) has a severity and pages on-call immediately; a `ServiceRequestTicket` (like 'reset my password') doesn't. Agents belong to teams with skills. Now wire everything from the last five chapters into one working desk."

**Failing pressure.** Before any pattern, this is Ch9's unglamorous skeleton work: find the nouns (`Ticket`, `IncidentTicket`, `ServiceRequestTicket`, `Agent`, `Team`), decide `is-a` versus `has-a`, and resist over-modeling. `IncidentTicket` really *is a* `Ticket` (true, stable is-a — same fields, same lifecycle, one extra behavior). An agent's skills are something they *have*, not a subclass they belong to — modeling `SkilledSupportAgent(Agent, Skillset)` would be the same multiple-inheritance trap Ch9 warned about for `ManagerWhoCodes`.

**Smallest change.** An abstract `Ticket` (never instantiated bare — you never want a ticket with no real type), two concrete subclasses, and composition everywhere else:

```python
from abc import ABC, abstractmethod

class Ticket(ABC):
    def __init__(self, subject, requester):
        self.subject, self.requester = subject, requester
        self.agent = None
        self.state = NewState()

    @abstractmethod
    def requires_paging(self):
        ...

    def to_record(self):
        record = {
            "type": self.ticket_type,
            "subject": self.subject,
            "requester": self.requester,
            "agent": self.agent.name if self.agent else None,
            "state": type(self.state).__name__,
        }
        record.update(self.extra_record_fields())
        return record

    def extra_record_fields(self):
        return {}

    @classmethod
    def from_record(cls, record, agents_by_name):
        ticket_class = TICKET_TYPES[record["type"]]
        ticket = ticket_class.from_record_fields(record)
        ticket.agent = agents_by_name.get(record["agent"])
        ticket.state = STATE_TYPES[record["state"]]()
        return ticket

class IncidentTicket(Ticket):
    ticket_type = "incident"

    def __init__(self, subject, requester, severity):
        super().__init__(subject, requester)
        self.severity = severity

    def requires_paging(self):
        return self.severity <= 2   # sev-1 and sev-2 page on-call

    def extra_record_fields(self):
        return {"severity": self.severity}

    @classmethod
    def from_record_fields(cls, record):
        return cls(record["subject"], record["requester"], record["severity"])

class ServiceRequestTicket(Ticket):
    ticket_type = "service_request"

    def requires_paging(self):
        return False

    @classmethod
    def from_record_fields(cls, record):
        return cls(record["subject"], record["requester"])


class Agent:
    def __init__(self, name, skillset):
        self.name = name
        self.skillset = skillset          # has-a, not is-a
        self.current_tickets = []

class Team:
    def __init__(self, name, agents):
        self.name = name
        self.agents = agents              # has-a many


STATE_TYPES = {
    "NewState": NewState,
    "AssignedState": AssignedState,
    "InProgressState": InProgressState,
    "WaitingOnCustomerState": WaitingOnCustomerState,
    "ResolvedState": ResolvedState,
    "ClosedState": ClosedState,
}
TICKET_TYPES = {
    "incident": IncidentTicket,
    "service_request": ServiceRequestTicket,
}
```

One quiet migration has to happen right here. Ch1's JSON note still applies: JSON writes dicts, lists, strings, numbers, booleans, and `None` — not arbitrary Python objects. So the storage boundary stays deliberately plain:

```python
class HelpDesk:
    def _event_for(self, event_name, ticket_id, ticket):
        return TicketEvent(event_name, ticket_id, ticket.subject, ticket.requester)

    def _notify(self, event_name, ticket_id, ticket):
        event = self._event_for(event_name, ticket_id, ticket)
        for listener in self.listeners:
            listener.handle(event)

    def _save(self):
        records = {
            ticket_id: ticket.to_record()
            for ticket_id, ticket in self.tickets.items()
        }
        self.storage.save({"next_id": self.next_id, "tickets": records})

    def _legacy_record(self, ticket):
        state_name = "NewState" if ticket["open"] else "ClosedState"
        return {
            "type": "service_request",
            "subject": ticket["subject"],
            "requester": ticket["requester"],
            "agent": None,
            "state": state_name,
        }

    def _load(self, agents_by_name):
        raw = self.storage.load()
        if not raw:
            data = {"next_id": 1, "tickets": {}}
        elif "tickets" not in raw:
            data = {
                "next_id": max([int(ticket_id) for ticket_id in raw] or [0]) + 1,
                "tickets": {
                    ticket_id: self._legacy_record(ticket)
                    for ticket_id, ticket in raw.items()
                },
            }
        else:
            data = raw
        self.next_id = data["next_id"]
        self.tickets = {
            int(ticket_id): Ticket.from_record(record, agents_by_name)
            for ticket_id, record in data["tickets"].items()
        }

    def open_ticket(self, subject, requester, severity=None):
        if severity is None:
            ticket = ServiceRequestTicket(subject, requester)
        else:
            ticket = IncidentTicket(subject, requester, severity)
        ticket_id = self.next_id
        self.tickets[ticket_id] = ticket
        self.next_id += 1
        self._save()
        self._notify("opened", ticket_id, ticket)
        return ticket_id
```

That's the cost of turning ticket dicts into ticket objects: every persisted field must be named explicitly, and reconstruction must put the object graph back together. Runtime-only fields stay out of the record. When Ch20 adds `ticket.lock`, this `to_record` path is why the lock never gets serialized; a fresh lock is created when the ticket object is rebuilt.

Then the actual integration — every prior chapter's piece, plumbed together, in the same spirit as Ch10's parking lot:

```
HelpDesk
  ◆ storage (Ch3 Strategy)      ◆ routing (Ch4 Strategy)
  ◇ listeners (Ch5 Observer)    ◆ logging/retry wrappers (Ch8 Decorator)
  ◇ many Teams ── ◇ many Agents
  produces Tickets whose lifecycle is a state machine (Ch7)
```

What *didn't* need a new pattern: team membership is plain composition, no Observer or Strategy required for it. No Facade yet (Ch18) — opening a ticket is still a direct method call, not yet hidden behind one door.

**Invariant / tests.** `HelpDesk.open_ticket(...)` returns the same shape regardless of which `Ticket` subclass was created — a caller looping over tickets and calling `.requires_paging()` never checks the type first (polymorphism). Swapping routing or adding a listener still requires zero edits inside `HelpDesk`'s method bodies.

**Cost / deferred.** No fast way yet to ask "what's the single most urgent ticket right now" — that's a data-structure problem (Ch19), not a modeling one. No protection against two agents claiming the same ticket at once (Ch20).

---

## Ch 11–13 · Auditing, refactoring, and drawing the desk we built

*Pairs with: [Chapter 11](lld-chapter-11.md) · [Chapter 12](lld-chapter-12.md) · [Chapter 13](lld-chapter-13.md)*

**Requirement.** "A second team is about to extend Bramble Desk. Before they touch it, give them an audit they can act on, clean up the terms that would mislead them, and draw the current shape so onboarding doesn't depend on oral history."

**Failing pressure.** The system runs, but new change pressure is different from runtime pressure. A teammate can still break it by not seeing the seams: storage vs routing, event listeners vs ticket lifecycle, ticket type vs ticket state. Worse, early notes used `priority`, `urgency`, and `severity` for the same concept, so a new SLA change could easily update the wrong field.

**Smallest change.** First, run Ch11's five-letter audit against the code already built:
- **S** — `HelpDesk` no longer owns storage format, routing rule, and notification channel; those reasons to change moved into their own classes.
- **O** — a new routing strategy or notifier is a new class, not an edit to `HelpDesk`.
- **L** — `IncidentTicket` and `ServiceRequestTicket` both honor the `Ticket` contract; callers ask `.requires_paging()` without type checks.
- **I** — storage stays at `{save, load}`. No `backup()` method appears until a caller actually needs backups.
- **D** — `HelpDesk` is handed a storage and routing object; it doesn't construct `FileStorage` or `RoundRobinRouting` internally.

Then do the Ch12 cleanup the audit exposed: one ubiquitous word, `severity`, for "how urgent the incident is"; no `priority` alias in ticket records, queues, or diagrams. Finally, draw the Ch13 diagram so the next change starts from the real shape instead of a mental guess.

**Invariant / tests.** The audit and rename are behavior-preserving: saved tickets still reconstruct, routing still returns an agent, listeners still receive the same `TicketEvent` fields. The diagram must match code that already exists — no box appears just because it feels like a pattern should be there.

**Cost / deferred.** This doesn't add product behavior. It buys change safety: clearer names, known seams, and a shared picture. The cost is time spent documenting and renaming now so the next feature doesn't pay it with interest.

**Diagram.**

```
┌────────────────┐        ◆ *        ┌──────────┐   ◇ *   ┌───────┐
│   HelpDesk     │───────────────────│   Team   │─────────│ Agent │
├────────────────┤                   └──────────┘         └───────┘
│ - storage      │◇ 1  [Storage]
│ - routing      │◇ 1  [RoutingStrategy]
│ - listeners    │◇ *  [Listener]
└────────────────┘
        ◆ *
        ▼
   ┌─────────┐
   │ Ticket  │◁── IncidentTicket, ServiceRequestTicket
   ├─────────┤
   │ - state │◆ 1  [TicketState] ◁── New, Assigned, InProgress, Waiting, Resolved, Closed
   └─────────┘
```

Nothing on this diagram wasn't already in the code by Ch10 — Ch13's job is making the shape visible, not adding to it.

---

## Ch 14 · Running the ritual on our own system

*Pairs with: [Chapter 14](lld-chapter-14.md)*

**Requirement.** "Send a customer-satisfaction survey 24 hours after a ticket closes — but not if it gets reopened first."

This is the moment to show the five-step ritual doesn't just apply to a blank whiteboard problem — it applies to *extending a system you already own*, which is what most real work actually is.

1. **Clarify requirements.** One survey per closed ticket, sent once, cancelled if the ticket reopens before the 24 hours elapse. Sent via whichever notifier the requester prefers.
2. **Identify entities.** A `SurveySchedule` (ticket, fire-at time, cancelled flag) — new noun, small state, its own class.
3. **Sketch the class diagram.** `HelpDesk ◆── many SurveySchedule`; a `SurveySchedule` references one `Ticket`.
4. **Walk through one flow.** A ticket closes, so `ClosedState` asks `HelpDesk` to create a schedule for 24 hours later. Twelve hours later the requester replies, so `reopen()` cancels the pending schedule. When the sweeper reaches that fire-at time, it sees `cancelled=True` and sends nothing.
5. **Discuss tradeoffs.** "What if the survey system goes down for a day?" → schedules are durable (persisted via the Ch3 storage family, no new mechanism needed) and a sweep job can catch up. Naming that answer *is* the deliverable — no code needed to prove the design absorbs it.

**Invariant / tests.** A ticket reopened before its 24 hours never receives a survey. A ticket closed and left alone always does, exactly once.

**Cost / deferred.** The sweep job that actually sends overdue surveys is infrastructure, not a class — noted and left out of scope, same as Ch14 leaving "millions of users" as a named-not-solved tradeoff.

---

## Ch 15–17 · Three requirement waves: tiers, policies, escalation

*Pairs with: [Chapter 15](lld-chapter-15.md) · [Chapter 16](lld-chapter-16.md) · [Chapter 17](lld-chapter-17.md)*

These three chapters are worked problems in the book (Library, Shopping, Ride-sharing) — each demonstrating the ritual on a fresh domain rather than teaching a new pattern. Here, they land as three requirement waves on the *same* desk, which is closer to how a real system actually grows.

**Ch15 wave — support tiers (echoes Library's membership tiers).**

*Requirement.* "Basic customers share one queue. Premium customers get a dedicated queue and a faster SLA; if no Premium agent is free, a request can wait in line for the next one specifically, not just any agent."

*Failing pressure.* A single shared queue can't express "this customer's ticket should only ever go to a Premium-tier agent." Same shape as Library's Standard/Premium membership rules (max books, loan period) — different numbers, same idea of a tier object carrying its own rules.

*Smallest change.* `BasicTier`/`PremiumTier` classes carrying `queue_name` and `sla_minutes`; routing consults the requester's tier before choosing a queue.

*Invariant / tests.* A Premium requester's ticket never lands in the Basic queue, even when every Premium agent is busy — it waits, it doesn't downgrade itself.

*Cost / deferred.* No fairness guarantee yet if Premium volume spikes — noted, not solved.

**Ch16 wave — SLA policies as Strategy (echoes Shopping's payment/discount strategies).**

*Requirement.* "SLA response targets vary per contract: `FlatSLA` (fixed hours regardless of severity), `TieredSLA` (hours depend on severity), `CreditSLA` (one faster response per quarter, then falls back to Flat)."

*Smallest change.* An SLA family with one shared method, `response_target(ticket)`, exactly parallel to Shopping's `PercentageDiscount`/`FixedDiscount`/`NoDiscount`. Ticket status stays a simple state machine (already built in Ch7) — this wave is about *policy*, not lifecycle, so nothing here reopens the State work.

*Invariant / tests.* Swapping a customer's SLA policy never requires touching `Ticket` or `HelpDesk` — only which policy object gets attached to their account.

*Cost / deferred.* `CreditSLA`'s "once per quarter" counter isn't persisted separately yet — piggybacks on the Ch3 storage for now, flagged as a future its-own-class candidate if it grows more rules.

**Ch17 wave — matching, pricing, and a richer lifecycle (echoes Ride-sharing).**

*Requirement.* "Route a ticket to the *specific* best-available agent, not just 'someone on the team' — least-loaded, or highest customer-satisfaction-score among agents with the matching skill. Also: incident tickets need a richer internal lifecycle — Paged → Acknowledged → Mitigating → Resolved — layered under the general ticket lifecycle."

*Smallest change.* A `MatchingStrategy` family (parallel to Ride-sharing's `NearestDriverMatching`/`HighestRatedNearbyMatching`) replacing the plain team-level routing from Ch3–4 for incidents specifically. A second, incident-only state machine (`PagedState`, `AcknowledgedState`, `MitigatingState`) nested inside `IncidentTicket`, following the same forwarding shape as Ch7's general ticket states — justified *now* because, like Ride-sharing's `Trip`, the transitions are rich and asymmetric enough to earn it. `ServiceRequestTicket` doesn't get this — it never needed one.

*Invariant / tests.* An incident's inner state machine and the outer ticket lifecycle never contradict each other (e.g., the outer ticket can't be `Closed` while the inner incident state is still `Mitigating`).

*Cost / deferred.* Matching doesn't yet weigh agent timezone or working hours — named, deferred, same as Ride-sharing's own "doesn't consider timezone" gap.

---

## Ch 18 · Guarding, simplifying, and routing

*Pairs with: [Chapter 18](lld-chapter-18.md)*

**Requirement.** "Only the assigned agent or their manager may view or edit a ticket. Opening a ticket touches four systems — create the record, save it, notify, and log — hide that behind one call. A ticket's severity should determine who's offered it first: L1 agent, then L2, then the on-call engineer if it's unclaimed after N minutes."

**Failing pressure.** Three different pains, easy to conflate. "Who can even reach this ticket" is an access question. "How do I stop every caller from re-deriving the four-step open sequence" is a simplicity question. "Who eventually handles this, in order" is a routing-with-fallback question. Reaching for one wrapper shape to cover all three would blur exactly the distinction Ch18 spends its whole chapter earning.

**Smallest change.** Three small, purpose-built wrappers — Proxy, Facade, Chain of Responsibility, matched to their actual questions:

```python
class AuthorizedTicketView:              # Proxy — should this call happen at all?
    def __init__(self, ticket, viewer):
        self.ticket, self.viewer = ticket, viewer

    def _ensure_allowed(self, action):
        assigned_agent = self.ticket.agent
        assigned_manager = getattr(assigned_agent, "manager", None)
        if self.viewer not in (assigned_agent, assigned_manager):
            raise PermissionError(f"not authorized to {action} this ticket")

    def read(self):
        self._ensure_allowed("view")
        return self.ticket

    def edit(self, **changes):
        self._ensure_allowed("edit")
        for field, value in changes.items():
            setattr(self.ticket, field, value)
        return self.ticket


class HelpDeskFacade:                    # Facade — one simple call
    def __init__(self, help_desk):
        self.help_desk = help_desk

    def open_ticket(self, subject, requester):
        return self.help_desk.open_ticket(subject, requester)


class EscalationHandler:                 # Chain of Responsibility — who claims this?
    def __init__(self, tier_name, minimum_minutes, accepts):
        self.tier_name = tier_name
        self.minimum_minutes = minimum_minutes
        self.accepts = accepts
        self.next_handler = None

    def set_next(self, handler):
        self.next_handler = handler
        return handler

    def offer(self, ticket, minutes_unclaimed):
        if minutes_unclaimed >= self.minimum_minutes and self.accepts(ticket):
            return self.tier_name
        if self.next_handler is None:
            return None
        return self.next_handler.offer(ticket, minutes_unclaimed)


def accepts_l1(ticket):
    return getattr(ticket, "severity", 5) >= 3

def accepts_l2(ticket):
    return getattr(ticket, "severity", 5) >= 2

def accepts_on_call(ticket):
    return True
```

The facade looks almost too thin because `HelpDesk.open_ticket` already creates the record, saves it, and notifies the subscribed audit/logger listeners. That's the point: the facade delegates the one existing operation; it doesn't replay notification and logging side effects a second time.

**Invariant / tests.** An agent outside the ticket's team is denied by `AuthorizedTicketView` before ever touching ticket data — the proxy's check runs first, always, and an unassigned ticket doesn't crash while checking for a manager. The same proxy guards both `read()` and `edit()`. `HelpDeskFacade.open_ticket` delegates once, so "opened" notifications and audit logs happen once. The escalation chain returns the first tier whose elapsed-time gate has opened *and* whose acceptance rule matches the ticket's severity — never a tier that would reject the ticket.

**Cost / deferred.** The facade still delegates rather than reimplementing anything — the moment it starts *doing* ticket creation, persistence, notification, or logging itself, it's a God class wearing a Facade's name (Ch12's smell, reappearing here as a caution).

---

## Ch 19 · Picking the next ticket fast

*Pairs with: [Chapter 19](lld-chapter-19.md)*

**Requirement.** "Give me the single most urgent open ticket, in better than linear time — even as tickets get created, reprioritized, or resolved constantly."

**Failing pressure.** This is the chapter where no pattern helps and the data structure *is* the design, exactly like LRU. Feel the brute force first: a plain dict of tickets means finding "most urgent" is an O(n) scan every single time. A list kept sorted by urgency fixes the read but makes every insert or reprioritization an O(n) re-sort.

The two things pull apart the same way LRU's did: *"find this ticket fast"* wants a hash map; *"usually know the most-urgent one fast"* wants an ordered structure that gives you the extreme element cheaply. Neither alone is enough.

**Smallest change.** A **binary heap** keyed by `(severity, deadline)` for O(log n) push and live pop, plus a **hash map** from ticket id to the current version — because a plain heap has no cheap way to change or remove an *arbitrary* entry once it's buried in the middle. Rather than trying to fix that in-place, use lazy invalidation: reprioritizing or resolving a ticket bumps its version (and for reprioritizing pushes a fresh entry); popping skips stale entries until it finds a live one.

```
UrgentTicketQueue
  heap: [(severity, deadline, ticket_id, version), ...]   # O(log n) push/pop
  current_version: { ticket_id -> version }               # O(1) "is this entry live?"

pop_most_urgent():
    compact_if_heap_is_three_times_live_size()
    loop:
        severity, deadline, ticket_id, version = heap.pop_min()
        if current_version.get(ticket_id) == version:
            return ticket_id          # live — this is the real answer
        # else: stale entry from before a reprioritize/resolve — discard, loop again
```

**Invariant / tests.** Popping always returns a ticket that is actually still open at its current severity — no stale or duplicate entries ever survive a pop. Reprioritizing a ticket never requires scanning the heap; it only bumps a version number and pushes one new entry.

**Cost / deferred.** Lazy deletion moves cost; it doesn't erase it. One unlucky pop can discard many stale entries if the same ticket was reprioritized over and over. Across a long run, each stale entry was created by one earlier update and is discarded once, so the usual claim is **amortized** O(log n) per update/pop, not worst-case O(log n) for every individual pop. To keep memory and single-pop latency from drifting, compact when `len(heap) > 3 * len(current_version)`: rebuild the heap from only entries where `current_version.get(ticket_id) == version`. That rebuild is O(n), paid deliberately at the threshold.

---

## Ch 20 · Two agents, one ticket, one winner

*Pairs with: [Chapter 20](lld-chapter-20.md)*

**Requirement.** "Two agents both click 'claim' on the same unassigned ticket at the same instant. Exactly one should get it."

**Failing pressure.** The natural-looking code — "check the ticket is unassigned, then assign it to me" — is two separate steps. If two threads both pass the check before either writes, both believe they won. This is the exact race Ch20 built around movie seats, just with a ticket instead of a seat.

**Smallest change.** Add a runtime-only lock to the existing `Ticket` object, then guard the *span* from check to write as one atomic step — not just the write. A per-queue lock would also be correct, but a per-ticket lock preserves more parallelism when two agents claim different tickets.

```python
import threading


class TicketAlreadyClaimed(Exception):
    pass

class Ticket:
    def __init__(self, subject, requester):
        ...
        self.lock = threading.Lock()


class HelpDesk:
    def claim(self, ticket_id, agent):
        ticket = self.tickets[ticket_id]
        with ticket.lock:                       # check AND set, same critical section
            if ticket.agent is not None:
                raise TicketAlreadyClaimed(f"ticket {ticket_id} already has an owner")
            ticket.agent = agent
```

The lock has to wrap the read (`ticket.agent is not None`) and the write (`ticket.agent = agent`) together — a lock that only wraps the write still loses, because both threads can pass the check before either writes, exactly the trap Ch20 calls out explicitly.

**Invariant / tests.** Run two threads racing to claim the same ticket a thousand times (a `threading.Barrier` releases them together, same technique Ch20 used for the seat race) — exactly one winner every time, never two, never zero.

**Cost / deferred.** This lock only guards one process's memory. A helpdesk running on multiple servers needs the same atomicity enforced at the database — a row-level compare-and-set (`UPDATE tickets SET agent = ? WHERE id = ? AND agent IS NULL`) or a distributed lock — the identical shape, just relocated, same escalation Ch20 itself named for the seat-booking system.

---

## What the whole desk looks like now

Across twenty chapters of pressure, the system avoided a rewrite — but it did not avoid migrations. Two boundary contracts had to be made explicit: listeners now receive stable `TicketEvent` objects, and storage now serializes tickets/states into plain JSON records before reconstructing real objects. That's the honest thesis: small local moves work when you name the seams that must survive the next move.

```
HelpDeskFacade ──> HelpDesk
LoggingTicketOps ──> SupportRoleGuard ──> HelpDesk
                     │
                     ├── storage (Strategy)
                     ├── routing/matching (Strategy)
                     ├── listeners (Observer)
                     ├── UrgentTicketQueue (heap + map)
                     └── Ticket (State machine,
                         IncidentTicket / ServiceRequestTicket)

AuthorizedTicketView (read/edit proxy) ──> Ticket
Ticket ──> per-ticket lock guards claim()

EscalationHandler chain offers unclaimed tickets by severity and elapsed time.
```

Every box on that diagram earned its place by relieving a specific, named pain — not by being remembered from a catalog. If you can trace which chapter put each box there and why, you've done the thing this whole book is for.

---

<div align="right">

[Cold Rebuild Drills →](lld-cold-rebuild-drills.md) · [Appendix](lld-appendix.md) · [Contents](lld-README.md)

</div>
