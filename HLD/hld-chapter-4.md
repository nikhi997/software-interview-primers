# Chapter 4: When one database can't hold it all

*[← Chapter 3](hld-chapter-3.md) · [Contents](hld-README.md)*

- [ ] **Mark as read**

End of Chapter 3: replicated database, reads scaled across replicas, surviving failure. Two walls remained: **every box holds the full dataset** (so the data can't grow past one disk) and **one primary takes all writes** (so writes can't grow past one box).

Replication couldn't help because replication *copies.* The fix is the opposite reflex: stop copying, start **splitting.** Each box holds a different *slice* of the data.

This is **sharding** (also called horizontal partitioning). It's the most powerful scaling move in the book, and also the one with the most sharp edges. Go slow here.

---

## The idea

Instead of one database holding all 6 TB, run several databases, each holding a *piece*:

```
                   ┌──▶ shard 1: users A–H
writes & reads ───▶├──▶ shard 2: users I–P
                   └──▶ shard 3: users Q–Z
```

Now:
- The data is split, so **total size** can grow forever — just add shards.
- Writes are split across shards, so **write capacity** scales — each shard has its own primary.

> 💡 **Concept notes — shard vs replica**
> A **replica** is a *full copy* of the data (Ch 3) — for read scaling and failover.
> A **shard** is a *distinct slice* of the data — for size and write scaling.
> They're orthogonal, and real systems use *both*: each shard is itself replicated (a primary + replicas), so it both holds a slice and survives failure. Sharding splits; replication copies; together they scale and protect.

---

## The hard part: which shard holds this row?

The moment you split data, every single read and write must answer one question first: *which shard?* Get the routing wrong and you either can't find data or you put it in the wrong place. The routing rule is called the **partition key** (or shard key).

Let's walk through the options, because choosing wrong here is the classic sharding mistake.

### Option A: Range-based sharding

Split by ranges of the key. Users A–H on shard 1, I–P on shard 2, Q–Z on shard 3.

- ✅ Simple. Range queries ("all users J–L") hit few shards.
- ❌ **Hot spots.** If lots of usernames start with "S", shard 3 is overloaded while shard 1 is idle. Real-world data is rarely evenly distributed. Think timestamps: range-shard by date and *all today's writes* hammer one shard while old shards sit cold.

### Option B: Hash-based sharding

Run the key through a hash function and use the result to pick a shard:

$$\text{shard} = \text{hash(key)} \bmod N \quad (N = \text{number of shards})$$

- ✅ **Even distribution.** A good hash scatters keys uniformly — no hot spots from skewed data.
- ❌ Range queries are now spread across all shards (adjacent keys hash to random shards).
- ❌ **The resharding catastrophe** — the reason this whole chapter has a second half.

> 💡 **Concept notes — what `mod N` actually does**
> `hash(key) mod N` gives a number from 0 to N−1 — pick that shard. If `hash("alice") = 178` and you have 4 shards, `178 mod 4 = 2`, so Alice lives on shard 2. Deterministic: the same key always routes to the same shard, so you can find it again. As long as N never changes.

---

## The resharding catastrophe

Here's the trap that makes naive hash sharding dangerous. You have 4 shards:

$$\text{shard} = \text{hash(key)} \bmod 4$$

Now you grow and add a 5th shard. `N` changes from 4 to 5, so the formula becomes `hash(key) mod 5`. But look what happens to where keys *map*:

```
key      hash    mod 4 (old)    mod 5 (new)
alice    178     2              3        ← moved!
bob      201     1              1        ← stayed
carol    99      3              4        ← moved!
dave     340     0              0        ← stayed
```

Changing N from 4 to 5 changes the shard for **almost every key** — roughly N/(N+1) of all data has to physically move to a different box. Add one shard, and you reshuffle nearly your *entire dataset* across the network. During that massive migration, the system is slow or down. This is why a careless `mod N` scheme is a time bomb: it works great until the day you need to grow, and then growing is catastrophic.

We need a way to add a shard that moves *only a small fraction* of the data. That's exactly what consistent hashing does.

---

## Consistent hashing

The fix: instead of mapping keys directly to shards with `mod N`, map **both keys and shards onto a circle** (a "ring"), and assign each key to the next shard clockwise.

```
        0/360°
          ┌───── Shard A
    Shard │
     C    ●         ● key "alice"
          │
          ●  Shard B
        (positions on a ring 0–360°)
```

The rules:
1. Hash each **shard** to a position on the ring (0–360°, conceptually).
2. Hash each **key** to a position on the ring too.
3. A key belongs to the **first shard found going clockwise** from the key's position.

> 💡 **Concept notes — why the ring fixes resharding**
> When you **add** a shard, it drops onto one spot on the ring. Only the keys sitting in the *arc just before it* — the ones that used to walk clockwise past that spot to the next shard — get reassigned to the new shard. Every other key is untouched. Adding a shard moves roughly **1/N of the data**, not nearly all of it. Same when a shard is **removed**: only its keys move, to the next shard clockwise. This is the entire reason consistent hashing exists, and it's used in Cassandra, DynamoDB, and basically every distributed cache and database.

