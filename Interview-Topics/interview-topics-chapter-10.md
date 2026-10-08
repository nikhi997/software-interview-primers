# Chapter 10: Platform engineering & production operations

*[← Chapter 9](interview-topics-chapter-9.md) · [Contents](interview-topics-README.md)*

- [ ] **Mark as read**

Writing a service is only half the job. The other half is getting the same artifact through
environments, giving it the right identity and configuration, observing what it does, changing it
without an outage, and recovering when reality disagrees with the plan. Job descriptions name
Docker, Kubernetes, Terraform, GitHub Actions, Argo CD, Vault, and OpenTelemetry. The concepts
underneath are **packaging, scheduling, repeatable change, secret delivery, telemetry, controlled
rollout, and recovery**.

The principle still holds: **feel the concept beneath the brand name.** A candidate who can explain
why a readiness probe differs from a liveness probe can move between Kubernetes and another
orchestrator. A candidate who only remembers `kubectl` commands cannot.

---

## Containers: one immutable artifact, not a tiny virtual machine

> 💡 **Concept notes — image, container, registry**
> An **image** is a layered, immutable filesystem plus process metadata. A **container** is a
> running process created from that image, isolated with kernel namespaces and constrained with
> cgroups. A **registry** stores versioned images. Containers share the host kernel; a VM includes
> a guest kernel, so the isolation and overhead are different.

A production image should be reproducible, small, and unprivileged:

- pin dependencies and use a multi-stage build so compilers do not enter the runtime image;
- run as a non-root user, drop unnecessary capabilities, and prefer a read-only filesystem;
- copy dependency manifests before source to preserve useful layer caching;
- keep config and secrets **out** of the image;
- use a specific, immutable image digest for promotion, not a mutable `latest` tag;
- scan the image and produce an SBOM, but treat scanning as evidence, not proof of safety.

The application is the main process (PID 1), writes logs to stdout/stderr, handles termination
signals, and shuts down within the platform's grace period. Persistent state belongs in a managed
store or volume, not in the container's writable layer.

---

## Kubernetes: desired state plus reconciliation

> 💡 **Concept notes — what Kubernetes actually is**
> Kubernetes is a **declarative control system**. You submit desired state; controllers repeatedly
> compare desired and observed state and reconcile the gap. A **Pod** is the smallest scheduled
> unit, a **Deployment** manages stateless replicas and rolling updates, a **Service** gives changing
> Pods a stable virtual address, and **Ingress/Gateway** routes external traffic. ConfigMaps carry
> non-secret config; Secrets are a delivery object, not automatically a secure vault.

The scheduler places Pods using resource **requests**, constraints, and available capacity. CPU and
memory **limits** constrain consumption. Bad requests cause poor placement; overly tight memory
limits cause OOM kills; CPU limits can throttle. An HPA changes replica count from a signal, but it
cannot save a service whose downstream database is already saturated.

> 💡 **Concept notes — the three probes**
> - **Startup:** has a slow-starting process finished booting? Until yes, do not run the other probes.
> - **Readiness:** should this instance receive traffic *now*? Failure removes it from endpoints
>   without restarting it.
> - **Liveness:** is the process stuck beyond self-recovery? Failure restarts it.
>
> A dependency outage usually should fail readiness, not liveness. Otherwise every Pod restarts
> during a database incident and creates a restart storm.

Use namespaces and RBAC for boundaries, Pod disruption budgets for voluntary disruptions, and
anti-affinity/topology spread for failure-domain diversity. Stateful workloads add stable identity,
ordered operations, and storage concerns; do not reach for a StatefulSet when a managed database is
the simpler operational choice.

---

## CI/CD: prove, package, promote, verify

> 💡 **Concept notes — integration is not deployment**
> **CI** turns a commit into evidence and an immutable artifact: format/lint, unit tests, build,
> dependency and secret scans, integration tests, image signing. **Delivery** keeps that artifact
> releasable; **deployment** changes a running environment. A good pipeline builds once and promotes
> the same digest through environments instead of rebuilding different bits for production.

A useful sequence is:

