An app keeps a per-user shopping cart in the app server's memory. It runs fine on one server. List exactly what goes wrong when it scales to three servers behind a round-robin load balancer, and the fix.

When requests from the same user land on different servers, each server doesn't have the user's cart state — it's lost. Fix: externalize session state to Redis or a shared cache (works with round-robin), or use sticky sessions (locks the user to one server). The latter adds complexity: load imbalance and a SPOF if that server fails.



You measure that one app server handles 800 RPS before latency spikes. Your peak load is 6,000 RPS. How many servers do you run if you want to survive losing one at peak? Show the arithmetic.

6,000 RPS ÷ 800 RPS per server = 7.5 servers needed at peak. Round up to 8. Add 1 spare for failover = 9 servers.

"Sticky sessions" let you keep session state on the app server by always routing a user to the same box. Name two costs of this versus externalizing sessions to a shared store.

Load imbalance: You can't move users between servers without breaking their sticky session, so a power user on one server creates a hot spot. SPOF: If a server dies, every user pinned to it loses their session — their cart vanishes. Externalized sessions avoid both.



You add a load balancer to remove the app-server single point of failure. In one sentence, explain why the load balancer doesn't just move the SPOF, and what makes that true.


Load balancers are deployed in active-passive pairs (or active-active). If the primary fails, the secondary takes over via failover—or both serve traffic simultaneously. The cloud provider (or your infra team) manages this redundancy, so the LB isn't a SPOF. The real SPOF risk is in your app logic, not the infrastructure layer.
