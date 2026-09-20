# Chapter 10: Many patterns, one problem

*[← Chapter 9](lld-chapter-9.md) · [Contents](lld-README.md)*

- [ ] **Mark as read**

You've seen four patterns now: Strategy, Observer, State, Decorator. Plus the building block — putting state and behavior in classes. Plus Singleton and Factory as named tools. And in Chapter 9, the skeleton under all of them: modeling plain classes and relating them with inheritance and composition.

A real LLD problem doesn't use one pattern. It uses several — wired through a domain of plain classes. Knowing which pattern fits where is the actual skill.

Let's design a parking lot.

## The requirements

Read these the way an interviewer would say them. Then breathe.

- A parking lot has multiple floors. Each floor has multiple spots. Spots are different sizes (motorcycle, compact, large).
- A vehicle (motorcycle, car, truck) arrives. It needs an appropriate spot. Motorcycles fit anywhere; cars fit compact or large; trucks only fit large.
- The lot tracks which spots are occupied. When a vehicle leaves, calculate the parking fee based on duration.
- Pricing varies — flat hourly, or different rates for different vehicle types, or weekend pricing. The pricing policy should be configurable.
- When the lot is full, an alert should be sent.
- When a vehicle parks or leaves, gate operators should be notified.

A lot of pieces. Go one at a time.

## Step 1: The core entities

