You're designing a messaging app. You can shard by user_id or by message_id. The dominant query is "load all messages in this conversation." Which shard key do you choose and why? What goes wrong with the other one?

we need to shard by user_id because the dominant query is to load all messages in a conversation, which is likely to be associated with a specific user. Sharding by message_id would scatter messages across different shards, making it inefficient to retrieve all messages for a conversation, as it would require querying multiple shards and aggregating results.


Your service stores 800 GB total and does 200 writes/sec, on 4 TB disks. Should you shard? Justify with the numbers, and say what you'd do instead.
no sharding is needed .With 800 GB total data and 4 TB disks, we have ample storage capacity. The write throughput of 200 writes/sec is manageable on a single disk without causing performance issues. Instead of sharding, we can focus on optimizing the database performance through indexing, caching, and efficient query design to handle the load effectively. Sharding would add unnecessary complexity without providing significant benefits in this scenario.



Name two operations that were trivial on a single database but become expensive once data is sharded, and explain why.
fetching data across shards and performing transactions that span multiple shards become expensive once data is sharded.
