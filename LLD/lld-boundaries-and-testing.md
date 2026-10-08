# Companion: Boundaries, dependencies, and tests that prove the design

*[Contents](lld-README.md) · [Code evolution](lld-code-evolution.md) · [Cold rebuild drills](lld-cold-rebuild-drills.md) · [Appendix](lld-appendix.md)*

The chapters teach objects and patterns by making one requirement hurt at a time. This companion zooms in on the seam Chapter 3 created and Chapter 11 named: **business code should depend on a small contract, while databases, APIs, clocks, and queues stay outside that boundary.**

This is not another pattern catalog and not a framework tutorial. It is one small order-reservation example evolved through:

- boundaries and responsibility;
- dependency injection;
- ports and adapters;
- repositories;
- explicit error contracts;
- unit, integration, contract, and concurrency tests;
- fakes versus mocks;
- optimistic locking.

The sequence remains the same as the rest of the primer: start with code that works, feel why it is hard to change or prove, then make the smallest boundary that relieves that pain.

---

## 1. Start with the coupled version

The requirement sounds small: reserve stock for an order.

```python
class ReservationService:
    def reserve(self, order_id, sku, quantity):
        connection = connect_to_postgres()
        row = connection.execute(
            "SELECT available FROM inventory WHERE sku = %s",
            (sku,),
        ).fetchone()
        if row["available"] < quantity:
            raise ValueError("not enough stock")
        connection.execute(
            "UPDATE inventory SET available = available - %s WHERE sku = %s",
            (quantity, sku),
        )
        requests.post(
            "https://events.internal/reservations",
            json={"order_id": order_id, "sku": sku, "quantity": quantity},
        )
```

It works in production, but answering basic questions is painful:

- Can the reservation rule be tested without Postgres and HTTP?
- If event publishing fails after the update, what does the caller observe?
- Is "not enough stock" a stable domain outcome or a string some client parses?
- Can storage move without rewriting the rule?
- Can two requests reserve the same last unit?

The class has crossed three boundaries at once: domain decision, persistence, and messaging. The problem is not that SQL or HTTP are bad. The problem is that the core rule cannot be exercised or reasoned about without them.

---

## 2. Draw the boundary before choosing the abstraction

First decide what belongs inside.

```text
inside: reservation use case
  - validate quantity
  - load stock
  - decide whether reservation is allowed
  - record the new state
  - report a stable outcome

outside:
  - SQL driver and schema
  - HTTP/event broker client
  - system clock
  - framework request/response objects
```

A useful boundary owns a business invariant and exposes a small vocabulary. It is not "one folder per technical layer" by reflex, and it does not require every class to have an interface.

> 💡 **Boundary test**
> Describe the use case without a vendor noun. "Reserve inventory if enough remains" is inside. "Run this Postgres query" and "POST this JSON" are adapters outside. If the domain sentence changes, the use case probably changes. If a vendor, protocol, or framework changes, an adapter should absorb it.

---

## 3. Dependency injection: pass collaborators in

The first small move is the same one Chapter 3 made for storage: stop constructing dependencies inside the service.

```python
class ReservationService:
    def __init__(self, inventory, events):
        self.inventory = inventory
        self.events = events

    def reserve(self, order_id, sku, quantity):
        item = self.inventory.get(sku)
        item.reserve(quantity)
        self.inventory.save(item)
        self.events.publish(
            "InventoryReserved",
            {"order_id": order_id, "sku": sku, "quantity": quantity},
        )
```

This is **dependency injection**: construction happens at the edge, use happens inside.

```python
service = ReservationService(
    inventory=PostgresInventoryRepository(connection),
    events=BrokerEventPublisher(producer),
)
```

Benefits:

- tests can supply controlled collaborators;
- configuration chooses implementations without branching inside the use case;
- lifecycle is explicit (one connection pool, one publisher);
- business code no longer imports infrastructure constructors.

Injection does not mean "use a dependency-injection framework." Constructor parameters are enough until object wiring becomes genuinely repetitive.

Avoid the service-locator disguise:

