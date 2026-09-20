# Chapter 16: Worked problem — Ride-sharing (Uber) — Try it

*Answers for the Try it questions in [hld-chapter-16.md](../hld-chapter-16.md).*

1. Why can't a normal database index answer "find drivers within 2 km of this point" efficiently? Explain how geohashing makes it a fast lookup.


2. Where does this system need strong consistency, and where is eventual consistency fine? Tie each to Chapter 7.


3. Why keep driver locations in memory rather than the durable database? What's the tradeoff and why is it acceptable here?


4. The matching service offers a ride to a driver. Describe the exact mechanism that prevents the same driver being matched to two riders simultaneously.


5. Identify every component reused from earlier chapters (queue, WebSocket gateway, cache, sharding) and the pain each solves here. Then propose how you'd handle airport-surge hot spots.
