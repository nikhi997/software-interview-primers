# Chapter 16: Worked problem — Ride-sharing (Uber)

*[← Chapter 15](hld-chapter-15.md) · [Contents](hld-README.md)*

- [ ] **Mark as read**

The final worked problem, running the six-step ritual one last time. Attempt it cold first.

The problem: *"Design a ride-sharing service like Uber. Riders request a ride; the system finds nearby available drivers and matches one; both see each other's live location during the trip."*

Signature lesson: **geospatial** systems — matching entities by *physical location* in real time. This is a genuinely different axis from everything before (which cared about users, data, connections — not *where things are in space*).

---

## Step 1: Clarify

**Functional:**
- Rider requests a ride from a pickup location. ✅
- Match with a nearby available driver. ✅ *(the heart of the problem)*
- Live location tracking during the trip (both see each other move). ✅
- Fare estimation, trip lifecycle (requested → matched → in-progress → completed). ✅

**Non-functional:**
- Scale? → *Millions of active drivers/riders, a major city has ~100K+ active drivers.*
- Latency? → *Matching must be fast (seconds). Location updates frequent (every few seconds).*
- Consistency? → *A driver must not be matched to two riders at once (strong consistency on the match).*
- Availability? → *High; people are stranded if it's down.*

The standout: **find nearby drivers fast** (geospatial query) and **match exactly once** (no double-booking — a consistency requirement).

---

## Step 2: Estimate

**Location updates (the firehose):** ~100K active drivers/city, each sending location every ~4 sec. For a large operation across many cities, say 5M active drivers globally:
$$\frac{5\text{M drivers}}{4 \text{ sec}} \approx 1{,}250{,}000 \text{ location updates/sec}$$

Over a million writes/sec *just for location* — write-heavy, and these writes are unusual (constantly-changing geographic data).

**Ride requests:** far fewer — thousands/sec at peak. The asymmetry: an ocean of location updates, a stream of match requests.

> 💡 The dominating challenge is the **location update firehose** + answering **"who's near this point?"** fast and constantly. That geospatial read/write pattern is unlike any previous problem, and it drives a specialized index.

---

## Step 3: API + data model

**API:**
```
POST /rides/request   { pickup: {lat,lng}, dropoff: {lat,lng} }   → ride_id, matched driver
POST /drivers/location { lat, lng }   (sent every few sec — the firehose)
GET  /rides/{id}      → trip status + live locations
```

**Data model:**
```
DRIVER:    driver_id, status (available/on_trip/offline), current_location {lat,lng}
RIDER:     rider_id, ...
TRIP:      trip_id, rider_id, driver_id, status, pickup, dropoff, fare, created_at
DRIVER_LOCATION:  driver_id → {lat, lng, updated_at}   (hot, constantly overwritten)
```

> 💡 Driver locations change every few seconds and are read constantly for matching → keep them in a **fast in-memory store** (Redis), not the main database. Writing 1M+/sec to a durable disk-based DB would be wasteful and slow; locations are ephemeral (you only care about *current* position), so they live in memory. Trips (which you must not lose) go to the durable database. *Match the store to the data's durability needs* (Ch 7).

---

## Step 4: High-level design — the geospatial problem

The core question: given a rider's pickup point, **find all available drivers within ~2 km, fast.** Naively, you'd compute the distance from the rider to *every* driver and keep the close ones — but checking millions of drivers per request is hopeless. You need a **spatial index** that answers "what's near this point?" without scanning everything.

### The tool: geospatial indexing

You can't use a normal index — those work on single sortable values (a number, a string), but location is *two* dimensions (lat *and* lng) and "nearby" isn't a simple range on either one alone. The trick is to **map 2D space onto a 1D index** in a way that keeps nearby things close in the index.

> 💡 **Concept notes — geohashing / quadtrees / S2**
> **Geohashing:** divide the world into a grid of cells, each with a string ID, where *nearby locations share an ID prefix.* To find drivers near a point: compute the point's geohash, then look up drivers in that cell and its neighbors — a fast prefix lookup instead of scanning everyone. Longer prefix = smaller, more precise cell.
> **Quadtree:** recursively split space into four quadrants, subdividing dense areas (a busy downtown) more finely than empty ones — naturally adapts to driver density.
> **S2 / H3:** production libraries (Google's S2, Uber's H3) that do this robustly on a sphere. H3 uses hexagons; Uber literally built it for this problem.
> You don't implement these in an interview — you **name** one and explain the idea: *"index drivers by geohash so 'find nearby' becomes a cell lookup, not a full scan."* That sentence wins this problem.

```
find nearby drivers(pickup):
   cell = geohash(pickup)                    # e.g., "9q8yy"
   candidates = drivers in cell + 8 neighbor cells   # fast prefix lookup
   filter to status=available, sort by actual distance/ETA
   return top few
```

### The matching flow — and the double-booking trap

```
1. Rider requests ride at pickup point
2. Geospatial lookup (Redis geo-index): nearby available drivers
3. Matching service picks the best (closest ETA, rating, etc.)
4. Offer to that driver — ⚠️ must mark them unavailable ATOMICALLY
5. Driver accepts → create trip, both notified
   Driver declines/times out → offer to next candidate
```

