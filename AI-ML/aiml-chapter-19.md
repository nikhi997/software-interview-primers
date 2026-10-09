# Chapter 19: Context engineering, memory, and reliable AI workflows

*[← Chapter 18](aiml-chapter-18.md) · [Contents](aiml-README.md)*

- [ ] **Mark as read**

You built the assistant from Chapters 9–18: good prompt, good retrieval, scoped tools, evals, fallbacks. Then a real customer uses it for three days.

On day one they say, "Call the migration **Orchid** and never contact the customer before legal approves." On day two the assistant summarizes the thread to save tokens and drops the legal constraint. On day three it retrieves an older note that says direct contact is allowed, calls the email tool after a timeout retry, and sends two messages. Every component worked in isolation. The *workflow* failed because the right state did not reach the right step, with the right authority, at the right time.

That is the pain this chapter fixes. The next layer after prompting, RAG, and tools is **context engineering**: deliberately selecting, structuring, and governing the information a model sees. Around it sits **memory** — durable state with rules for writing, reading, correcting, and deleting — and a **reliable workflow runtime** that checkpoints progress and keeps side effects safe.

The mindset: **the model can only reason over the state you assemble, so engineer that state before asking for a smarter model.**

---

## First failure: "just send the whole conversation"

The simplest memory system is no memory system: resend the entire transcript on every turn. It feels faithful because nothing is intentionally omitted.

Then the thread grows. Cost and latency rise. Old instructions conflict with new ones. Retrieved documents, tool results, and chat messages all compete for attention. An indirect injection buried in an attachment remains in every future request. Eventually the request exceeds the context limit: depending on the API and client, it may be rejected or truncated. Neither is a substitute for an application-level decision about what deserved to survive.

> 💡 **Concept notes — context is not memory**
> The **context window** is the model's temporary working set for one call. It is not durable, not automatically authoritative, and not guaranteed to emphasize every included detail. **Memory** is application-managed state that can survive calls and be retrieved later. A transcript can be an input to memory, but repeatedly pasting it is not a memory design.
>
> Long context changes what *fits*, not what is relevant, current, permitted, or trustworthy. Chapter 11's choice still holds: use long context for a bounded artifact, RAG for a large changing corpus, and structured tools for authoritative live state.

So "include everything" fails twice: eventually it cannot include everything, and before then it includes too much.

---

## The move: build a context pipeline

Treat the model input as a compiled artifact, not an append-only string. For every call, construct a **context packet** from typed sources.

> 💡 **Concept notes — select, structure, and attribute**
> A practical context pipeline:
> 1. **Identify the decision.** What must this call decide or produce?
> 2. **Select minimum evidence.** Retrieve only the policies, recent turns, user facts, and tool results required for that decision.
> 3. **Resolve authority and freshness.** Prefer the system of record over a remembered sentence; prefer a newer approved fact over an older draft.
> 4. **Structure by role and type.** Keep developer instructions, untrusted content, retrieved evidence, tool results, and workflow state in distinct fields.
> 5. **Attach provenance.** Record source ID, timestamp/version, tenant scope, and trust level so claims can be cited and conflicts debugged.
> 6. **Budget and order.** Reserve space for the task and output; place critical constraints where the model and validator can reliably use them.
> 7. **Validate and log the manifest.** Check required fields and authorization before the call, then log source IDs and versions — not unrestricted sensitive text — for replay and evaluation.

The packet might contain:

```text
goal: draft_migration_update
workflow_state: awaiting_legal_approval
hard_constraints:
  - no_external_contact_before_approval  [decision: legal-42, version: 3]
recent_turns:
  - user correction: project_name = "Orchid"
retrieved_evidence:
  - migration-policy §4.2               [policy version: 12]
tool_results:
  - account_status = active             [CRM read at 14:03Z]
untrusted_content:
  - customer attachment excerpt         [never instructions]
```

This is still a prompt underneath. The improvement is that your code knows what each piece *is*, why it is present, and which checks apply before and after generation.

Typed fields and role separation do not make prompt injection impossible. Authorization and the "no external contact" constraint must also be enforced by code before an action executes. A model treating untrusted text as an instruction must not be able to bypass that gate.

