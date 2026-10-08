# Chapter 20: Worked problem — Movie ticket booking

*[← Chapter 19](lld-chapter-19.md) · [Contents](lld-README.md)*

- [ ] **Mark as read**

The last worked problem, and like the last one it has a single crux — but a different one. Chapter 19's difficulty was the data structure. Here it's **concurrency**: two people must never walk away with the same seat. Get that right and everything else is ordinary modeling.

The problem: *"Design a movie ticket booking system like BookMyShow. Users browse shows, pick specific seats, and pay. The hard part: when two users grab the same seat at the same instant, exactly one of them wins."*

## Step 1: Clarify

- Single theater or a chain? **Single multiplex with several screens, for now.**
- What's bookable? **A Show = a movie on a screen at a start time. Each show has its own seats.**
- Seat selection? **Users pick specific seats, not just a count.**
- The race — what should happen when two users pick the same seat? **Exactly one succeeds; the other is told it's taken.**
- Hold during payment? **Yes. Selecting seats holds them for a few minutes while the user pays. If payment doesn't complete, the hold expires and the seats free up.**
- Payment? **A step that can succeed or fail; on failure the holds are released.**
- Pricing? **Per seat type — regular vs premium. Surge is a later tradeoff.**

Scope locked. The seat lifecycle is **AVAILABLE → HELD → BOOKED**, with an expired hold falling back to AVAILABLE.

## Step 2: Entities

- **Movie** — title, duration.
- **Screen** — a hall with a fixed seat layout.
- **Show** — a movie on a screen at a time; owns its seats.
- **Seat** — id, type, price, status, who holds it, when the hold expires.
- **Booking** — a user, a show, the seats, the total amount, confirmed or not.
- **BookingService** — orchestrates hold → pay → confirm.

Patterns I'm spotting:
- Pricing by seat type → **Strategy** (Ch3), trivial for now.
- Seat status → an **Enum**; could grow into **State** (Ch7) if transitions get rich.
- The real work isn't a pattern at all — it's a **lock**. Hold that thought.

## Step 3: Class diagram (verbal sketch)

```
BookingService
  ◇── many Bookings
  drives: hold_seats() -> confirm()

Show
  has Movie
  ◆── many Seats   (keyed by seat id)
  has a Lock       (guards this show's seats)

Seat
  status: AVAILABLE / HELD / BOOKED
  held_by, hold_expires_at

Booking
  has User, Show, [Seats], amount, confirmed
```

The load-bearing decision is that tiny "has a Lock" on `Show`. Let's earn it.

## Step 4: Code skeleton

Start with the entities, which are unremarkable:

```python
import threading
import time
from enum import Enum


class SeatStatus(Enum):
    AVAILABLE = "available"
    HELD = "held"
    BOOKED = "booked"


class Seat:
    def __init__(self, seat_id, seat_type, price):
        self.id = seat_id
        self.type = seat_type          # "regular" / "premium"
        self.price = price
        self.status = SeatStatus.AVAILABLE
        self.held_by = None
        self.hold_expires_at = 0

    def is_free(self, now):
        if self.status == SeatStatus.AVAILABLE:
            return True
        # a hold that has timed out is effectively free again (lazy expiry)
        return self.status == SeatStatus.HELD and now > self.hold_expires_at


class Show:
    def __init__(self, show_id, movie, seats):
        self.id = show_id
        self.movie = movie
        self.seats = {s.id: s for s in seats}
        self.lock = threading.Lock()   # one lock guards this show's seats


class Booking:
    def __init__(self, booking_id, user, show, seats):
        self.id = booking_id
        self.user = user
        self.show = show
        self.seats = seats
        self.amount = sum(s.price for s in seats)
        self.confirmed = False
```

Now the part that matters. The dangerous operation is "check the seats are free, then mark them mine." If two threads run the check at the same time, both see the seat free, both mark it — double booking. The check and the mark have to be **one atomic step**. That's what the show's lock is for.

```python
class SeatUnavailable(Exception):
    pass


class BookingService:
    HOLD_SECONDS = 300

    def __init__(self):
        self.bookings = []

    def hold_seats(self, show, seat_ids, user, now=None):
        now = time.time() if now is None else now
        with show.lock:                          # the critical section
            seats = [show.seats[sid] for sid in seat_ids]
            # all-or-nothing: every requested seat must be free
            for seat in seats:
                if not seat.is_free(now):
                    raise SeatUnavailable(f"seat {seat.id} is taken")
            for seat in seats:
                seat.status = SeatStatus.HELD
                seat.held_by = user
                seat.hold_expires_at = now + self.HOLD_SECONDS
            return seats

    def confirm(self, show, seat_ids, user, payment_ok, now=None):
        now = time.time() if now is None else now
        with show.lock:
            seats = [show.seats[sid] for sid in seat_ids]
            for seat in seats:
                if seat.status != SeatStatus.HELD or seat.held_by != user:
                    raise SeatUnavailable(f"seat {seat.id} hold lost")
                if now > seat.hold_expires_at:
                    raise SeatUnavailable(f"seat {seat.id} hold expired")
            if not payment_ok:
                for seat in seats:                # release on payment failure
                    seat.status = SeatStatus.AVAILABLE
                    seat.held_by = None
                raise SeatUnavailable("payment failed; holds released")
            for seat in seats:
                seat.status = SeatStatus.BOOKED
            booking = Booking(len(self.bookings), user, show, seats)
            booking.confirmed = True
            self.bookings.append(booking)
            return booking
```