> 💡 **Concept notes — match exactly once (the consistency requirement)**
> Step 4 is the one place this system needs **strong consistency.** If two riders' requests both see the same driver as "available" and both try to grab them, you've double-booked. Prevent it with an **atomic operation** — a lock or atomic compare-and-set on the driver's status ("set available→reserved, only if currently available"). Whoever wins, wins; the other request moves to the next driver. This is the *CP choice* (Ch 7) for this specific operation, while location updates are happily *AP*. **Same system, consistency chosen per operation** — the lesson of the whole book, one last time.

### Live tracking during the trip

Once matched, rider and driver see each other move. This is **Chapter 15 again** — persistent connections (WebSockets) push location updates between the two parties in real time. Ride-sharing reuses chat's real-time delivery for live tracking.

### The full diagram

```
                  ┌──────────────┐
 riders/drivers ─▶│ load balancer│
                  └──────┬───────┘
                         ▼
        ┌────────────────────────────────┐
        │          app / API tier        │
        └──┬──────────────┬───────────┬──┘
  location │       match  │           │ live tracking
  updates  ▼              ▼           ▼
  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐
  │ geo-index    │  │ matching svc │  │ WebSocket gateway│ (Ch 15)
  │ (Redis geohash)│ │ atomic claim │  │ push locations   │
  │ driver→cell  │  │ of driver    │  └──────────────────┘
  └──────────────┘  └──────┬───────┘
   1M+ updates/sec         ▼
   in memory        ┌──────────────────────┐
                    │ DB: trips, users     │ durable, sharded
   trip events ──▶ queue ──▶ workers ──▶ receipts, fare calc, analytics (Ch 6)
```

The location firehose hits the in-memory geo-index (not the durable DB). Matching does an atomic claim. Live tracking reuses WebSocket gateways from Ch 15. Trips persist durably. Post-trip work (fare, receipt, analytics) goes async via a queue. *Every component from the book, composed for one problem.*

---

## Step 5: Deep dive

- *"1M+ location updates/sec — how?"* → In-memory geo-index (Redis), sharded by region/city (Ch 4 — shard by geography, the dominant query axis). Updates just overwrite the driver's current cell; old position discarded. No durability needed — locations are ephemeral.
- *"Shard the geo-data how?"* → By **geographic region** — a city's drivers and riders are matched together and almost never cross-city, so geographic sharding keeps each match query on one shard (Ch 4: shard by the dominant query). Hot cities (dense downtowns) may need finer splitting — same hot-spot concern as range sharding.
- *"Driver accepts two requests at once?"* → Can't — the atomic claim in Step 4 (compare-and-set on status) guarantees one winner. The loser re-matches.
- *"Surge pricing?"* → A service computes demand/supply ratio per region from the live geo-index and adjusts fare — a read over the same spatial data.

---

## Step 6: Bottlenecks & tradeoffs

- **Next bottleneck:** hot regions (airport at rush hour) overload one geo-shard → finer geospatial partitioning, or dedicated capacity for hot cells (the hot-key problem yet again, now geographic).
- **Tradeoffs made:** driver locations are **in-memory and not durable** (we chose speed + write throughput over durability — losing a location update is harmless, the next arrives in seconds). Matching is **strongly consistent** (CP) at the cost of a bit of latency, *only* for the claim step — everything else stays fast and loose. We accept location data is **approximate/slightly stale** (a driver's shown position is a few seconds old) — fine for matching and tracking.

---

## The one thing to remember

Ride-sharing is the **geospatial** problem: index entities by location (geohash/quadtree/H3) so "find nearby" is a cell lookup instead of a full scan, keep the location firehose in a fast in-memory store, and make *only* the match step strongly consistent to avoid double-booking. *Spatial index + ephemeral in-memory locations + atomic match.*

---

## Try it

1. Why can't a normal database index answer "find drivers within 2 km of this point" efficiently? Explain how geohashing makes it a fast lookup.
2. Where does this system need strong consistency, and where is eventual consistency fine? Tie each to Chapter 7.
3. Why keep driver locations in memory rather than the durable database? What's the tradeoff and why is it acceptable here?
4. The matching service offers a ride to a driver. Describe the exact mechanism that prevents the same driver being matched to two riders simultaneously.
5. Identify every component reused from earlier chapters (queue, WebSocket gateway, cache, sharding) and the pain each solves here. Then propose how you'd handle airport-surge hot spots.

*Write your answers in [hld-chapter-16-tryit.md](code/hld-chapter-16-tryit.md).*

---

## The bumper sticker

> *Ride-sharing is geography in real time: index by location so "who's nearby" is a cell lookup, keep the location firehose in fast ephemeral memory, and make only the match atomic so no driver is double-booked.*

---

## You've finished the book

Step back and see what you can now do. Given *any* system, you can: clarify functional vs non-functional, estimate the load into real numbers, choose a data model and SQL/NoSQL by access pattern, grow an architecture from one box to a global system adding each component *only* when a number forces it, name every tradeoff (CAP, consistency, latency/throughput, durability), and zoom into the hard part — fanout, real-time delivery, or geospatial matching.

But the real skill isn't "knowing components." It's *deriving* the architecture from the pains, live, justifying every box with a number and naming what it cost. That comes from reps — running the six-step ritual on problem after problem until it's automatic. The appendix has a catalog, the numbers to memorize, and more problems to practice.

Be patient with it. The understanding comes faster than you'd think; the *automatic recognition* takes months of reps. Trust the process.

> *Architecture is the set of moves you make so the system bends instead of breaks when the traffic lands.* That was the whole game.

---

<div align="right">

[Appendix →](hld-appendix.md)

</div>