`commit → fast checks → tests → build once → scan/sign → publish digest → deploy lower environment → integration/smoke checks → approval/policy gate → progressive production rollout → verify SLOs → record provenance`

Protect the pipeline itself: least-privilege workload identity, pinned third-party actions, reviewed
workflow changes, isolated untrusted pull requests, short-lived credentials, and auditable approvals.
Fast feedback and safe change matter more than the vendor's YAML syntax.

**Continuous deployment** is not "no controls." It replaces a manual ceremony with automated
evidence, policy, progressive exposure, and an automatic stop or rollback.

---

## Infrastructure as Code: reviewable desired state

> 💡 **Concept notes — IaC beneath Terraform**
> Infrastructure as Code represents infrastructure as versioned desired state. A plan previews the
> delta; an apply changes reality; a state record maps configuration to real resources. Pulumi,
> CloudFormation, Bicep, and Terraform differ in language and state mechanics, not in the reason:
> repeatability, review, audit, and drift visibility.

Keep modules small with explicit inputs/outputs. Separate state and permissions by environment and
blast radius. Lock remote state, encrypt it, and never place secrets in outputs. Review the plan,
pin providers/modules, test policy, and reconcile **drift** rather than normalizing console edits.

IaC is not automatically idempotent or safe. Renaming a resource may look like delete-and-create;
an apparently small network change may disconnect production. Read the plan for replacements,
deletions, permission expansion, and data movement. Back up state and know the recovery path before
an apply.

---

## Secrets and workload identity

> 💡 **Concept notes — a secret is a lifecycle, not a string**
> Secrets need creation, storage, scoped delivery, rotation, revocation, and audit. Keep them out of
> source, images, CI logs, command-line arguments, telemetry, and Terraform state. Prefer a workload
> identity and short-lived credentials over a long-lived key. Fetch at runtime or mount through an
> approved integration; authorize each workload only for what it needs.

Kubernetes Secrets are base64-encoded API objects unless additional encryption and access controls
are configured. They are not equivalent to Vault, AWS Secrets Manager, GCP Secret Manager, or Azure
Key Vault. Whichever store you use, plan rotation without downtime: support overlapping old/new
credentials, reload safely, verify adoption, then revoke the old value. If a secret leaks, rotate
first and investigate; deleting the Git line does not erase history or exposure.

---

## OpenTelemetry and observability

> 💡 **Concept notes — signal, context, backend**
> **OpenTelemetry (OTel)** is vendor-neutral instrumentation and context propagation for traces,
> metrics, and logs. It is not the storage/query UI. SDKs or auto-instrumentation create telemetry;
> an OTel Collector can receive, process, sample, redact, and export it to one or more backends.

The three pillars answer different questions:

- **Metrics:** is there a broad problem? Track request rate, error rate, and duration, plus saturation.
- **Traces:** where did one request spend time across services? Propagate trace context across HTTP
  and messaging boundaries.
- **Logs:** what detailed event happened? Use structured fields and correlate with trace/request IDs.

Observability is the ability to answer new questions from emitted evidence, not merely "we have
dashboards." Instrument service boundaries and business outcomes; avoid high-cardinality metric
labels such as user IDs; sample intentionally; redact credentials and personal data before export.
Alert on user-visible symptoms and SLO burn, not every internal wiggle.

**SLI** is a measured behavior (successful requests, latency). **SLO** is its target over a window.
The **error budget** is the tolerated unreliability. It creates a shared release/risk decision: when
the budget burns too fast, reduce change and restore reliability.

---

## Deployment, verification, and rollback

> 💡 **Concept notes — a rollout is an experiment**
> A rolling deployment replaces instances gradually. **Blue/green** prepares a full parallel
> environment and switches traffic. A **canary** exposes a small cohort first and expands only while
> guardrails hold. A feature flag separates code deployment from feature release. Choose based on
> cost, risk, observability, and whether old and new versions can coexist.

Before rollout, define success and stop conditions: error rate, latency, saturation, business
metrics, and a comparison window. During rollout, watch both application and dependencies. After
rollout, verify the version, traffic, schema, queues, and business outcome—not just "the job was
green."

Rollback is a designed capability:

