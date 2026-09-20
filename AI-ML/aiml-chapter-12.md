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

## The safety problem: capability cuts both ways

A model that can *only talk* can at worst say something wrong. A model that can *act* can delete data, spend money, send messages, or leak information. The instant you grant tools, security and safety stop being optional.

> 💡 **Concept notes — guardrails for acting systems**
> Core principles for any tool-using/agentic system:
> - **Least privilege:** give the model the *minimum* tools and permissions for the job. Don't hand it a `delete_records` tool if it only needs to read. A read-only database role beats a read-write one.
> - **Human-in-the-loop for risky actions:** require explicit human confirmation before anything destructive, costly, or irreversible (sending money, emailing customers, deleting data). The model proposes; a human approves.
> - **Validate the model's requests:** never pass model-generated arguments straight into a sensitive call. Check and sanitize them — the model could be wrong, or hijacked.
> - **Prompt injection becomes critical here (Chapter 10):** if an agent reads external content (a web page, an email, a document) and that content contains hidden instructions, the agent might *act* on them — exfiltrate data, misuse a tool. This is the scariest LLM-security scenario precisely *because* the model can act. Untrusted content + action capability = treat with extreme caution.
> - **Sandbox and limit:** cap steps, set spending/rate limits, run code tools in isolated environments, log everything for audit.
> The mantra: **the more a system can do, the more it can do wrong — so constrain capability to the task and put a human between the model and anything irreversible.**

---

## A note on "MCP" and the tool ecosystem

> 💡 **Concept notes — standardizing tools (fast-moving)**
> A practical pain point is that every app wired tools to models in its own ad-hoc way. Emerging standards (such as the **Model Context Protocol, MCP**) aim to give models a uniform way to discover and call external tools and data sources, so a tool built once works across many apps. The *specific* standards here are fast-moving — don't over-index on names — but the *direction* is durable: tools and data sources are becoming pluggable, standardized components that models connect to. Knowing the concept (a common interface between models and the outside world) matters more than any one protocol's current details.

> 💡 **Concept notes — where agents are heading (fast-moving)**
> Agentic systems are the field's most active frontier, and the trajectory is worth knowing even as specifics churn. Two directions dominate. **Multi-agent systems:** instead of one agent doing everything, several specialized agents collaborate — a "planner" delegates to "worker" agents, or agents critique each other's output — which can help on complex tasks but multiplies the cost, latency, and failure modes of a single agent. **Agentic RAG:** the retrieval step (Chapter 11) itself becomes agentic — the model decides *what* to search for, reformulates queries, and retrieves in a loop rather than once. The durable takeaway underneath the hype: more autonomy means more capability *and* more ways to fail, so the guardrails above matter *more* as agents grow more capable, not less. "Promising and improving fast, but I'd add autonomy only where the reliability controls keep up" stays the mature stance.

---

## Try it

1. An LLM can't actually send an email. Walk through exactly how a "send the customer an apology email" request gets executed in a function-calling system — who does what?
2. What turns a single tool call into an "agent"? Describe the ReAct loop in your own words.
3. Why do errors "compound" in an agent loop in a way they don't for a single LLM answer? What does that imply for how you scope an agent?
4. You're building an agent that can query *and modify* a production database. List three guardrails you'd insist on before launch.
5. Explain why prompt injection is more dangerous for an agent that browses the web than for a plain chatbot.
6. Give two of the LLM's built-in limits (from Chapter 9) and the tool you'd add to overcome each.


---

## The bumper sticker

> *Tools let an LLM act: it only *requests* an action in structured form, and your code stays the gatekeeper that runs it. Loop that and you get an agent — powerful, brittle, and dangerous, so grant least privilege, cap the steps, and keep a human between the model and anything irreversible.*

Next: how you actually know any of this works — evaluating LLM systems and keeping them safe, the discipline that separates demos from products.

---

<div align="right">

[Chapter 13 →](aiml-chapter-13.md)

</div>
