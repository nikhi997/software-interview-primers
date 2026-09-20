# Chapter 7: When you must not lose data

*[← Chapter 6](hld-chapter-6.md) · [Contents](hld-README.md)*

- [ ] **Mark as read**

We keep saying a write is "saved." Let's interrogate that word, because it hides the deepest tradeoff in distributed systems.

A user transfers money. We write "balance = $0" to the primary, return "Success!", and one millisecond later the primary's disk dies before that write reached any replica. The money is gone from one account and never arrived in the other. We *told the user it succeeded.* It didn't.

That's the pain of this chapter: **"saved" is not one thing.** It's a spectrum of guarantees, each with a cost. And once data lives on multiple boxes that can't always talk to each other, you're forced to choose what to sacrifice. That forced choice has a name: the **CAP theorem.**

---

## Durability: what "saved" can mean

**Durability** is the guarantee that once you've acknowledged a write, it survives — crashes, restarts, disk failures. But there are *degrees*, and each is a point on a speed-vs-safety dial:

**1. Acknowledge after writing to one box's memory.** Fastest. But if that box dies before flushing to disk, the write is gone. Weak durability.

**2. Acknowledge after writing to one box's disk.** Survives a process crash/restart on that box. But if the *disk* dies, it's gone. Medium.

**3. Acknowledge only after the write is on multiple boxes.** Survives any single box dying entirely. Strong durability — and the standard for anything you can't lose (payments, orders). The cost: you wait for the write to reach several machines before saying "done," so writes are slower.

> 💡 **Concept notes — the durability dial is a latency dial**
> Every step up in safety costs latency. Waiting for disk is slower than memory; waiting for *N* boxes is slower than one. There's no "just make it durable" for free — you're choosing how long the user waits against how much you can afford to lose. A like-counter can sit at level 1 (lose a few likes on a crash, who cares). A bank transfer sits at level 3 (never lose it, even if slower). *Match the durability to the cost of losing the data.*

This is why we don't crank everything to maximum safety: it would make every write needlessly slow. You spend durability where loss is expensive.

---

## Under the hood: how one box persists a write

We've talked about *when* to acknowledge a write. Worth one level deeper, because it explains how "write to disk" (level 2) can be fast enough to use at all: *how* a single database actually gets a write onto disk without grinding to a halt.

> 💡 **Concept notes — the write-ahead log (WAL)**
> Updating the real data files in place is slow — it means seeking to scattered spots on disk for every write. So databases cheat with a **write-ahead log**: before touching the main data structures, they *append* the change to a single sequential log file and `fsync` that. Appending to the end of one file is about the fastest thing a disk can do, and the moment the change is in the log, the write is durable — if the box crashes, it **replays the log** on restart to rebuild anything it hadn't yet folded into the main files. This is the trick that makes on-disk durability affordable. It's also not a coincidence that this log looks like the replication stream from Ch 3: the same ordered log of changes is what a replica follows to stay in sync.

> 💡 **Concept notes — two ways a database stores data: B-tree vs LSM-tree**
> Underneath, storage engines come in two broad flavours, and the choice is a read-vs-write tradeoff. A **B-tree** (Postgres, MySQL/InnoDB) keeps data in a sorted tree updated *in place* — great for reads and range scans, but each write may have to seek and overwrite a page. An **LSM-tree** (Cassandra, RocksDB, and most write-heavy stores) instead buffers writes in memory and flushes them as sorted files that are merged in the background — so writes become fast sequential appends, at the cost of a read sometimes checking several files. Rule of thumb: **B-tree for read-heavy workloads, LSM-tree for write-heavy ingest.** You'll rarely *pick* this in an interview, but knowing *why* a write-heavy system reaches for an LSM store — it turns random writes into sequential ones — is exactly the kind of depth that separates levels.

---

## Replication and the durability/latency choice

Recall Ch 3: writes go to a primary, then replicate to replicas. *When* do we tell the user "saved"?

**Asynchronous replication:** acknowledge as soon as the *primary* has it; replicate to replicas in the background.
- ✅ Fast — the user waits only for the primary.
- ❌ If the primary dies before replicating, that write is lost. (Our money-transfer disaster.)

**Synchronous replication:** acknowledge only after at least one *replica* also has the write.
- ✅ Survives the primary dying — the write is safe on another box.
- ❌ Slower — the user waits for the network hop to the replica.

**Quorum (the middle ground real systems use):** with N copies, require a write to land on W of them and a read to consult R of them, chosen so the reads and writes always overlap.

> 💡 **Concept notes — quorum, simply**
> If you have **N** copies and you make every write touch **W** copies and every read touch **R** copies, then as long as **W + R > N**, any read is guaranteed to see at least one copy that has the latest write (the read set and write set must overlap). Example: N=3, W=2, R=2 → 2+2 > 3, so reads always catch the latest write while tolerating one box being down. Tuning W and R slides you between "fast writes, slow/risky reads" and the reverse. This is how Cassandra and DynamoDB let you dial consistency per query.

---

## The CAP theorem

Now the big one. The moment your data lives on multiple boxes connected by a network, that network *can fail* — boxes that were talking suddenly can't reach each other. This is a **network partition**, and it is not optional: networks *will* partition. Cables get cut, switches die, datacenters lose links. The only question is what your system does when it happens.

