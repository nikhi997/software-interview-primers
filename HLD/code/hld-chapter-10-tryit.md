Define latency and throughput, then give a concrete example of improving one while worsening the other.

latency is the time taken to complete a request and throughput is the number of requests compeleted in a unit time . example: if we batch process requests, we can improve throughput by processing more requests at once, but this may increase latency for individual requests as they wait in the queue longer.


Your service averages 20 ms but p99 is 1.5 s, and a typical page loads 40 resources. Roughly what fraction of page loads hit at least one slow (p99) request? Why does this make p99, not the average, the number to chase?

p99 means that 1% of requests take longer than 1.5 s. For a page with 40 resources, the probability that at least one request is slow is 1 - (0.99^40) ≈ 0.33, or about 33%. This makes p99 the number to chase because it reflects the worst-case experience for users, which can significantly impact perceived performance and user satisfaction, even if the average latency is low.

For a food-delivery app, assign a consistency model to each and justify: the restaurant menu, your live order status, the driver's GPS location, your saved payment methods.

menu:eventual consistency as slight delays in menu updates are acceptable; order status: strong consistency to ensure accurate tracking of the order; driver's GPS location: eventual consistency is acceptable as slight delays in location updates do not critically affect the user experience; saved payment methods: strong consistency to ensure that payment information is accurate and up-to-date for transactions.


A service is "highly available" but users report losing data after a crash. Explain how that's possible using availability vs durability.

high availability means the service can respond to requests even during failures, but it does not guarantee that data is safely stored. If the service crashes and loses in-memory data or has not persisted changes to durable storage, users may lose data despite the service being available. Durability ensures that once a write is acknowledged, it will survive crashes and be retrievable later.

Pick any three components from earlier chapters and write the three sentences (why / gain / cost) for each from memory.
cache to reduce load on the database and improve response times, gain is faster data retrieval and reduced latency, cost is increased complexity in cache invalidation and potential stale data.
message queue to decouple services and handle asynchronous processing, gain is improved scalability and fault tolerance, cost is added complexity in managing message delivery guarantees and potential for message loss or duplication.
database sharding to distribute data across multiple servers for improved performance and scalability, gain is increased throughput and reduced latency for large datasets, cost is increased complexity in data management, query routing, and potential for uneven data distribution


Your monolith bundles Identity, Billing, and Shipping, and all three share one User table. Give the bounded-context boundary you'd draw, what each context's own model of "user" contains, and the one cost you take on by splitting them into separate services.

Identity context: user ID, authentication credentials, profile information; Billing context: user ID, payment methods, billing history; Shipping context: user ID, shipping addresses, order history. Cost: increased complexity in managing data consistency and synchronization across services.
