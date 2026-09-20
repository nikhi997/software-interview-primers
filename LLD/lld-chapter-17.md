# Chapter 17: Worked problem — Ride-sharing

*[← Chapter 16](lld-chapter-16.md) · [Contents](lld-README.md)*

- [ ] **Mark as read**

The problem: *"Design a ride-sharing system like Uber. Riders request rides, drivers accept, trips happen, both rate each other."*

## Step 1: Clarify

- Single rider or pool? **Single rider, single driver per trip for now.**
- Pricing? **Distance + time + surge multiplier.**
- Matching? **Nearest available driver.**
- Trip states? **Requested → DriverAssigned → InProgress → Completed. Plus Cancelled.**
- Payment? **Auto-charged after trip ends, one payment method per rider.**
- Ratings? **Both rate each other 1–5 after the trip.**

## Step 2: Entities

- **Rider** — id, name, location, payment, rating
- **Driver** — id, name, location, vehicle, available, rating
- **Vehicle** — license plate, type (regular, premium)
- **Location** — lat, lng
- **Trip** — rider, driver, start, end, status, fare

`lat`, `lng`, `fare`, `license plate` are single values — attributes. `Location` looks like a pair of numbers you could leave as fields, but it earns its own class because it has *behavior*: it can measure the distance to another location. That behavior is what promotes a noun from attribute to class. The verbs (*request, accept, complete, rate*) belong to `Trip`, which owns the lifecycle, and the relationships are `has-a`: a `Trip` *has* a rider, a driver, a state, and a pricing policy.

Patterns:
- Pricing → **Strategy** (regular, surge, premium)
- Matching → **Strategy** (nearest, highest-rated nearby)
- Trip lifecycle → **State** (real candidate — rich asymmetric transitions)

## Step 3: Class diagram (verbal)

```
Rider ─── makes ─── Trip ─── handled by ─── Driver
                     │
                     ◆── current TripState
                     ◆── PricingStrategy

RideSystem
  ◇── many Riders
  ◇── many Drivers
  ◇── many Trips
  has MatchingStrategy
  has PricingStrategy
```

## Step 4: Code skeleton

```python
import math


class Location:
    def __init__(self, lat, lng):
        self.lat = lat
        self.lng = lng

    def distance_to(self, other):
        # simplified: euclidean (real systems use haversine)
        return math.sqrt((self.lat - other.lat)**2 + (self.lng - other.lng)**2)


class Vehicle:
    def __init__(self, license_plate, vehicle_type):
        self.license_plate = license_plate
        self.type = vehicle_type  # "regular", "premium"


class Rider:
    def __init__(self, rider_id, name):
        self.id = rider_id
        self.name = name
        self.location = None
        self.rating = 5.0


class Driver:
    def __init__(self, driver_id, name, vehicle):
        self.id = driver_id
        self.name = name
        self.vehicle = vehicle
        self.location = None
        self.available = True
        self.rating = 5.0


# Pricing Strategy
class RegularPricing:
    rate_per_km = 1.0
    rate_per_min = 0.2
    base_fare = 2.0

    def calculate(self, distance_km, duration_min, surge=1.0):
        return (self.base_fare + distance_km * self.rate_per_km + duration_min * self.rate_per_min) * surge


class PremiumPricing:
    rate_per_km = 2.5
    rate_per_min = 0.5
    base_fare = 5.0

    def calculate(self, distance_km, duration_min, surge=1.0):
        return (self.base_fare + distance_km * self.rate_per_km + duration_min * self.rate_per_min) * surge


# Matching Strategy
class NearestDriverMatching:
    def match(self, rider, available_drivers):
        if not available_drivers:
            return None
        return min(available_drivers, key=lambda d: d.location.distance_to(rider.location))


class HighestRatedNearbyMatching:
    def __init__(self, max_distance_km=5):
        self.max_distance = max_distance_km

    def match(self, rider, available_drivers):
        nearby = [d for d in available_drivers if d.location.distance_to(rider.location) <= self.max_distance]
        if not nearby:
            return None
        return max(nearby, key=lambda d: d.rating)


# Trip States (full State pattern this time)
class RequestedState:
    def assign_driver(self, trip, driver):
        trip.driver = driver
        driver.available = False
        trip.set_state(AssignedState())

    def cancel(self, trip):
        trip.set_state(CancelledState())

    def start(self, trip):
        raise ValueError("Can't start: no driver assigned")

    def complete(self, trip):
        raise ValueError("Can't complete: trip not started")


class AssignedState:
    def assign_driver(self, trip, driver):
        raise ValueError("Driver already assigned")

    def cancel(self, trip):
        trip.driver.available = True
        trip.set_state(CancelledState())

    def start(self, trip):
        trip.set_state(InProgressState())

    def complete(self, trip):
        raise ValueError("Can't complete: trip not started")


class InProgressState:
    def assign_driver(self, trip, driver):
        raise ValueError("Trip in progress")

    def cancel(self, trip):
        raise ValueError("Can't cancel in-progress trip")

    def start(self, trip):
        raise ValueError("Already started")

    def complete(self, trip):
        trip.driver.available = True
        trip._calculate_fare()
        trip.set_state(CompletedState())


class CompletedState:
    def _terminal(self, *args):
        raise ValueError("Trip is completed")
    assign_driver = _terminal
    cancel = _terminal
    start = _terminal
    complete = _terminal


class CancelledState:
    def _terminal(self, *args):
        raise ValueError("Trip is cancelled")
    assign_driver = _terminal
    cancel = _terminal
    start = _terminal
    complete = _terminal


class Trip:
    def __init__(self, trip_id, rider, start, end, pricing):
        self.id = trip_id
        self.rider = rider
        self.driver = None
        self.start_location = start
        self.end_location = end
        self.pricing = pricing
        self.fare = None
        self.state = RequestedState()
        self.duration_min = 10  # simulated

    def set_state(self, state):
        self.state = state

    def assign_driver(self, driver):
        self.state.assign_driver(self, driver)

    def cancel(self):
        self.state.cancel(self)

    def start(self):
        self.state.start(self)

    def complete(self):
        self.state.complete(self)

    def _calculate_fare(self):
        distance = self.start_location.distance_to(self.end_location)
        self.fare = self.pricing.calculate(distance, self.duration_min)


class RideSystem:
    def __init__(self, matching_strategy, pricing_strategy):
        self.riders = {}
        self.drivers = {}
        self.trips = []
        self.matching = matching_strategy
        self.pricing = pricing_strategy

    def request_ride(self, rider_id, start, end):
        rider = self.riders[rider_id]
        rider.location = start
        available = [d for d in self.drivers.values() if d.available]
        driver = self.matching.match(rider, available)

        trip = Trip(len(self.trips), rider, start, end, self.pricing)
        self.trips.append(trip)

        if driver:
            trip.assign_driver(driver)

        return trip
```

