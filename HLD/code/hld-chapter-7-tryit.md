# Chapter 7: When you must not lose data — Try it

*Answers for the Try it questions in [hld-chapter-7.md](../hld-chapter-7.md).*

1. For each, say weak/medium/strong durability and justify: (a) a "user is typing…" indicator, (b) a posted comment, (c) a completed payment.


2. You run N=5 copies. You want reads to always see the latest write while tolerating 2 boxes being down for writes. Pick W and R satisfying W+R>5 and the fault tolerance, and explain.


3. A partition splits your two datacenters. For a CP system and an AP system, describe exactly what a read in the disconnected datacenter returns, and name one kind of data each choice is right for.


4. Why is it misleading to call a large distributed system "CA"? What's the honest framing?


5. Take a feature from any app you use and argue whether its reads should be CP or AP. Then find a *different* feature in the same app that should be the opposite.


6. A database appends every change to a write-ahead log before updating its main data files. Explain why the append is faster than updating in place, and what the log is used for when the box restarts after a crash.


7. You're choosing a storage engine for a write-heavy event-ingestion pipeline. Would you lean B-tree or LSM-tree, why, and what do you trade away by choosing it?
