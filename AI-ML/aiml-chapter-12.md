# Chapter 12: Letting the model act

*[← Chapter 11](aiml-chapter-11.md) · [Contents](aiml-README.md)*

- [ ] **Mark as read**

So far the LLM only produces *text.* But the most powerful — and most hyped — AI systems do things: search the web, query a database, send an email, book a meeting, run code, call other software. The jump from "a model that talks" to "a model that *acts*" is the leap to **tools** and **agents**, and it's where a huge share of the new "AI Engineer" roles live. It's also where the engineering gets genuinely hard, because a system that can act can act *wrongly.* This chapter is about how that capability works and how to keep it on a leash.

---

## The key idea: the model can't act, so it *asks*

An LLM can't actually send an email or hit a database — it only emits text. The trick is beautifully simple: you tell the model what tools exist, and when it wants to use one, it **outputs a structured request** ("call `send_email` with these arguments"). *Your code* sees that request, actually runs the function, and feeds the result back to the model. The model decides *what* to do; your code does it and reports back.

> 💡 **Concept notes — tool / function calling**
> **Function calling** (or **tool use**) lets an LLM invoke external code. You describe available functions to the model — name, what each does, and the arguments it takes (a schema). When the model judges a function is needed, instead of answering it returns a structured call like `get_weather(city="Paris")`. Your application **executes** the function, captures the result, and passes it back into the context. The model then uses that result to continue or answer. Critically: **the model only *requests* the action; your code remains the gatekeeper that actually performs it.** That gatekeeping is your main control point for safety.

This is also how LLMs overcome their built-in limits (Chapter 9): can't do math reliably? Give it a calculator tool. Doesn't know today's date or live data? Give it a search tool or an API. Can't see your database? Give it a query tool. **Tools are how an LLM reaches past its frozen training data into the live world.**

---

## From a single tool to an agent

Call a tool once and you have a *tool-using* model. Let the model **loop** — decide an action, see the result, decide the next action, repeat until the goal is met — and you have an **agent.**

> 💡 **Concept notes — agents and the ReAct loop**
> An **agent** is an LLM that pursues a goal over multiple steps, choosing and using tools along the way, using each result to inform its next move. The common pattern is the **ReAct loop** (Reason + Act): the model **reasons** about what to do next, **acts** by calling a tool, **observes** the result, then reasons again — looping until done. Example: "What's the weather where our biggest customer is?" → *reason:* I need the biggest customer → *act:* query DB → *observe:* "Acme, in Denver" → *reason:* now I need Denver's weather → *act:* call weather API → *observe:* "snowing" → *answer.* The agent decomposed a task and chained tools **without you scripting the steps.** That autonomy is the appeal — and the danger.

> 💡 **Concept notes — what makes agents hard**
> Agents are powerful but **unreliable**, and honesty about this is a senior signal. Each step can err, and **errors compound** across a loop — a wrong decision at step 2 derails everything after. They can get stuck in loops, call the wrong tool, misread a result, or run up cost and latency by taking many steps. They're **non-deterministic**, so the same task can play out differently each run, making them hard to test and debug. The current engineering reality: keep agents **narrow** (few, well-defined tools), cap the number of steps, add checkpoints, and design for failure. "Agents are promising but brittle, so I'd scope them tightly and build in guardrails and step limits" is a far stronger answer than uncritical hype.

---

## Workflow first; agent only where judgment earns its risk

Teams often call any multi-step LLM system an "agent." That hides the most important design choice: **who chooses the next step?**

> 💡 **Concept notes — workflow vs agent**
> A **workflow** has a path your code owns: classify → retrieve → draft → validate → request approval. The model may perform a step, but transitions, retries, and allowed actions are explicit. An **agent** lets the model choose the next action and repeat until it believes the goal is complete. Workflows are easier to test, resume, audit, and bound; agents are useful when the path genuinely cannot be enumerated cheaply.
>
> Start with the workflow. Add **bounded autonomy** only inside the uncertain part: a research step may choose among three read-only tools for at most five turns, while authorization, spending limits, completion criteria, and final side effects remain deterministic. Autonomy is a budget — steps, time, money, permissions — not an on/off label.

This distinction also catches a common overbuild: if the business process already has five known stages, replacing the stage machine with a free-running planner removes reliability without adding useful capability.

Anthropic's [Building effective agents](https://www.anthropic.com/engineering/building-effective-agents) explains this workflow/agent distinction through simple composition patterns (reviewed 2026-10-09). The useful lesson is the control-flow boundary, not adopting that vendor's tooling.

---

## Durable execution: the loop must survive real systems

An in-memory demo forgets everything when the process crashes. A production workflow may wait minutes for a provider, hours for approval, or days for a user reply. It needs durable state outside the model.

