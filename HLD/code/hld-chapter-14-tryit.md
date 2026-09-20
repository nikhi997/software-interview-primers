# Chapter 14: Worked problem — Twitter / News Feed — Try it

*Answers for the Try it questions in [hld-chapter-14.md](../hld-chapter-14.md).*

1. Re-derive fanout-on-write vs fanout-on-read from scratch, listing the cost of each, and explain why read-heavy systems default to write.


2. A celebrity with 50M followers posts. Compute the write amplification under pure fanout-on-write. Explain precisely how the hybrid approach avoids it.


3. Where in this design does each appear, and why: a queue, a cache, blob storage, sharding by user_id? Name the pain each solves.


4. Why cap stored timelines at ~800 tweets instead of keeping the full history per user?


5. Adapt the design for Instagram (image-first). What changes, what stays the same? (Hint: Ch 9 does more work here.)