CAP says: when a partition happens, you can have **at most two** of these three, and since partitions are unavoidable, you're really choosing between the last two:

- **C — Consistency:** every read sees the latest write (or an error). All nodes agree.
- **A — Availability:** every request gets a (non-error) answer, even if it might be stale.
- **P — Partition tolerance:** the system keeps working when the network splits.

> 💡 **Concept notes — why it's really a binary choice**
> P isn't optional in a distributed system — partitions happen whether you like it or not, so you *must* tolerate them by continuing in *some* fashion. So the real fork is: **when a partition hits, do you sacrifice C or A?**
> - **CP (choose Consistency):** if a node can't confirm it has the latest data, it **refuses to answer** (returns an error or blocks) rather than risk returning stale data. Correct but unavailable during the partition.
> - **AP (choose Availability):** every node **keeps answering** with whatever data it has, even if possibly stale, and the copies reconcile once the partition heals. Available but temporarily inconsistent.

### Making it concrete

Two datacenters, network link between them just died. A user writes to datacenter 1. A different user reads from datacenter 2, which hasn't received that write.

- A **CP** system: datacenter 2 says *"I can't guarantee I'm current — error / please wait."* No wrong answers, but some requests fail. *Choose this for money, inventory, anything where a wrong answer is worse than no answer.*
- An **AP** system: datacenter 2 says *"here's my (possibly stale) value."* Always answers, but might be briefly wrong, reconciling later. *Choose this for feeds, likes, product views — where a slightly stale answer beats an error.*

> 💡 **Concept notes — there is no "CA" system in practice**
> People sometimes say a single-box database is "CA." But the instant you're distributed (and at scale you are), partitions are a fact of life, so P is forced and the honest choice is CP or AP. Don't claim CA in an interview for a distributed system — it signals you've missed the point of CAP.

### The mental rule

> *When the network splits: would you rather return a wrong/stale answer, or no answer? Money → no answer (CP). Social feed → stale answer (AP).*

Most real systems aren't globally one or the other — they choose **per feature.** The same company runs CP for payments and AP for the activity feed. The interview-grade answer is never "this system is CP" — it's *"the balance check is CP because a stale balance is dangerous; the like count is AP because a stale like count is harmless."*

---

## PACELC: the footnote that makes you sound senior

CAP only describes behavior *during a partition.* But there's a tradeoff even when everything is healthy: **latency vs consistency.** PACELC extends CAP:

> **If Partition, choose A or C; Else (normal operation), choose Latency or Consistency.**

Even with no partition, keeping all copies perfectly consistent costs latency (you wait to synchronize). Relax consistency and you go faster. So a system like Cassandra is "**AP / EL**" — during a partition it favors availability, and normally it favors low latency over strict consistency. You don't need to master PACELC, but dropping it shows you understand the tradeoff exists *all the time*, not just during failures.

---

## Bringing it back to our system

Our URL shortener:
- **URL mappings**: once created, basically never change. Stale reads are harmless. → lean **AP**, cache aggressively, replicate async. Speed and availability over strict consistency.
- **The unique-code guarantee** (no two long URLs get the same code, custom codes aren't double-claimed): this needs **consistency** — two users must not both claim "pasta." → the write path that allocates codes leans **CP**.

Same system, different choice per feature. That's the whole art.

---

## What we have now

We can now reason about what "saved" guarantees, dial durability to match the cost of losing each kind of data, and — crucially — *choose CP or AP per feature* based on whether a wrong answer or no answer is worse. This is the conceptual core that the worked problems in Part 4 lean on constantly.

We've covered scale (Part 1) and the big behaviors: fast (cache), decoupled (queue), durable/consistent (this chapter). One operational pain remains before we wrap components: what happens when clients send *too many* requests — abuse, runaway scripts, or just more love than we can handle? That's rate limiting and backpressure. Chapter 8.

---

## Try it

1. For each, say weak/medium/strong durability and justify: (a) a "user is typing…" indicator, (b) a posted comment, (c) a completed payment.
2. You run N=5 copies. You want reads to always see the latest write while tolerating 2 boxes being down for writes. Pick W and R satisfying W+R>5 and the fault tolerance, and explain.
3. A partition splits your two datacenters. For a CP system and an AP system, describe exactly what a read in the disconnected datacenter returns, and name one kind of data each choice is right for.
4. Why is it misleading to call a large distributed system "CA"? What's the honest framing?
5. Take a feature from any app you use and argue whether its reads should be CP or AP. Then find a *different* feature in the same app that should be the opposite.
6. A database appends every change to a write-ahead log before updating its main data files. Explain why the append is faster than updating in place, and what the log is used for when the box restarts after a crash.
7. You're choosing a storage engine for a write-heavy event-ingestion pipeline. Would you lean B-tree or LSM-tree, why, and what do you trade away by choosing it?

*Write your answers in [hld-chapter-7-tryit.md](code/hld-chapter-7-tryit.md).*

---

## The bumper sticker

> *"Saved" is a dial, not a fact: match durability to the cost of loss, and when the network splits, choose per-feature whether a stale answer (AP) or no answer (CP) is the lesser evil.*

Next: clients can send more requests than we can or should serve. Time to learn to say "no" gracefully — rate limiting and backpressure.

---

<div align="right">

[Chapter 8 →](hld-chapter-8.md)

</div>