> 💡 **Concept notes — virtual nodes**
> One problem: with few shards on the ring, the arcs are uneven — one shard might own a huge arc (and get overloaded) while another owns a sliver. The fix is **virtual nodes**: each physical shard is hashed onto the ring at *many* positions (say 100 each). Now the load evens out, and when a shard joins or leaves, its share is taken from/spread to many others smoothly. You don't need to implement this in an interview — just *name it* as how real systems keep the ring balanced.

There's a runnable consistent-hashing demo in `code/consistent_hashing.py` — read it after this chapter and watch how few keys move when you add a node.

---

## The price of sharding: things that used to be easy are now hard

Sharding is powerful but it *taxes* you. Name these costs in an interview — they're what separate people who've read about sharding from people who understand it.

**1. Cross-shard queries get expensive.** "Count all users" used to be one query. Now it must hit *every* shard and combine results (a scatter-gather). Anything that spans shards is slow.

**2. Joins across shards are painful.** If users are on one shard and their orders on another, joining them means pulling data from multiple boxes and joining in your app. You design the shard key specifically to keep related data *together* (e.g., shard by `user_id` so a user's orders live with the user).

**3. Transactions across shards are hard.** A single-box database can atomically update two rows. Across shards, that needs distributed transactions (two-phase commit) — slow and complex. Often you redesign to avoid needing them.

**4. Choosing the shard key is a one-way door.** Pick `user_id` and later realize you query by `region` constantly? Re-sharding to a new key is a massive migration. The shard key should match your *most common access pattern* — get it right early.

> 💡 **Concept notes — pick the shard key from the query, not the data**
> The right shard key is the field you filter by most. Shard a chat app by `conversation_id` and all of one conversation's messages live on one shard — fetching a chat is one shard's work. Shard the same app by `message_id` and every conversation is scattered, so opening a chat scatter-gathers across all shards. Same data, different key, wildly different performance. Always ask: *what's the dominant query?* Shard to make that query hit one shard.

---

## Redoing the estimate: when do we even need this?

Don't shard early — sharding is a tax you pay forever. From Ch 3, our URL shortener stored under 1 TB after years and writes were 10/sec on a single primary. **It never needs sharding.** Replication alone carries it. Saying *"this doesn't need sharding, replication is enough"* in an interview is a senior answer — it shows you don't reach for the biggest hammer reflexively.

You shard when a real number forces it:
- **Data size > one disk.** 50 TB of data, 4 TB disks → you *must* split. ~13+ shards minimum.
- **Write throughput > one primary.** 50,000 writes/sec, one primary does 5,000/sec → 10+ shards to spread writes.

Only then. And when you do, use consistent hashing so the *next* growth step doesn't reshuffle everything.

---

## What we have now — the full scalable skeleton

```
                   ┌─ shard 1 (primary + replicas)
LB ─▶ app servers ─┼─ shard 2 (primary + replicas)   ← consistent hashing
                   └─ shard 3 (primary + replicas)      picks the shard
```

This is the complete data tier most large systems use: **sharded for size/writes, each shard replicated for reads/failure, routed by consistent hashing so growth is cheap.** Combined with the stateless app tier and load balancer from Ch 2, you can now scale this skeleton to essentially any size.

We've solved *capacity.* But we haven't touched *speed* or *efficiency.* Every read still hits a disk somewhere, even for the same popular URL fetched a million times. That waste — repeated reads of the same data — is the pain Chapter 5 fixes with caching.

---

## Try it

1. You shard with `hash(key) mod 8`. You add 2 shards to make 10. Roughly what fraction of keys have to move? Why is this bad, and what technique avoids it?
2. Explain, in terms of the ring, why adding one node under consistent hashing moves only ~1/N of the keys.
3. You're designing a messaging app. You can shard by `user_id` or by `message_id`. The dominant query is "load all messages in this conversation." Which shard key do you choose and why? What goes wrong with the other one?
4. Your service stores 800 GB total and does 200 writes/sec, on 4 TB disks. Should you shard? Justify with the numbers, and say what you'd do instead.
5. Name two operations that were trivial on a single database but become expensive once data is sharded, and explain why.

*Write your answers in [hld-chapter-4-tryit.md](code/hld-chapter-4-tryit.md).*

---

## The bumper sticker

> *Replication copies, sharding splits. Shard only when size or writes outgrow one box, route with consistent hashing so growth stays cheap, and choose the shard key to match your dominant query.*

That closes Part 1. You can now scale the *skeleton* — app tier, load balancer, replicated and sharded data — to any size. Part 2 adds the components that make it *fast, durable, and well-behaved*, starting with the biggest free win in all of system design: caching.

---

<div align="right">

[Chapter 5 →](hld-chapter-5.md)

</div>
