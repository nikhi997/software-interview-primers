# Chapter 12: Keeping it running

*[← Chapter 11](hld-chapter-11.md) · [Contents](hld-README.md)*

- [ ] **Mark as read**

You've designed the system. You've drawn the diagram — boxes, arrows, an API, a data model. In a real company, that diagram is where the *easy* part ends. Because a design on a whiteboard does nothing. Someone has to get the code onto those boxes, keep the boxes alive at 3am, and notice *before the users do* when one of them starts to rot.

That someone is what people mean by "the DevOps people" (or SRE — we'll untangle the names at the end). And increasingly, the interviewer means it too: after you draw the system, a strong follow-up is *"okay — how would you deploy this? How do you know it's healthy? What's your rollback plan?"* Candidates who can only draw boxes go quiet here. This chapter is so you don't.

We'll do it the same way we did everything else: **start with the manual, painful version, feel exactly where it hurts, then add the one tool that fixes that pain.** Don't memorize a toolchain. Derive it.

The principle for this chapter: *feel the operational pain before reaching for the tool.*

---

## Start here: one engineer, doing it all by hand

Your app is built. To put a new version live, you — a human — do this:

1. Pull the latest code onto the server over SSH.
2. Run the tests (if you remember to).
3. Restart the process.
4. Refresh the page and squint to see if it still works.

For one server and one engineer, this is *fine.* Like Chapter 1's single box, don't add anything yet. But let's grow it the way real systems grow, and watch each step break.

---

## Pain #1: "I shipped a bug because I skipped the tests" → CI/CD

The first thing that breaks isn't a machine — it's *you.* You're in a hurry, you skip step 2, and a broken build goes live. Or two people deploy at once and clobber each other. Or the tests pass on your laptop but you forgot to run them on a clean checkout.

The pain is **manual, inconsistent, human-driven release.** The fix is to take the human out of the loop: a **pipeline** that runs *automatically* every time code is pushed.

- **CI — Continuous Integration:** on every push, a server checks out the code *fresh*, builds it, and runs the whole test suite. If anything is red, the change is blocked. No "works on my machine," no skipped tests — the pipeline doesn't get tired or take shortcuts.
- **CD — Continuous Delivery/Deployment:** if CI is green, the same pipeline packages the build and ships it — to staging automatically, and to production either on a button press (delivery) or fully automatically (deployment).

```
push code ─▶ [ build ] ─▶ [ test ] ─▶ [ package ] ─▶ [ deploy ]
                 │            │                            │
              fails? ◀────── red? ── stop, notify ───────┘
```

> 💡 **Concept notes — what CI/CD actually buys you**
> It's not "automation for its own sake." It's that **every change goes through the identical, un-skippable path**, so a release becomes boring and frequent instead of scary and rare. The deep payoff: when deploys are small and automatic, a broken one is easy to find (it was *that* tiny change) and easy to undo. Teams that deploy once a quarter have terrifying deploys; teams that deploy fifty times a day have forgettable ones. In an interview: "every merge runs build + tests in CI; green builds auto-deploy to staging, and to prod via a gated step" is the answer that shows you've shipped real software.

---

## Pain #2: "It worked in test, but prod has a different Python" → containers

Your pipeline is green. You deploy. Prod falls over anyway — because the prod box has a different OS library, a different runtime version, a missing environment variable. The classic lament: *"but it works on my machine."*

The pain is **the environment is implicit.** Your code assumes a world (this Python, that library, these files) that isn't guaranteed to exist on the target machine.

The fix: stop shipping *just the code* and start shipping **the code plus its entire environment, bundled together.** That bundle is a **container** (Docker being the common tool). A container image pins the OS userland, the runtime, the dependencies, and your app into one immutable artifact. The box it lands on barely matters, because the container brings its own world.

> 💡 **Concept notes — container vs VM, in one breath**
> A **virtual machine** virtualizes the *hardware* and runs a whole guest OS — heavy, slow to boot. A **container** shares the host's OS kernel and isolates only the process and its files — lightweight, boots in milliseconds, so you can pack many per machine. The interview soundbite: *"containers make the environment part of the artifact, so 'works on my machine' becomes 'works everywhere the image runs.'"* That immutability is also what makes a rollback trivial — you just run the previous image.

---

## Pain #3: "I'm restarting crashed containers by hand all night" → orchestration

Now you're stateless (Chapter 2) and containerized, so you scale the obvious way: run lots of containers across lots of machines. Then reality lands. One crashes at 2am — who restarts it? A machine dies — who reschedules its containers elsewhere? You deploy a new version — who replaces the old containers without dropping traffic? You need *more* capacity at peak — who adds containers, and removes them after?

Doing this by hand doesn't scale past a few boxes. The pain is **manually managing the lifecycle of many containers across many machines.**

The fix is an **orchestrator** (Kubernetes is the dominant one). You stop issuing commands and instead *declare the desired state*: "I want 10 copies of this container, always." The orchestrator's job is to **make reality match that declaration and keep it matching** — restarting crashed containers, rescheduling off dead machines, rolling out new versions, scaling on demand.

> 💡 **Concept notes — declarative, not imperative**
> This is the key mental shift. Imperative = "start a container" (a command you must repeat and babysit). Declarative = "there should always be 10 healthy containers" (a *goal* the system continuously reconciles). You describe the destination; the orchestrator drives there and corrects drift forever. This is the same idea as a database constraint or a thermostat: state the invariant, let the system enforce it. You don't need to know Kubernetes YAML for most interviews — you need to say *"an orchestrator keeps N healthy replicas running, reschedules failures, and handles rollouts,"* and mean it.

---

## Pain #4: "It's live and I have no idea if it's healthy" → observability

Everything's running. A user emails: *"the site is slow."* You SSH in and start guessing. Which service? Slow how? Since when? You're **blind** — the system is a black box and you're debugging by anecdote.

The pain is **no visibility into a running system.** The fix is to make the system *tell you* how it feels, continuously. This is **observability**, and it has three classic pillars:

- **Metrics** — numbers over time: requests/sec, error rate, p99 latency, CPU, queue depth. Cheap to store, great for dashboards and alerts. *"Error rate jumped to 5% at 14:03."*
- **Logs** — timestamped event records. Detailed, higher volume. *"At 14:03, order 9981 failed: payment timeout."*
- **Traces** — the path of a single request *across* services. In a system like your Chapter 11 diagram, one request hops through load balancer → service → cache → DB → queue. A trace stitches those hops together so you can see *where* the 800ms went.

```
metrics ─▶ "something is wrong, and roughly where"   (the alarm)
logs    ─▶ "here's exactly what happened"            (the detail)
traces  ─▶ "here's which hop in the chain was slow"  (the path)
```

> 💡 **Concept notes — monitoring vs observability**
> *Monitoring* answers questions you knew to ask (a dashboard for CPU). *Observability* is having enough signal to answer questions you *didn't* anticipate — to debug a novel failure you've never seen. The practical rule: instrument the **golden signals** — latency, traffic, errors, saturation — on every service. When the interviewer asks "how do you know it's healthy?", naming metrics/logs/traces and the golden signals is the senior answer. "I'd check the server" is the junior one.

---

## Pain #5: "Is it reliable *enough*?" — the question with no number → SLI / SLO / error budgets

Your dashboards are green-ish. The PM asks: *"are we reliable enough to launch?"* You say "I think so?" — and that's the problem. "Reliable" with no number is an argument waiting to happen. Worse, chasing *perfect* reliability is a trap: the last fraction of a nine can cost more than the whole rest combined, and it freezes you from ever shipping features.

The pain is **reliability with no agreed definition or budget.** The fix is to make it numeric (this is the heart of **SRE — Site Reliability Engineering**):

- **SLI — Service Level *Indicator*:** the *measurement.* e.g. "% of requests served under 200ms" or "% of requests that succeed."
- **SLO — Service Level *Objective*:** the *target* for that indicator. e.g. "99.9% of requests succeed each month." This is a number you choose and defend.
- **SLA — Service Level *Agreement*:** the SLO written into a *contract* with consequences (refunds) if you miss it. The SLO is your internal goal; the SLA is the promise to the customer, usually set looser than the SLO.
- **Error budget:** the flip side of the SLO. 99.9% allowed failure means **0.1% is your budget to spend.** Over a month that's ~43 minutes of downtime you're *allowed.*

> 💡 **Concept notes — the error budget is the whole trick**
> The error budget turns reliability from a vague virtue into a *currency.* If you're under budget, you have room to take risks — ship fast, deploy often. If you've *blown* the budget this month, you stop shipping features and spend the time on stability instead. It dissolves the eternal fight between product ("ship faster!") and ops ("stop breaking things!") by giving both a shared, numeric referee. The interview gold: *"we don't aim for 100% — we set an SLO, and the error budget tells us when to slow down and harden vs. when we have room to move fast."*

This also connects straight back to Chapter 10's "nines": an SLO *is* a target number of nines, and the error budget is just the downtime those nines permit, made spendable.

---

## Pain #6: "I shipped to everyone at once and took down everyone at once" → release strategies

CI/CD makes deploys easy — maybe *too* easy. You push a bad version to **100% of users instantly**, and 100% of users instantly see the outage. The deploy itself became the incident.

The pain is **all-or-nothing releases.** The fix is to **expose a new version gradually**, so a bad one hurts a few people for a few minutes instead of everyone all at once:

- **Rolling update:** replace old containers with new ones a few at a time. No downtime, but old and new run side by side briefly (your code must tolerate that).
- **Blue-green:** stand up the new version ("green") fully alongside the old ("blue"), then flip the load balancer from blue to green in one move. Instant switch, instant rollback (flip back), but you pay for double the capacity during the change.
- **Canary:** send a *small* slice of traffic (say 1%) to the new version, watch its metrics (Pain #4 pays off here), and only widen to 100% if it stays healthy. The most surgical option — you catch the bad release while it's hurting almost no one.

> 💡 **Concept notes — every release strategy is buying the same thing: a small blast radius**
> They differ in cost and speed, but the goal is identical — *limit how many users a bad deploy can hurt, and make undoing it fast.* Canary is the interview favorite because it pairs naturally with observability: "ship to 1%, watch error rate and latency, auto-roll-back if they spike, otherwise ramp up." Notice this is the error budget in action — a canary spends a tiny, bounded slice of the budget to de-risk the full rollout.

---

## Pain #7: "I built prod by clicking in a console and can't reproduce it" → Infrastructure as Code

One more thing rots quietly. You set up prod by clicking around a cloud console — created the load balancer here, the database there, opened a firewall port by hand. Six months later you need an identical staging environment, or you need to rebuild after a region outage, and *nobody remembers the exact clicks.* The environment is a one-of-a-kind artifact that exists only in someone's memory.

The pain is **infrastructure created by hand is unreproducible and undocumented.** The fix: describe the infrastructure itself in **code** — a text file that says "one load balancer, three app servers, this database, these firewall rules." Tools (Terraform being the common one) read that file and **make the cloud match it.**

> 💡 **Concept notes — Infrastructure as Code (IaC)**
> Your infrastructure becomes a program you check into git: **version-controlled** (every change is reviewable and revertible), **reproducible** (spin up an identical staging or DR environment from the same file), and **self-documenting** (the file *is* the source of truth, not tribal memory). It's the exact same "declarative, reconcile to desired state" idea as the orchestrator in Pain #3 — just applied to the *infrastructure* (servers, networks, databases) instead of the containers running on it. When asked "how do you manage your environments?", *"infra is defined as code in version control, so prod and staging are reproducible from the same source"* is the answer.

---

## So... what do "the DevOps people" actually do?

Step back and look at what we built, in order:

```
CI/CD          ─ ship code safely and automatically
containers     ─ make the environment part of the artifact
orchestration  ─ keep N healthy copies running, self-healing
observability  ─ see how the live system feels (metrics/logs/traces)
SLI/SLO/budget ─ define "reliable enough" as a number, and a budget
release strategy ─ expose change gradually, small blast radius
IaC            ─ define the whole environment as reproducible code
```

That whole column *is* the job. A couple of names you'll hear:

- **DevOps** is really a *culture/practice*: tear down the wall between the people who *write* code ("Dev") and the people who *run* it ("Ops") so the same team owns a service from commit to production. The tooling above exists to make that ownership practical.
- **SRE (Site Reliability Engineering)** is Google's concrete take on it: treat operations as a *software* problem, and make reliability measurable and budgeted (Pain #5). In practice the SLO/error-budget machinery comes from the SRE world.
- **Platform engineering** is the newer flavor: a team builds an internal platform (paved-road pipelines, ready-made deploy + observability) so *product* engineers self-serve all of the above without becoming experts in each tool.

> 💡 **Concept notes — the unifying idea, the same one as the whole book**
> Look at the column again: CI/CD, orchestration, and IaC are all the *same move* — **declare the desired state and let an automated system continuously reconcile reality to it**, instead of a human issuing one-off commands. Observability is how you *check* reality matches intent; SLOs define *how close* it must match; release strategies make *changing* the intent safe. "DevOps people" build and run that reconciling machinery. It's Chapter 11's diagram, kept alive — and just like the rest of HLD, each piece is here because a specific operational pain demanded it, not because it's on a list of best practices.

---

## How this shows up in the interview

You usually won't get a whole interview on this — but you'll get *probed* on it after you draw a system, and a crisp answer separates seniors from juniors:

- *"How would you deploy a change to this?"* → "CI runs build + tests on every merge; green builds roll out via canary — 1% first, watch error rate and p99, auto-rollback on regression, then ramp."
- *"How do you know it's healthy?"* → "Golden signals — latency, traffic, errors, saturation — as metrics on every service, structured logs for detail, distributed tracing to find the slow hop. Alert on SLO burn, not on raw CPU."
- *"What's your rollback plan?"* → "Immutable container images, so rollback is redeploying the previous image; blue-green or canary makes the switch instant."
- *"How reliable will it be?"* → "Pick an SLO — say 99.9% success — and run to its error budget: under budget we ship fast, over budget we freeze features and harden."

Notice these reuse everything: stateless services (Ch 2) make rolling deploys safe; the nines (Ch 10) become the SLO; the queue (Ch 6) needs its *depth* watched as a saturation signal. Operations isn't a separate topic bolted on — it's how the design you drew stays standing.

---

## Try it

1. You deploy 30 times a day and a bad release slips through about once a week. Walk through *which* of the seven tools above most directly shrinks the damage of that weekly bad release, and why — then name the *second* one that helps and how it pairs with the first.
2. Define an SLI, an SLO, and an error budget for the *redirect* path of the URL shortener from the upcoming interview-ritual chapter (hint: redirects must be fast and available). Pick concrete numbers and justify them. How many minutes/month of failure does your budget allow?
3. Compare blue-green vs canary for a payment service. Which would you choose, and what does each cost you (think capacity, speed of rollback, and blast radius)?
4. Your dashboard shows p99 latency spiking but average latency is flat. What does that tell you, and which of the three observability pillars do you reach for next to find the cause?
5. Explain, to a skeptical PM, why aiming for 100% reliability is the *wrong* goal — using the error-budget idea. What does the budget let the team do that "be as reliable as possible" does not?

*Write your answers in [hld-chapter-12-tryit.md](code/hld-chapter-12-tryit.md).*

---

## The bumper sticker

> *Operations is the design kept alive: ship safely through a pipeline, package the environment into the artifact, declare the running state and let it self-heal, watch the golden signals, define "reliable enough" as a number with a budget, and change things in small blast radii. Every one of those exists because a specific 2am pain demanded it.*

Next: the interview ritual itself — six steps, applied end-to-end to a URL shortener at scale — the loop you'll run on every problem for the rest of the book.

---

<div align="right">

[Chapter 13 →](hld-chapter-13.md)

</div>