> 💡 **Concept notes — checkpoints, idempotency, and receipts**
> Persist the workflow's current state, inputs, tool results, approval decision, and a stable operation ID after every meaningful step. On retry, **resume from the checkpoint** instead of replaying the whole conversation. Make side-effecting tools **idempotent**: the receiving service must enforce that the same operation ID and payload submitted twice return the original result rather than charging twice or sending two emails. Record a receipt for each action; after a timeout, reconcile the operation's status rather than infer that it failed. If the service lacks deduplication or a reliable status lookup, pause for reconciliation — a local key alone cannot make the remote action safe to repeat.
>
> Put **approval gates** in code, not prose. The model can propose a refund, but only a separate authorized transition can execute it. Approvals expire, bind to the exact arguments reviewed, and are invalidated if those arguments change.

Durability does not make the model smarter. It makes the surrounding process recoverable, which is more valuable when a non-deterministic component sits inside it.

---

## The safety problem: capability cuts both ways

A model that can *only talk* can at worst say something wrong. A model that can *act* can delete data, spend money, send messages, or leak information. The instant you grant tools, security and safety stop being optional.

> 💡 **Concept notes — guardrails for acting systems**
> Core principles for any tool-using/agentic system:
> - **Least privilege:** give the model the *minimum* tools and permissions for the job. Don't hand it a `delete_records` tool if it only needs to read. A read-only database role beats a read-write one.
> - **Human-in-the-loop for risky actions:** require explicit human confirmation before anything destructive, costly, or irreversible (sending money, emailing customers, deleting data). The model proposes; a human approves.
> - **Validate the model's requests:** never pass model-generated arguments straight into a sensitive call. Check and sanitize them — the model could be wrong, or hijacked.
> - **Prompt injection becomes critical here (Chapter 10):** if an agent reads external content (a web page, an email, a document) and that content contains hidden instructions, the agent might *act* on them — exfiltrate data, misuse a tool. This is the scariest LLM-security scenario precisely *because* the model can act. Untrusted content + action capability = treat with extreme caution.
> - **Sandbox and limit:** cap steps, set spending/rate limits, run code tools in isolated environments, and record scoped, redacted audit metadata under a retention policy.
> The mantra: **the more a system can do, the more it can do wrong — so constrain capability to the task and put a human between the model and anything irreversible.**

---

## Protocol boundaries: MCP is not A2A, and neither is a trust boundary

> 💡 **Concept notes — tool protocol vs agent protocol (fast-moving)**
> **MCP** standardizes how an AI application connects to tools, resources, and prompt templates exposed by a server. The **Agent-to-Agent (A2A) protocol** addresses a different boundary: agents discovering one another, exchanging tasks/messages, and reporting status. A weather tool is an MCP-shaped capability; delegating a research task to another independently-operated agent is an A2A-shaped interaction. These conceptual boundaries were checked against the [MCP specification](https://modelcontextprotocol.io/specification/2026-07-28) and [A2A core concepts](https://a2a-protocol.org/latest/topics/key-concepts/) on 2026-10-09. The specifications evolve; check their current versions before implementing wire details.
>
> Neither protocol grants trust. Your host still authenticates the peer, authorizes every capability, validates schemas, applies tenant scope, limits data returned, and records audit events. **Interoperability tells components how to talk; your application decides what they are allowed to do.**

> 💡 **Concept notes — where agents are heading (fast-moving)**
> Two designs are useful to recognize without assuming either is an upgrade. **Multi-agent systems:** instead of one agent doing everything, several specialized agents collaborate — a "planner" delegates to "worker" agents, or agents critique each other's output — which may help on separable tasks but adds cost, latency, and coordination failure modes. **Agentic RAG:** the retrieval step (Chapter 11) itself becomes agentic — the model decides *what* to search for, reformulates queries, and retrieves in a loop rather than once. The durable takeaway: more autonomy gives the system more choices and more ways to fail. Compare either design with a single workflow on your task's evals before adopting it.

---

## Try it

1. An LLM can't actually send an email. Walk through exactly how a "send the customer an apology email" request gets executed in a function-calling system — who does what?
2. What turns a single tool call into an "agent"? Describe the ReAct loop in your own words.
3. Why do errors "compound" in an agent loop in a way they don't for a single LLM answer? What does that imply for how you scope an agent?
4. You're building an agent that can query *and modify* a production database. List three guardrails you'd insist on before launch.
5. Explain why prompt injection is more dangerous for an agent that browses the web than for a plain chatbot.
6. Give two of the LLM's built-in limits (from Chapter 9) and the tool you'd add to overcome each.
7. A five-stage business process has known transitions but one ambiguous research step. Which part should be a workflow, which part might be agentic, and what budgets bound it?
8. Why must a retried `send_email` tool accept an idempotency key? What receipt would you persist before moving to the next step?
9. Distinguish MCP from A2A. Why does adopting either protocol leave authorization as your responsibility?


---

## The bumper sticker

> *Tools let an LLM act: it only *requests* an action in structured form, and your code stays the gatekeeper that runs it. Loop that and you get an agent — powerful, brittle, and dangerous, so grant least privilege, cap the steps, and keep a human between the model and anything irreversible.*

Next: how you actually know any of this works — evaluating LLM systems and keeping them safe, the discipline that separates demos from products.

---

<div align="right">

[Chapter 13 →](aiml-chapter-13.md)

</div>