What if the required evidence and invariants still exceed the budget? **Do not silently drop a constraint.** Count tokens with the selected model's tokenizer, reserve output space, and either split the task into bounded steps, obtain a larger suitable context budget, or stop and report that the decision cannot safely be made with the available context.

---

## Second failure: the summary silently changes history

To control token growth, the team replaces old turns with a rolling summary. It works until "do **not** contact the customer" becomes "coordinate customer contact." Summarization is lossy compression; once the raw turns are discarded, the mistake becomes the assistant's new reality.

> 💡 **Concept notes — compaction needs invariants**
> Separate facts that may be summarized from **invariants** that must survive verbatim: approvals, denials, user corrections, safety constraints, operation IDs, and unresolved commitments. Keep raw event history under an appropriate retention policy; produce versioned summaries as derived views, not replacements for the source of truth. Before accepting a compacted summary, run checks that every active invariant and open task still appears.

Use hierarchical compaction for long work: recent turns verbatim, a checked summary for older turns, and retrieval into raw history when a detail becomes relevant. The workflow should know which summary version produced a decision, so it can replay or roll back after a bad compaction.

---

## Memory is a product feature with a write policy

"Remember everything about the user" sounds helpful until the system remembers a guess, keeps a deleted preference, leaks one tenant's note into another, or treats a temporary instruction as permanent.

> 💡 **Concept notes — useful memory types**
> - **Working memory:** the current context packet — temporary state for this call.
> - **Episodic memory:** what happened in prior interactions — decisions, completed actions, and their receipts.
> - **Semantic memory:** stable facts and preferences — preferred language, project name, organization policy.
> - **Procedural state:** where a durable workflow is — current step, pending approval, retry count, deadlines.
>
> These are application categories, not magical model faculties. Each needs a schema, owner, scope, retention rule, and source of truth.

Some memory taxonomies use **procedural memory** for learned procedures or reusable skills. That is different from the deterministic workflow state here: knowing how to request approval does not prove that this action has already been approved.

> 💡 **Concept notes — read and write deliberately**
> Do not let every model sentence become memory. A **write policy** decides what may be stored: explicit user preference, verified tool fact, approved decision, or completed action — not an inference presented as fact. Store provenance, confidence where appropriate, creation/update time, expiry, and tenant/user scope. Deduplicate repeated facts; represent corrections and supersession instead of keeping contradictory "truths."
>
> A **read policy** retrieves only memory relevant to the current task and authorized principal. Sensitive or stale memories may require re-confirmation. Users and operators need ways to inspect, correct, and delete retained memory; deletion must propagate to derived indexes and caches.

The model may *propose* "the user prefers email," but your application should ask whether that came from an explicit choice, an authorized system, or a guess from one interaction. Memory quality begins at write time.

---

## Reliable workflows keep the model inside a deterministic spine

Chapter 12 distinguished workflows from agents. Now make the workflow durable.

> 💡 **Concept notes — checkpoint the state machine**
> Model the business process as explicit states and allowed transitions:
>
> `drafting → awaiting_approval → approved → sending → sent`
>
> Persist the state and its version after each step. A worker claims a step, executes it, stores the result/receipt, and advances with a compare-and-set so two workers cannot both advance the same job. After a crash, resume from the last committed checkpoint. Timeouts create an **unknown outcome**, not permission to repeat a side effect blindly.

> 💡 **Concept notes — idempotency and exactly-once illusions**
> Networks can lose responses after the remote service acted. Design side-effecting tools around a stable **idempotency key** for the workflow's logical action; the receiver must atomically deduplicate the effect and reject a reused key with different arguments. Keep the key unchanged on retry, and record the receipt before advancing. Check the receiver's deduplication scope and retention window: retrying after that window may repeat the effect.
>
> A checkpoint and a local key cannot make a non-idempotent remote email service exactly-once. If the provider has neither deduplication nor a reliable operation-status lookup, leave the action in an **unknown** state and reconcile manually rather than automatically resend. You may achieve an exactly-once *business effect* within a defined service contract; do not assume a distributed call itself happens exactly once.

> 💡 **Concept notes — approvals bind to a version**
> A human approves a specific proposal: exact recipient, amount, content hash, evidence, and tool arguments. If context or arguments change, approval becomes invalid and the workflow returns to review. The model cannot reinterpret "approved" as blanket permission for a later action.