```python
class ReservationService:
    def reserve(self, ...):
        inventory = GlobalContainer.resolve("inventory")  # dependency is hidden again
```

The call site looks parameter-free, but tests and readers still have to discover global state.

---

## 4. Ports and adapters: name the direction

Dependency injection creates a seam. **Ports and adapters** explains its direction.

```text
                     incoming adapter
                 HTTP / CLI / message handler
                            |
                            v
                   ReservationService
                   (application core)
                     /             \
            outgoing port      outgoing port
          InventoryRepository   EventPublisher
                 |                    |
          Postgres adapter       broker adapter
```

- A **port** is a contract the application exposes or needs.
- An **adapter** translates a concrete technology into that contract.
- **Incoming adapters** translate HTTP, CLI, jobs, or messages into use-case calls.
- **Outgoing adapters** translate repository/publisher calls into SQL, broker APIs, or remote services.

The dependency arrows point inward: adapters know the application contract; the application does not know adapter details.

In Python, a `Protocol` can make the contract explicit without forcing inheritance:

```python
from typing import Protocol


class InventoryRepository(Protocol):
    def get(self, sku: str) -> "InventoryItem":
        ...

    def save(self, item: "InventoryItem") -> None:
        ...


class EventPublisher(Protocol):
    def publish(self, event_type: str, payload: dict) -> None:
        ...
```

Keep ports shaped around the use case. A generic `Database` port with `execute(sql)` leaks persistence decisions inward; `InventoryRepository.get/save` speaks the domain's language.

### An adapter should translate both ways

```python
class PostgresInventoryRepository:
    def __init__(self, connection):
        self.connection = connection

    def get(self, sku):
        row = self.connection.execute(
            "SELECT sku, available, version FROM inventory WHERE sku = %s",
            (sku,),
        ).fetchone()
        if row is None:
            raise InventoryItemNotFound(sku)
        return InventoryItem(
            sku=row["sku"],
            available=row["available"],
            version=row["version"],
        )

    def save(self, item):
        # The optimistic-locking form arrives later.
        self.connection.execute(
            "UPDATE inventory SET available = %s WHERE sku = %s",
            (item.available, item.sku),
        )
```

Rows stay outside; domain objects stay inside. Database-specific exceptions should also be translated at this edge rather than leaking into controllers and use cases.

---

## 5. Repositories: collection-shaped persistence

A **repository** presents persisted domain objects as though they came from a collection:

```python
item = inventory.get("PEN-BLUE")
item.reserve(2)
inventory.save(item)
```

It owns:

- mapping between storage records and domain objects;
- query details needed by the use case;
- persistence-specific exception translation;
- concurrency metadata such as a version.

It should not own:

- whether a reservation is allowed;
- HTTP status codes;
- email formatting;
- an ever-growing generic query language "for flexibility."

One repository usually aligns with an **aggregate**—the consistency boundary changed together. It need not mirror one database table, and every table does not automatically deserve a repository.

> 💡 **Repository vs DAO**
> A DAO often exposes storage-shaped operations and rows. A repository exposes domain-shaped objects and queries. Both can be valid; the important test is whether persistence details cross into the business rule. Do not rename a SQL wrapper "repository" and call the boundary finished.

---

## 6. Error contracts: failures are part of the API

The initial code raises `ValueError("not enough stock")`. That message is not a stable contract. Define failures callers can classify without parsing prose.

```python
class ReservationError(Exception):
    pass


class InvalidQuantity(ReservationError):
    def __init__(self, quantity):
        super().__init__(f"quantity must be positive, got {quantity}")
        self.quantity = quantity


class InventoryItemNotFound(ReservationError):
    def __init__(self, sku):
        super().__init__(f"inventory item {sku!r} not found")
        self.sku = sku


class InsufficientStock(ReservationError):
    def __init__(self, sku, requested, available):
        super().__init__(
            f"requested {requested} of {sku}, only {available} available"
        )
        self.sku = sku
        self.requested = requested
        self.available = available


class ConcurrentModification(ReservationError):
    def __init__(self, sku):
        super().__init__(f"inventory item {sku!r} changed concurrently")
        self.sku = sku
```