- keep the prior artifact and configuration available;
- make database changes **expand/contract**: add compatible schema, deploy readers/writers, migrate,
  then remove old schema later;
- make messages and APIs tolerant of mixed versions;
- distinguish rollback from roll-forward when data has already changed;
- rehearse rollback and record who may trigger it.

A deployment can succeed while the release fails. The pipeline reports mechanism; users and SLOs
report outcome.

---

## Incident response: stabilize, communicate, learn

> 💡 **Concept notes — incident work has phases**
> **Detect and declare.** Name severity, impact, commander, responders, and a communication channel.
> **Stabilize.** Protect users: rollback, disable a flag, shed load, fail over, or reduce scope.
> **Diagnose.** Build and test hypotheses from the timeline and telemetry; preserve evidence.
> **Recover and verify.** Confirm user-visible health, drain backlogs carefully, and watch recurrence.
> **Learn.** Write a blameless review with contributing conditions and owned, prioritized actions.

During an incident, separate command, operations, investigation, and communications when the team is
large enough. Time-stamp decisions. Prefer reversible mitigations. Do not let ten people change the
same system without coordination. Give stakeholders factual updates: impact, current mitigation,
next checkpoint, and uncertainty—never an invented ETA.

Root cause is rarely a single careless person. Ask why the system allowed one action to create that
impact: missing guardrail, unsafe default, weak test, hidden coupling, poor detection, or excessive
blast radius. Actions should change the system, not merely say "be more careful."

---

## The concept-beneath-brand map

| Brand names you may hear | Concept to lead with | Useful follow-up |
|---|---|---|
| Docker, containerd, OCI | Immutable process packaging and isolation | Image layers, PID 1, non-root, digest promotion |
| Kubernetes, ECS, Nomad | Scheduling plus desired-state reconciliation | probes, requests/limits, rollout behavior |
| GitHub Actions, Jenkins, GitLab CI | Automated evidence and artifact promotion | build once, provenance, gates |
| Terraform, Pulumi, CloudFormation | Reviewable infrastructure desired state | plan, state, drift, blast radius |
| Vault, cloud secret managers | Secret lifecycle and scoped delivery | workload identity, rotation, audit |
| OTel, Prometheus, Datadog, Jaeger | Instrumentation, signals, storage/query | context, cardinality, sampling, SLOs |
| Argo CD, Flux | GitOps reconciliation | desired state, drift, rollback/roll-forward |

An honest pivot sounds like: "I have not operated Argo CD directly. I have used another deployment
controller where reviewed desired state was reconciled into the cluster, with progressive rollout
and health gates. I would map Argo's sync and health model onto that workflow, then learn its exact
resource and rollback semantics." Concept first, mapping second, boundary explicit.

---

## Try it

1. Explain image vs container vs VM, then review a container build for three production risks.
2. A Pod cannot serve traffic for 40 seconds. Design its startup, readiness, and liveness probes.
3. Design a build-once/promote-many CI/CD path, including supply-chain and production gates.
4. Review an IaC plan that replaces a database. What do you stop and investigate?
5. Design zero-downtime secret rotation for a database credential.
6. Trace one slow request using metrics, traces, and logs. What does each signal contribute?
7. Choose rolling, blue/green, or canary for a risky release and define stop/rollback conditions.
8. You are incident commander for rising 5xxs after a deploy. Narrate the first 15 minutes.
9. Give an honest pivot from a platform brand you know to one you do not.

*Write your answers in
[interview-topics-chapter-10-tryit.md](code/interview-topics-chapter-10-tryit.md), then run the
dependency-free rollout and trace lab in
[`platform_ops_lab.py`](code/platform_ops_lab.py) with `python3 Interview-Topics/code/platform_ops_lab.py`.*

## The bumper sticker

> *Platform engineering is the discipline of making change repeatable, observable, reversible, and
> boring. Containers package a process; orchestrators reconcile desired state; pipelines and IaC
> make change reviewable; identity and secret systems constrain access; telemetry shows reality;
> rollout gates and incident practice limit the blast radius. Learn those concepts and every brand
> becomes a dialect.*

---

<div align="right">

[Appendix →](interview-topics-appendix.md)

</div>