Before any pattern, sort the pile — the same plain-class modeling from the last chapter. Underline the nouns in the requirements: *parking lot, floor, spot, size, vehicle, fee*. Most are things with their own state and behavior, so they earn a class: a `ParkingLot` (holds floors, parks and frees vehicles), a `Floor` (holds spots, finds a free one), a `Spot` (knows if it's occupied, whether a vehicle fits), a `Vehicle`. But "size" is just one value a spot or vehicle *carries*, and "fee" is a single number — neither has behavior of its own, so they stay **attributes**, not classes.

Now the verbs, and who owns each one. *Does a vehicle fit? Is the spot occupied?* — those are questions a `Spot` answers about itself, so `can_fit(vehicle)` and `is_free()` live on `Spot`. *Park, leave, is the lot full?* — the `ParkingLot` orchestrates those. One verb stands apart: *calculate the fee*, which varies by policy. Park it on a separate pricing object for now — that's the first hint a pattern is coming, but don't name it yet.

Finally the relationships. A motorcycle *is a* vehicle, a car *is a* vehicle — a true `is-a`, so inheritance fits. Everything else is `has-a`: the lot *has* floors, a floor *has* spots, a spot *has* (at most one) vehicle. Sort that out and the skeleton writes itself.

```python
import time


class Vehicle:
    def __init__(self, license_plate, size):
        self.license_plate = license_plate
        self.size = size  # "motorcycle", "compact", "large"


class Motorcycle(Vehicle):
    def __init__(self, license_plate):
        super().__init__(license_plate, "motorcycle")


class Car(Vehicle):
    def __init__(self, license_plate):
        super().__init__(license_plate, "compact")


class Truck(Vehicle):
    def __init__(self, license_plate):
        super().__init__(license_plate, "large")
```

> 💡 **Python notes — inheritance and `super().__init__` (recap from Ch9)**
> `class Motorcycle(Vehicle):` says Motorcycle *is a* Vehicle — it inherits everything from Vehicle. `super().__init__(license_plate, "motorcycle")` calls the parent's `__init__` from inside the child's, setting the parent's attributes without rewriting that logic. This is a true `is-a` (a Motorcycle really is a kind of Vehicle), which is exactly when inheritance is the right call — see Chapter 9.
>
> `Vehicle` here is a textbook **abstract base class**: you never park a bare `Vehicle("ABC-123")` with no real size — only a `Motorcycle`, `Car`, or `Truck`. In a production design you'd write `class Vehicle(ABC)` (Chapter 9) so Python refuses to instantiate the bare base. We keep it a plain class here to keep the focus on the *patterns*, not the class machinery — but note that a plain `class Vehicle:` does **not** block `Vehicle(...)`; only `ABC` plus an `@abstractmethod` does.

```python
class Spot:
    SIZES = {"motorcycle": 1, "compact": 2, "large": 3}

    def __init__(self, spot_id, size):
        self.id = spot_id
        self.size = size
        self.vehicle = None
        self.parked_at = None

    def is_free(self):
        return self.vehicle is None

    def can_fit(self, vehicle):
        return self.SIZES[vehicle.size] <= self.SIZES[self.size]

    def park(self, vehicle):
        self.vehicle = vehicle
        self.parked_at = time.time()

    def leave(self):
        vehicle = self.vehicle
        duration = time.time() - self.parked_at
        self.vehicle = None
        self.parked_at = None
        return vehicle, duration


class Floor:
    def __init__(self, floor_number, spots):
        self.number = floor_number
        self.spots = spots

    def find_free_spot(self, vehicle):
        for spot in self.spots:
            if spot.is_free() and spot.can_fit(vehicle):
                return spot
        return None
```

Plain classes. State and behavior. No patterns yet — exactly the modeling from Chapter 9.

## Step 2: Pricing — which pattern?

*"Pricing varies. Flat hourly, or different rates per vehicle type, or weekend pricing. Configurable."*

Multiple algorithms. Caller picks one. **Strategy.**

```python
class FlatHourlyPricing:
    def __init__(self, rate_per_hour):
        self.rate = rate_per_hour

    def calculate(self, vehicle, duration_seconds):
        hours = duration_seconds / 3600
        return self.rate * hours


class PerVehicleTypePricing:
    def __init__(self, rates):
        self.rates = rates  # {"motorcycle": 2, "compact": 4, "large": 8}

    def calculate(self, vehicle, duration_seconds):
        hours = duration_seconds / 3600
        return self.rates[vehicle.size] * hours
```

## Step 3: The full alert — which pattern?

*"When the lot is full, an alert is sent. When a vehicle parks or leaves, gate operators are notified."*

Multiple listeners reacting to events. **Observer.**

```python
class EmailAlerter:
    def handle(self, event, data):
        print(f"EMAIL: {event} — {data}")


class DashboardAlerter:
    def handle(self, event, data):
        print(f"DASHBOARD: {event} — {data}")


class GateOperatorNotifier:
    def handle(self, event, data):
        if event in ("vehicle_parked", "vehicle_left"):
            print(f"GATE: {event} — {data}")
```

## Step 4: Wire it up

```python
class ParkingLot:
    def __init__(self, floors, pricing):
        self.floors = floors
        self.pricing = pricing
        self.listeners = []

    def subscribe(self, listener):
        self.listeners.append(listener)

    def _notify(self, event, data):
        for listener in self.listeners:
            listener.handle(event, data)

    def park(self, vehicle):
        for floor in self.floors:
            spot = floor.find_free_spot(vehicle)
            if spot:
                spot.park(vehicle)
                self._notify("vehicle_parked", {"vehicle": vehicle.license_plate, "spot": spot.id})
                if self._is_full():
                    self._notify("lot_full", {})
                return spot
        return None

    def leave(self, license_plate):
        for floor in self.floors:
            for spot in floor.spots:
                if spot.vehicle and spot.vehicle.license_plate == license_plate:
                    vehicle, duration = spot.leave()
                    fee = self.pricing.calculate(vehicle, duration)
                    self._notify("vehicle_left", {"vehicle": license_plate, "fee": fee})
                    return fee
        return None

    def _is_full(self):
        for floor in self.floors:
            for spot in floor.spots:
                if spot.is_free():
                    return False
        return True
```

Usage:

```python
spots = [Spot(1, "motorcycle"), Spot(2, "compact"), Spot(3, "large")]
floor_1 = Floor(1, spots)
pricing = PerVehicleTypePricing({"motorcycle": 2, "compact": 4, "large": 8})

lot = ParkingLot([floor_1], pricing)
lot.subscribe(EmailAlerter())
lot.subscribe(GateOperatorNotifier())

lot.park(Car("ABC-123"))
# GATE: vehicle_parked — ...

lot.leave("ABC-123")
# GATE: vehicle_left — ...
```

## What you just did

Built a system with:
- **Inheritance** for vehicle types
- **Strategy** for pricing (swappable)
- **Observer** for notifications
- **Plain composition** for floors → spots → vehicles

Notice what you *didn't* need: State (no lifecycle changes in the lot itself), Decorator (no wrapping behavior).

The skill in LLD interviews is exactly this: read requirements, identify the parts, name the pattern (if any) for each part, write it.

## The pattern recognition cheat sheet

When reading requirements, ask:

| Smell | Pattern |
|---|---|
| "X can be done multiple ways, caller picks" | **Strategy** |
| "When X happens, multiple things should react" | **Observer** |
| "Behavior depends on the object's mode/phase/status" | **State** |
| "Add behavior on top of existing objects without changing them" | **Decorator** |
| "Build configured objects without exposing construction details" | **Factory** |
| "Exactly one of these should ever exist" | **Singleton** |

Not every requirement maps to a pattern. Most don't. Patterns are tools for specific problems, not the default mode of writing code.

## Before you turn the page

**Exercise 1:** Add weekend pricing. Implement `WeekendPricing(weekday_strategy, weekend_strategy)` — a pricing strategy that delegates to one or the other based on the current day. *Strategy that contains Strategies.* Notice the shape.

**Exercise 2:** Add a maintenance mode for spots. A spot can be Free, Occupied, or Maintenance. When in Maintenance, it can't be parked in. You've done this pattern before. Implement it.

**Exercise 3:** Look at `park`. It loops through floors, looks for a spot. What if the lot has 10,000 spots? Search gets slow. What's a different way to *find* a spot? (Hint: index. Keep a dict of free spots by size. Update on park/leave.)

This last exercise isn't about patterns — it's about data structures. LLD interviews care about both. Patterns give organization. Data structures give performance.

---

<div align="right">

[Chapter 11 →](lld-chapter-11.md)

</div>
