# Chapter 3: When the database is the bottleneck

*[← Chapter 2](hld-chapter-2.md) · [Contents](hld-README.md)*

- [ ] **Mark as read**

End of last chapter: many stateless app servers behind a load balancer, all funneling into **one database.** We named the pain: that single database is both a single point of failure (it dies, everyone's down) and a bottleneck (one box, finite query capacity).

Let's give the data more than one box. But databases are *not* like app servers — you can't just run three and round-robin between them. The reason why is the whole lesson of this chapter.

---

## Why you can't scale a database like an app server

App servers were easy to multiply because we made them **stateless** — they hold no unique data, so any one is as good as any other. Throw away one, spin up another, identical.

A database is the opposite. It exists *specifically* to hold state. If you naively run three databases and send writes to random ones:

```
write "code abc → wikipedia.org" → goes to database 1
read  "code abc"                 → goes to database 2 → "never heard of it"
```

The three databases don't know about each other's writes. Your data is scattered and inconsistent. Multiplying a database is hard *precisely because* it holds the state that app servers were able to give up.

There are two fundamentally different moves, and they solve different problems:

- **Replication** — keep *full copies* of the same data on multiple boxes. Solves: read capacity + surviving a box dying. (This chapter.)
- **Sharding** — split the data into *pieces*, each box holds a different piece. Solves: data too big / writes too many for one box. (Chapter 4.)

We reach for replication first, because most systems are read-heavy and replication is simpler.

---

## Replication: one writer, many readers

The most common setup: **primary-replica** (also called leader-follower, or historically master-slave).

```
                        ┌──▶ replica 1 (read only)
writes ──▶ PRIMARY ─────┼──▶ replica 2 (read only)
           (the only    └──▶ replica 3 (read only)
            writer)
reads  ──▶ any replica
```

- **One primary** accepts all **writes.**
- The primary streams every change to the **replicas.**
- Replicas serve **reads** only.

> 💡 **Concept notes — primary and replica**
> The **primary** is the single source of truth for writes. Every insert/update/delete goes here.
> A **replica** is a full, continuously-updated copy of the primary. It exists to (a) serve reads, taking load off the primary, and (b) stand ready to be promoted to primary if the primary dies.
> **Replication lag** is the delay between a write landing on the primary and showing up on a replica — usually milliseconds, but it's not zero. This tiny gap causes a real problem we'll hit in a moment.

### Why this fits a read-heavy system perfectly

Remember our URL shortener's ratio from Ch 1: **100 reads per write.** Look at where the load goes:

- The 1% that are writes → all hit the single primary. At 10 writes/sec, the primary is bored.
- The 99% that are reads → spread across the replicas. Add replicas to add read capacity.

We just scaled the part that was actually under pressure (reads) by adding replicas, and left the lightly-loaded part (writes) on one box. That's the move: **replication scales reads.**

And we got fault tolerance for free-ish: if a replica dies, the others cover. If the *primary* dies, you **promote** a replica to be the new primary (failover). Brief disruption, but not data loss and not permanent downtime.

> 💡 **Concept notes — how a replica *becomes* the primary: leader election**
> Promotion can't be left to chance. If the primary dies and two replicas both decide "I'm in charge now," you get **split-brain** — two primaries accepting conflicting writes, about the worst thing that can happen to your data. So the surviving boxes must *agree* on exactly one new leader, even though some of them may be down or slow. That agreement problem has a name: **consensus**, and the algorithms that solve it (**Raft**, **Paxos**) work by majority vote — a replica becomes primary only when **more than half** the boxes vote for it. Because a majority can form only once at a time, you can never elect two leaders simultaneously, which is exactly what kills split-brain. You don't implement this yourself — your database, or a coordinator like **ZooKeeper/etcd**, does it — but the phrase that lands in an interview is *"a new primary is chosen by consensus, a majority quorum, which prevents split-brain."* The practical costs: you want an **odd** number of voters (so a majority always exists) and you accept a brief unavailable window while the election runs.

---

## The trap: replication lag and stale reads

Here's the bite, and it's a favorite interview probe.

Replication isn't instant. A write hits the primary, then takes a few milliseconds to reach the replicas. In that gap, a read from a replica returns **stale data** — the old value.

Concrete failure:

```
1. User updates their profile name → write goes to PRIMARY → succeeds
2. Page reloads immediately → read goes to a REPLICA
3. Replica hasn't received the update yet (lag)
4. User sees their OLD name. "Did my save not work??"
```

The user did everything right; the system showed them stale data because the read raced ahead of replication. This is the cost of replication, and you have to *name it and handle it.*

> 💡 **Concept notes — consistency models, gently**
> **Strong consistency:** a read always reflects the latest write. Simple to reason about, but it means reads can't freely use lagging replicas.
> **Eventual consistency:** replicas converge to the latest value *eventually* (milliseconds later). Reads might briefly be stale. Cheaper and more scalable. Most read-heavy systems happily accept it — a URL that resolves to its target 50 ms late is fine; a bank balance is not. We go deeper in Ch 10.

### Common fixes (know these — they're exactly what interviewers want)

1. **Read-your-own-writes:** route a user's reads to the **primary** for a short window right after they write. They see their own change instantly; everyone else can tolerate the tiny lag. Cheap and effective.
2. **Tolerate it:** for data where staleness doesn't matter (a click counter, a public feed), just read from replicas and accept eventual consistency.
3. **Read from primary for critical reads:** for the rare read that *must* be current (checking a balance before a transfer), go to the primary and pay the cost.

The senior move in an interview isn't avoiding lag — it's *saying which reads can tolerate it and which can't, and routing accordingly.*

---

## Redoing the estimate: how many replicas?

Say one database box serves **5,000 reads/sec** comfortably. Our URL shortener at takeoff needs 50,000 reads/sec (from Ch 2).

$$\frac{50{,}000 \text{ reads/sec}}{5{,}000 \text{ reads/sec per box}} = 10 \text{ replicas}$$

Plus the primary, plus one extra replica for redundancy → about **12 database boxes**, and writes are still trivially handled by the single primary. Reads scale by adding replicas. Clean.

But notice the load we *didn't* solve. All those replicas are full copies. Every one of them must hold the **entire dataset.** And every write still goes through **one primary.** So replication runs out of room in exactly two situations:

- **The data won't fit on one box.** Replicas are full copies; if the data is 5 TB and your biggest disk is 4 TB, *no* replica can hold it. Adding replicas doesn't help — they'd each need the whole thing.
- **Writes outgrow one primary.** Replication gives you one writer. A write-heavy system (say 50,000 writes/sec) will saturate the single primary, and you can't add primaries without a new technique.

Both of those need a fundamentally different move: stop copying the whole dataset, and start *splitting* it. That's sharding — Chapter 4.

---

## What we have now

```
                          ┌──▶ replica 1 ─┐
LB ─▶ app servers ─writes─▶ PRIMARY        │ reads spread
                  └─reads──┼──▶ replica 2 ─┤ across replicas
                          └──▶ replica 3 ─┘
```

- Reads scale horizontally by adding replicas.
- Survives a database box dying (promote a replica).
- We accept (and route around) **replication lag** / eventual consistency.

Remaining walls: **one primary for all writes**, and **every box holds the full dataset.** When either the write volume or the data size outgrows a single box, copying won't save us. We have to split.

---

## Try it

1. Your app is 95% reads, 5% writes, total 40,000 RPS. One DB box does 4,000 reads/sec and 4,000 writes/sec. With primary-replica replication, how many replicas do you need for the reads? Is the single primary okay for the writes? Show the math.
2. A user changes their email, the page reloads, and they see the *old* email. Explain exactly why, in terms of replication lag, and give a fix that doesn't slow down everyone else's reads.
3. Replication gives you many readers but only one writer. Describe a system where that's a problem, and name (just name) the technique Chapter 4 will use to fix it.
4. Your dataset is 6 TB and growing; your largest available disk is 4 TB. Explain in one sentence why adding more *replicas* cannot solve this.
5. Your primary dies and two replicas both try to take over at once. Name what goes wrong if both succeed, and explain how leader election by majority vote prevents it — including why you'd want an *odd* number of voters.

*Write your answers in [hld-chapter-3-tryit.md](code/hld-chapter-3-tryit.md).*

---

## The bumper sticker

> *Replication copies the whole dataset to many boxes: it scales reads and survives failure, at the cost of replication lag. It cannot help when the data won't fit or the writes won't fit on one box.*

Next: the data is too big for one box, or the writes are too many for one primary. Time to split the data into pieces — and meet the hardest routing problem in the book.

---

<div align="right">

[Chapter 4 →](hld-chapter-4.md)

</div>