> 💡 **Concept note — the check and the change must share the lock**
> The bug isn't fixed by locking "the seat." It's fixed by putting *both* the read (`is_free`) and the write (`status = HELD`) inside the *same* `with show.lock:` block. A lock that only wraps the write still loses: two threads pass the check, then take turns writing, and the second silently overwrites the first. Atomicity is about the *span* — check-and-set together — not about touching a lock at some point.

## Step 5: Walk a flow

The flow that actually tests the design is two users racing for one seat. We force maximum contention with a barrier so both threads hit `hold_seats` together.

```python
import threading

movie = "Dune"
show = Show(1, movie, [Seat("A1", "premium", 15), Seat("A2", "regular", 10)])
service = BookingService()

results = []
start = threading.Barrier(2)

def grab(user):
    start.wait()                 # release both threads at the same instant
    try:
        service.hold_seats(show, ["A1"], user)
        results.append((user, "got it"))
    except SeatUnavailable:
        results.append((user, "missed"))

t1 = threading.Thread(target=grab, args=("alice",))
t2 = threading.Thread(target=grab, args=("bob",))
t1.start(); t2.start()
t1.join(); t2.join()

# exactly one "got it", exactly one "missed"
print(results)
```

Run it and exactly one of Alice or Bob gets the seat; the other is told it's taken. Run it a thousand times and the count never drifts — never two winners, never zero. That invariant is the entire product, and it rests on the span of one `with show.lock:`.

## Step 6: Tradeoffs

- **"This is one process. What about many servers?"** → A `threading.Lock` only coordinates threads sharing this process's memory; every other process has a different lock. Put the invariant where every writer meets: prefer a database constraint, conditional update/compare-and-set, or row lock at the shared store. A distributed lock is a separate lease-based coordination system—not a mutex that simply "moves" to Redis—and needs expiry, ownership, and usually fencing against a paused old holder. Use it only when the store cannot enforce the invariant directly.

- **"Lock granularity?"** → One lock per *show* lets different shows book in parallel while keeping each show's seats consistent. A single global lock would be correct but serialize the whole system. Per-*seat* locks allow even more parallelism but invite deadlock when a booking spans several seats — acquire them in a fixed order (e.g., sorted by id) to stay safe (appendix C).

- **"Holds that never get paid?"** → Here expiry is *lazy*: a stale hold is treated as free the next time someone checks. Simple and correct, but the seat looks taken on the seat map until then. A background sweeper that flips expired holds back to AVAILABLE frees them promptly — at the cost of another moving part.

- **"Surge / dynamic pricing."** → Pull price out of the seat into a **PricingStrategy** (Ch3): regular, premium, surge. A surge calculator could be an **Observer** (Ch5) watching how full the show is.

- **"Waitlist when sold out."** → **Observer** again: when a hold expires and a seat frees, notify the next person in line.

- **"Idempotent confirm."** → If `confirm` is retried after a network blip, guard against double-charging — key the booking on a request id and return the existing booking on replay.

## Pattern audit

Used:
- **Plain classes** — Movie, Seat, Show, Booking.
- **Enum** — seat status (state-like, but the per-state behavior is thin, so an enum beats the full State pattern here).
- **A per-show `Lock`** — the concurrency primitive from appendix C. This is the design.

Could be added (when the follow-ups ask):
- **Strategy** — pricing (regular / premium / surge).
- **State** — if seat or booking transitions grow rich and asymmetric (compare the Trip in Ch17).
- **Observer** — waitlist notifications, surge.
- **Facade** — a `BookingFacade` over hold → pay → confirm, so callers make one call (Ch18).

The crux here was not a pattern. It was choosing a lock and its granularity, and getting the critical section's *span* right. Like Chapter 19, the strongest answer leads with the real mechanism and keeps the patterns in reserve.

---

You've now done six worked problems across two flavors: object-modeling (Splitwise, Library, Shopping, Ride-sharing), a data-structure-driven one (LRU), and a concurrency-driven one (booking). The test that matters now is the cold one: pick a problem you *haven't* seen — food delivery, a chess game, a file system, a parking garage you haven't read — set a 25-minute timer, and run the full ritual. If what you produce resembles these chapters, you're interview-ready.

The appendix that follows is a reference — a pattern catalog, concurrency basics, and common pitfalls. Reach for it after you've internalized the chapters, not as study material.

For the production version of this boundary—repository contracts, optimistic versions, concurrent tests, and why a fake is not enough—continue with the [boundaries and testing companion](lld-boundaries-and-testing.md).

---

<div align="right">

[Appendix →](lld-appendix.md)

</div>
