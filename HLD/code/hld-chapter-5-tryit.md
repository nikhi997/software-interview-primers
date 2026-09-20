*** OURS (local) ***


A product page is read 10,000 times/sec but its data changes a few times a day. Design the caching: which pattern, what TTL, and what's the worst-case staleness a user could see? Justify the TTL.

we have to use a read-through cache pattern for this scenario. The TTL (Time To Live) should be set to a value that balances freshness and performance. Given that the data changes a few times a day, a TTL of 1 hour could be appropriate. This means that once the data is cached, it will remain in the cache for up to 1 hour before it is considered stale and needs to be refreshed from the database.


With a 90% cache hit rate and 50,000 reads/sec total, how many reads/sec actually reach the database? What hit rate would you need to get that under 1,000/sec?

With a 90% cache hit rate, 10% of the requests reach the database. So, 50,000 * 0.1 = 5,000 reads/sec reach the database. To get that under 1,000/sec, we need a hit rate of 98% or higher (50,000 * 0.02 = 1,000).


Explain the thundering-herd problem in your own words, and give one fix.

The thundering-herd problem occurs when many requests simultaneously try to access a resource that is not in the cache, causing a spike in database load. One fix is to use request coalescing or locking, where only one request fetches the data from the database while others wait for the result.

A scanner sends millions of requests for random invalid IDs. Why does your cache not help, and what's it called? Name a fix.

This scenario is known as a cache miss storm or cache pollution. The cache does not help because the requests are for invalid or rarely accessed data, which never gets cached effectively. One fix is to use a bloom filter to quickly check if an ID is valid before querying the cache or database.

Why is LRU the default eviction policy? Describe a traffic pattern where LFU would beat it.
lRU is the default eviction policy because it assumes that recently accessed items are more likely to be accessed again in the near future, which is a common access pattern in many applications. This makes LRU effective for workloads with temporal locality. and LFU would beat LRU in a scenario where there are a few items that are accessed very frequently over a long period of time, while other items are accessed infrequently. In this case, LFU would keep the frequently accessed items in the cache longer, while LRU might evict them in favor of more recently accessed but less frequently used items.


*** THEIRS (remote) ***

def get_value(key):
    value = cache.get(key)
    if value is not None:
        return value
    value = database.get(key)
    cache.set(key, value)
    return value