## Step 5: Walk a flow

```python
system = RideSystem(NearestDriverMatching(), RegularPricing())

alice = Rider(1, "Alice")
system.riders[1] = alice

bob = Driver(1, "Bob", Vehicle("XYZ-123", "regular"))
bob.location = Location(40.7, -74.0)
system.drivers[1] = bob

trip = system.request_ride(1, Location(40.7, -74.0), Location(40.75, -74.05))
# Trip in AssignedState, Bob assigned

trip.start()    # InProgressState
trip.complete() # Calculates fare, frees Bob, CompletedState
print(trip.fare)
```

## Step 6: Tradeoffs

- **"Surge pricing during high demand."** → PricingStrategy takes a surge from a SurgeCalculator. SurgeCalculator could be Observer-style — watches recent ride volume, updates the multiplier.

- **"Pool rides — multiple riders per trip."** → Trip has a list of riders. State pattern still works. Matching gets harder — match a rider to a trip going the right direction.

- **"Driver chooses to accept or reject."** → Add an OfferedState before AssignedState. Driver gets notified, accepts (→ Assigned) or rejects (→ back to Requested, try next driver).

- **"Real-time location updates."** → Observer. Rider and Driver locations publish updates; system subscribes for matching.

- **"Pricing per city/region."** → Factory. `pricing_for_city("SF")` returns a configured pricing strategy.

## Pattern audit

Used heavily:
- **Strategy** — Matching (multiple algorithms), Pricing (multiple algorithms)
- **State** — Trip lifecycle (5 states, each enforces transitions)

Could be added:
- **Observer** — surge pricing, location updates, notifications
- **Factory** — city-specific configurations

Notice State paid off here in a way it didn't in earlier problems. Trip has rich, asymmetric transitions — assign-then-start-then-complete, with cancellation possible only at certain points. Each state enforces what's legal. The if-check version would have been a mess.

---

These four are the classic object-modeling problems: find the entities, give them behavior, and reach for a pattern only when the pain calls for it. Three chapters remain, and they stretch different muscles — first a batch of patterns you haven't met yet (Proxy, Facade, Chain of Responsibility), then two worked problems whose crux *isn't* a pattern at all: one driven by a data structure, one by concurrency. That's Part 5.

---

<div align="right">

[Chapter 18 →](lld-chapter-18.md)

</div>
