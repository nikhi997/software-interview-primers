# Chapter 10: Platform engineering & production operations — Try it

*Answers for the Try it questions in
[interview-topics-chapter-10.md](../interview-topics-chapter-10.md).*

For each answer, lead with the concept, state the operating tradeoff, name a failure mode, and end
with how you would verify the outcome. Product names are optional.

1. Explain image vs container vs VM, then review a container build for three production risks.



2. A Pod cannot serve traffic for 40 seconds. Design its startup, readiness, and liveness probes.



3. Design a build-once/promote-many CI/CD path, including supply-chain and production gates.



4. Review an IaC plan that replaces a database. What do you stop and investigate?



5. Design zero-downtime secret rotation for a database credential.



6. Trace one slow request using metrics, traces, and logs. What does each signal contribute?



7. Choose rolling, blue/green, or canary for a risky release and define stop/rollback conditions.



8. You are incident commander for rising 5xxs after a deploy. Narrate the first 15 minutes.



9. Give an honest pivot from a platform brand you know to one you do not.



## Dependency-free lab

Run:

```bash
python3 Interview-Topics/code/platform_ops_lab.py
```

Then change one input at a time and predict the result before running it:

- make canary error rate `0.021`;
- make canary p95 latency `420`;
- remove `traceparent` from the outbound headers;
- put `api_key` into the sample event;
- add a new rollout gate for saturation.

Write the invariant each change tests:

| Change | Prediction | Invariant / operational reason | Observed |
|---|---|---|---|
| Error rate |  |  |  |
| p95 latency |  |  |  |
| Missing trace context |  |  |  |
| Secret-like field |  |  |  |
| Saturation gate |  |  |  |