The domain object enforces its invariant:

```python
from dataclasses import dataclass


@dataclass
class InventoryItem:
    sku: str
    available: int
    version: int = 0

    def reserve(self, quantity):
        if quantity <= 0:
            raise InvalidQuantity(quantity)
        if self.available < quantity:
            raise InsufficientStock(self.sku, quantity, self.available)
        self.available -= quantity
```

An incoming HTTP adapter translates domain outcomes into transport outcomes:

```text
InvalidQuantity       -> 400 Bad Request
InventoryItemNotFound -> 404 Not Found
InsufficientStock     -> 409 Conflict
ConcurrentModification-> retry briefly, then 409 Conflict
unexpected failure    -> 500 + internal trace id, no internals leaked
```

The core does not raise `HTTPException(409)`: HTTP is one adapter. A message consumer may retry or dead-letter the same domain error differently.

Document whether each operation is:

- successful;
- rejected by a business rule;
- retryable because of concurrency or a transient dependency;
- indeterminate because a remote effect may have happened;
- failed permanently.

That classification is more useful than one catch-all exception hierarchy.

---

## 7. Tests form layers because boundaries fail differently

No single test style proves the design. Use the smallest layer that can reveal the failure.

### Unit tests: prove business rules in memory

```python
def test_reserve_reduces_available_stock():
    item = InventoryItem("PEN-BLUE", available=5)

    item.reserve(2)

    assert item.available == 3


def test_reserve_rejects_more_than_available():
    item = InventoryItem("PEN-BLUE", available=1)

    try:
        item.reserve(2)
        assert False, "expected InsufficientStock"
    except InsufficientStock as error:
        assert error.available == 1
        assert item.available == 1
```

Fast, deterministic, no adapters. These prove the invariant, not the wiring.

### Integration tests: prove a real adapter

Run `PostgresInventoryRepository` against a real disposable Postgres database:

- migrations create the expected schema;
- rows map to domain objects and back;
- transactions roll back correctly;
- constraints and optimistic updates behave as assumed;
- real driver types, time zones, and error codes are translated.

Mocking the SQL driver does not prove SQL syntax or transaction behavior. That belongs in an integration test.

### Contract tests: every adapter obeys the same port

A reusable suite describes repository behavior:

```python
def repository_contract(repository_factory):
    repository = repository_factory()
    original = InventoryItem("PEN-BLUE", available=5)
    repository.add(original)

    loaded = repository.get("PEN-BLUE")
    assert loaded == original

    loaded.reserve(2)
    repository.save(loaded)
    assert repository.get("PEN-BLUE").available == 3
```

Run it against the in-memory fake and the Postgres adapter. The fake is useful only if it shares observable semantics: missing-item behavior, identity/copy behavior, version conflicts, and transaction visibility where the tests depend on them.

Contract tests do not prove two systems have identical internals. They prove the behavior the application relies upon.

### Concurrency tests: force the dangerous interleaving

A normal unit test rarely races at the right instant. Use barriers/latches to line contenders up, then assert the invariant:

```text
two services load version 7
  -> release both saves together
  -> exactly one save of expected version 7 succeeds
  -> the other receives ConcurrentModification
  -> total stock reflects one reservation, never an overwrite
```

Run the same scenario against the real adapter. A fake protected by one Python lock can accidentally hide a database bug.

Concurrency tests increase confidence; they do not prove every schedule. Make the critical interleaving deliberate rather than relying on sleeps.

---

## 8. Fakes and mocks answer different questions

### Fake: a working lightweight implementation

```python
from copy import deepcopy


class InMemoryInventoryRepository:
    def __init__(self, items=()):
        self.items = {item.sku: deepcopy(item) for item in items}

    def get(self, sku):
        if sku not in self.items:
            raise InventoryItemNotFound(sku)
        return deepcopy(self.items[sku])

    def save(self, item):
        self.items[item.sku] = deepcopy(item)
```