Inside that spine, an agentic step may choose among read-only research tools. Outside it, code owns authorization, budgets, retries, approvals, and completion.

---

## Conflicts: authority beats recency, recency beats repetition

Suppose the transcript says "customer contact is allowed," memory says it is blocked, and a policy document says legal approval is required. More copies of the transcript do not make it more authoritative.

Define a conflict policy before the model sees the conflict:

1. **Authorization and safety constraints** are hard gates.
2. **Systems of record and approved decisions** outrank conversational recollections.
3. Between equally authoritative facts, use version/freshness and surface unresolved disagreement.
4. If conflict remains, abstain and request clarification — do not ask the model to improvise a policy.

Record the winning source and losing alternatives in the trace. That makes "why did it do that?" answerable without exposing every raw input.

---

## Evaluate the context and memory, not just the answer

An answer can be wrong because the model reasoned badly, or because the application handed it the wrong state. Those need different fixes.

> 💡 **Concept notes — context and memory evals**
> Build fixture scenarios with a known set of required facts, distractors, stale facts, conflicting sources, permissions, and invariants. Measure:
> - **Context recall:** were all required facts included?
> - **Context precision:** how much included material was actually relevant?
> - **Authority/freshness accuracy:** did the packet select the correct source/version?
> - **Invariant preservation:** did compaction retain constraints, approvals, corrections, and open tasks?
> - **Memory write accuracy:** were only eligible facts stored, under the right scope and expiry?
> - **Workflow recovery:** after failure at every checkpoint, did resume avoid skipped steps and duplicate effects?
> - **Trace compliance:** did tools, approvals, budgets, and citations match policy?

Then keep answer-quality evals from Chapter 13. A bad packet with a lucky answer still fails; a good packet with a bad answer points to the model or prompt rather than retrieval/memory.

Test adversarially too: plant an instruction in old memory, revoke a permission, delete a user preference, make a tool timeout after acting, and change a proposal after approval. Reliability lives in these transitions, not the happy path.

---

## The design interview answer

When asked to design a long-running assistant, resist "vector database = memory." Walk the layers:

1. **Source of truth:** where authoritative facts and workflow state live.
2. **Memory write policy:** which verified events become durable, scoped state.
3. **Context builder:** how each call selects, orders, budgets, and attributes evidence.
4. **Workflow runtime:** explicit states, checkpoints, retries, idempotency, approvals.
5. **Evaluation and observability:** packet manifests, traces, recovery tests, user correction/deletion.

Only then discuss storage products or model choice. The hard part is not saving text; it is deciding what deserves to be remembered and making retries safe.

---

## Try it

1. A 200-page manual fits in a model's context window. Give three reasons you may still use retrieval, and one case where long context is the simpler choice.
2. Design a context packet for "refund this order." Which facts come from memory, RAG, and structured tools? Which source is authoritative for each?
3. A rolling summary drops "never email the customer." What should have been stored as an invariant, and how would a compaction check catch the loss?
4. Write a memory write policy for user preferences. Which statements are eligible, how are corrections represented, and how does deletion propagate?
5. A `send_email` call times out after the provider accepted it. Walk through the checkpoint, idempotency key, receipt lookup, and safe resume behavior.
6. A manager approved a $40 refund, then the model changed the amount to $400. Why is the old approval invalid even though the workflow still says `approved`?
7. Distinguish context recall from context precision. Give a failure with high recall/low precision and one with low recall/high precision.
8. Where would you allow bounded agent autonomy inside a durable workflow, and which transitions must remain deterministic?
9. Required facts and active constraints exceed the context budget. Why is truncation unsafe, and which alternatives can preserve correctness?
10. Your email provider does not enforce idempotency keys and a send timed out. Why is a local receipt table insufficient, and what state should the workflow enter?

---

## The bumper sticker

> *The model does not need every token you've ever seen; it needs the smallest authorized packet of current evidence for this decision. Store memory with a write policy, preserve invariants through compaction, and run the model inside a checkpointed, idempotent workflow so a retry cannot become a duplicate real-world action.*

That's the final engineering layer. The appendix that follows is your reference shelf — now including the vocabulary and interview questions for context, memory, and durable workflows.

---

<div align="right">

[Appendix →](aiml-appendix.md)

</div>
