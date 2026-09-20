Your app is 95% reads, 5% writes, total 40,000 RPS. One DB box does 4,000 reads/sec and 4,000 writes/sec. With primary-replica replication, how many replicas do you need for the reads? Is the single primary okay for the writes? Show the math.

Reads: 0.95 × 40,000 = 38,000 RPS
Writes: 0.05 × 40,000 = 2,000 RPS

Read replicas needed: 38,000 ÷ 4,000 = 9.5 → 10 replicas. Add 1 spare for failover = 11 replicas total.

Writes: Primary handles 4,000 writes/sec; we need only 2,000 RPS. One primary is sufficient.


A user changes their email, the page reloads, and they see the old email. Explain exactly why, in terms of replication lag, and give a fix that doesn't slow down everyone else's reads.

**Why:** The write goes to the primary, which propagates it to replicas. During replication lag, if the user reads from a replica before the update arrives, they see stale data (their old email).

**Fix:** Use read-after-write consistency. Route that user's *own* reads to the primary for a short window after they write. Other users' reads continue hitting the fast replicas. No impact on general read performance.


Replication gives you many readers but only one writer. Describe a system where that's a problem, and name (just name) the technique Chapter 4 will use to fix it.

**Problem:** Write-heavy systems. If your app has high write volume, the single primary becomes the bottleneck—you can't scale writes by adding replicas (each replica is read-only). Also, if data grows beyond one server's capacity, all replicas must also grow proportionally, since each holds the entire dataset.

**Fix:** Sharding.

Your dataset is 6 TB and growing; your largest available disk is 4 TB. Explain in one sentence why adding more replicas cannot solve this.

Each replica must hold the entire 6 TB dataset; adding more 4 TB replicas doesn't help because none can fit the data. Replication solves read scaling, not storage capacity—you need sharding to partition the data across multiple servers.

Your primary dies and two replicas both try to take over at once. Name what goes wrong if both succeed, and explain how leader election by majority vote prevents it — including why you'd want an odd number of voters.

**Problem:** Split brain. If both replicas become leaders and accept writes independently, the data diverges—one server accepts writes that the other never sees, causing inconsistency.

**Solution:** Majority vote ensures only *one* server claims leadership. It must earn votes from a majority (e.g., 3 out of 5 servers). With an even number, you risk a 2–2 tie and no clear winner. Odd numbers guarantee a majority—one server always wins, the others don't.