Use a fake when the test cares about resulting state and several operations should behave coherently. Returning deep copies matters: returning the stored object directly would let mutation "persist" without `save`, unlike a real database.

### Mock/spy: records an interaction

```python
class RecordingEvents:
    def __init__(self):
        self.published = []

    def publish(self, event_type, payload):
        self.published.append((event_type, payload))
```

Use a mock or spy when the interaction itself is the contract: "publish one `InventoryReserved` event after a successful save." Avoid asserting every internal call in sequence; those tests freeze implementation rather than behavior.

Rules of thumb:

- Prefer plain domain objects for pure rules.
- Prefer a fake for stateful collaborators.
- Prefer a stub for one controlled response.
- Prefer a spy/mock for an important outgoing interaction.
- Use the real adapter in integration and concurrency tests.
- If a test needs ten mocks, reconsider the use-case boundary before adding the eleventh.

---

## 9. The race that injection does not solve

Two service instances can both load `available = 1`:

```text
service A loads available=1, version=7
service B loads available=1, version=7
A reserves -> available=0
B reserves -> available=0
A saves
B saves
both report success; one reservation was lost
```

Good object boundaries made the rule testable, but they did not make a multi-process update atomic.

An in-process `threading.Lock()` protects threads sharing one Python process. It does **not** coordinate:

- another worker process;
- another app server;
- an admin tool writing the same row;
- a job consuming the same stock.

The invariant must be enforced where all writers meet: the persistent store.

---

## 10. Optimistic locking: detect stale writes with a version

Optimistic locking assumes conflicts are uncommon. Read a version, then update only if the stored version is still the one you read:

```sql
UPDATE inventory
SET available = :available,
    version = version + 1
WHERE sku = :sku
  AND version = :expected_version;
```

If the update count is zero, someone changed the row first. The repository translates that outcome:

```python
class PostgresInventoryRepository:
    def save(self, item):
        changed = self.connection.execute(
            """
            UPDATE inventory
            SET available = %s, version = version + 1
            WHERE sku = %s AND version = %s
            """,
            (item.available, item.sku, item.version),
        ).rowcount
        if changed != 1:
            raise ConcurrentModification(item.sku)
        item.version += 1
```

The use case decides what to do:

- retry a small number of times by reloading and reapplying the command;
- surface a conflict so the caller can refresh;
- never blindly repeat a non-idempotent remote side effect.

```python
class ReservationService:
    def __init__(self, inventory, events, max_conflict_retries=2):
        self.inventory = inventory
        self.events = events
        self.max_conflict_retries = max_conflict_retries

    def reserve(self, order_id, sku, quantity):
        for attempt in range(self.max_conflict_retries + 1):
            item = self.inventory.get(sku)
            item.reserve(quantity)
            try:
                self.inventory.save(item)
                break
            except ConcurrentModification:
                if attempt == self.max_conflict_retries:
                    raise
        self.events.publish(
            "InventoryReserved",
            {"order_id": order_id, "sku": sku, "quantity": quantity},
        )
```

This simple form still has a dual-write gap between repository save and event publish. In a production event-driven system, the repository transaction would save the item and an outbox record together; the HLD [multi-region and event-driven drills](../HLD/hld-multi-region-event-driven-drills.md) exercise that system boundary.

### Optimistic vs pessimistic

- **Optimistic version check:** no lock while thinking; detect conflict at write. Good when contention is low and retry is cheap.
- **Pessimistic row lock:** lock the selected row during a transaction. Good when contention is high or the operation spans reads/writes that must serialize; costs waiting and risks deadlock.
- **Atomic conditional update:** encode the invariant directly, e.g. `UPDATE ... SET available = available - :q WHERE available >= :q`. Often the smallest and safest solution.
- **Distributed lock/lease:** coordinate through a shared service only when the store cannot enforce the invariant. Requires expiry, ownership, and stale-holder protection.

Do not replace every in-process lock with a distributed lock. First ask where the shared state lives and whether that store can enforce the condition atomically.

---

## 11. Composition root: keep wiring at the edge

