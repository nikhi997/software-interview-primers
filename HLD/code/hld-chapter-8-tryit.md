Implement token bucket in words for "20 requests/sec sustained, bursts up to 50." Give B and R. What happens to the 51st simultaneous request, and how long until 10 more are allowed?
def implement_token_bucket():
    # B = 50 (burst capacity)
    # R = 20 requests/sec (sustained rate)

    # The token bucket starts with 50 tokens (B).
    # Each request consumes 1 token.
    # Tokens are replenished at a rate of 20 tokens per second (R).

    # If a client makes 51 simultaneous requests:
    # - The first 50 requests will be allowed, consuming all tokens.
    # - The 51st request will be rejected because there are no tokens left.

    # After the burst, tokens will start to replenish at the rate of 20 tokens/sec.
    # To allow 10 more requests, we need to wait until at least 10 tokens are available.
    # This will take 10 / 20 = 0.5 seconds.

    return "B = 50, R = 20. The 51st request is rejected. It takes 0.5 seconds for 10 more requests to be allowed."

Explain the fixed-window boundary problem with a concrete timeline, and how sliding window fixes it.
fixed-window boundary problem occurs when requests are counted in fixed time intervals, leading to potential spikes in traffic at the boundaries of those intervals.
For example, consider a fixed window of 1 minute with a limit of 100 requests.
- At 11:59:59, a user makes 100 requests, reaching the limit.
- At 12:00:00, the window resets, and the user can make another 100 requests immediately.
- This results in a total of 200 requests in just 1 second, which can overwhelm the system.
Sliding window fixes this by counting requests over a rolling time period rather than fixed intervals. Instead of resetting the count at the start of each minute, it continuously tracks the number of requests made in the last 60 seconds. This way, if a user makes 100 requests at 11:59:59, they will have to wait until some of those requests fall outside the 60-second window before they can make more requests, preventing the spike at the boundary.

Why must rate-limit counters live in a shared store (e.g., Redis) rather than in each edge server's memory? What abuse becomes possible if they don't?
rate-limit counters must live in a shared store like Redis because all edge servers need to have a consistent view of each user's request count. If each edge server maintains its own counters in memory, a user could exploit this by sending requests to different servers, effectively bypassing the rate limit. For example, if a user sends 50 requests to one server and then immediately sends another 50 requests to a different server, they would be able to make 100 requests in total, even if the intended limit is 100 requests per minute. This would allow users to exceed their quota and potentially overwhelm the system, leading to abuse and unfair usage of resources.

Describe a retry storm and the three-part fix that prevents it.

a retry storm occurs when a client repeatedly retries failed requests in rapid succession, often due to transient errors or timeouts. This can lead to a flood of requests that overwhelms the server, causing further failures and creating a vicious cycle.
The three-part fix to prevent a retry storm includes:
1. **Exponential Backoff**: Clients should implement an exponential backoff strategy, where the wait time between retries increases exponentially after each failure. This reduces the frequency of retries and gives the server time to recover.
2. **Jitter**: Adding randomness (jitter) to the retry intervals helps to prevent synchronized retries from multiple clients, which can lead to spikes in traffic. By randomizing the wait times, clients are less likely to retry at the same moment, reducing the overall load on the server.
3. **Retry Cap**: Implementing a maximum number of retries ensures that clients do not continue to retry indefinitely. Once the retry cap is reached, the client should stop retrying and handle the failure gracefully, such as by notifying the user or logging the error for further investigation. This prevents the system from being overwhelmed by an endless stream of retries.


Your database tier is overloaded by legitimate traffic. Rate limiting per client won't help (everyone's within their quota). Name three backpressure/degradation techniques you'd apply and what each sacrifices.
1. **Load Shedding**: This technique involves dropping low-priority requests to reduce the load on the database. For example, analytics events or background tasks could be deferred or discarded, allowing the system to focus on high-priority requests like user transactions. The sacrifice here is that some non-essential functionality may be temporarily unavailable.
2. **Circuit Breaker**: Implementing a circuit breaker pattern allows the system to stop calling a failing downstream service for a period of time. This prevents the database from being overwhelmed by requests that are likely to fail. The sacrifice is that users may experience temporary unavailability of certain features or services, but it helps maintain overall system stability.
3. **Graceful Degradation**: This technique involves serving a reduced experience instead of returning an error. For example, the system could serve stale cached data, a simplified page, or a message indicating that certain features are unavailable while still allowing core functionality to operate. The sacrifice is that users may not have access to the full range of features or the most up-to-date information, but they can still use the essential parts of the application.