Something must choose concrete adapters. Put that choice in one obvious place—the **composition root**:

```python
def build_reservation_handler(config):
    connection = build_connection_pool(config.database_url)
    producer = build_event_producer(config.broker_url)

    repository = PostgresInventoryRepository(connection)
    events = BrokerEventPublisher(producer)
    service = ReservationService(repository, events)
    return ReservationHttpHandler(service)
```

Framework handlers should translate and delegate:

```text
HTTP request
  -> parse/authenticate/validate transport shape
  -> call ReservationService
  -> translate result/error to HTTP response
```

Business decisions do not belong in the controller, and status codes do not belong in the domain object.

---

## 12. What to test for one complete flow

For `reserve(order_id, sku, quantity)`, a balanced suite might be:

**Unit**
- positive quantity reduces available stock;
- zero/negative quantity is rejected;
- insufficient stock preserves state;
- successful use case publishes the expected domain event;
- rejected reservation publishes nothing;
- conflict retries are bounded.

**Repository contract**
- add/get/save round trip;
- missing item raises `InventoryItemNotFound`;
- stale version raises `ConcurrentModification`;
- returned objects do not mutate stored state until saved.

**Integration**
- real migrations and Postgres mapping;
- update count detects stale versions;
- transaction rollback preserves inventory;
- outbox row and inventory change commit or roll back together, if outbox is used.

**Concurrency**
- two contenders for the last unit produce exactly one success;
- many contenders never drive stock below zero;
- retries do not publish duplicate business effects.

**Incoming-adapter**
- error-to-status mapping;
- authentication/authorization;
- request/idempotency key parsing;
- no internal exception details leak.

Testing follows the boundaries: pure rules close to the core, technology assumptions at adapters, and races at the shared store.

---

## 13. Interview drill

Prompt: *"Design the classes for reserving limited stock during checkout."*

In 25 minutes:

1. Clarify whether one process or many servers write stock.
2. Name the invariant: available never below zero; one order reservation applied once.
3. Model `InventoryItem` behavior without infrastructure.
4. Introduce `InventoryRepository` only when persistence arrives.
5. Inject it into `ReservationService`; keep construction at the edge.
6. Define domain errors and adapter translations.
7. Choose atomic conditional update, optimistic versioning, or row lock from contention—not fashion.
8. Name one unit, integration, contract, and concurrency test.
9. Explain why `threading.Lock()` is sufficient for one process and insufficient for many.
10. Add event publication only after naming the DB/event atomicity gap.

**Strong-answer signal:** the candidate leads with the invariant and shared-state boundary, not a pattern name.

---

## Review checklist

Before calling a design complete:

- [ ] The use case can be described without vendor/framework nouns.
- [ ] Dependencies are visible constructor/method parameters.
- [ ] Ports use domain language and stay small.
- [ ] Adapters translate records, protocols, and infrastructure errors.
- [ ] Repositories align with a consistency boundary, not automatically with tables.
- [ ] Domain failures are typed/classifiable; callers do not parse strings.
- [ ] HTTP/broker details stay in incoming/outgoing adapters.
- [ ] Unit tests prove rules without infrastructure.
- [ ] Integration tests exercise real technology behavior.
- [ ] Contract tests run against each adapter where substitutability matters.
- [ ] Concurrency tests force the contested interleaving at the shared store.
- [ ] Fakes preserve relevant semantics; mocks assert only important interactions.
- [ ] In-process locks are not presented as cross-process coordination.
- [ ] Optimistic conflicts have a bounded retry or visible conflict outcome.
- [ ] External side effects are not repeated casually on conflict retry.
- [ ] Object wiring has one discoverable composition root.

---

## The bumper sticker

> *A boundary earns its keep when the rule is testable without the tool, the adapter is replaceable without rewriting the rule, and the shared store—not an imaginary global mutex—enforces cross-process invariants.*

<div align="right">

[Code evolution →](lld-code-evolution.md) · [Appendix →](lld-appendix.md) · [Contents](lld-README.md)

</div>
