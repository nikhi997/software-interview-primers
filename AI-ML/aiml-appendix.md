# Appendix: The AI/ML reference shelf

*[← Chapter 19](aiml-chapter-19.md) · [Contents](aiml-README.md)*

Everything in one place for fast review. Use this after you've read the chapters — it's a memory aid, not a substitute for the explanations.

Looking for something more active than a reference shelf? The [rebuild labs](aiml-rebuild-labs.md) turn each chapter into a runnable exercise, and [Model to Product](aiml-model-to-product.md) retells all 19 chapters as one continuous system build — read it once this appendix feels familiar.

---

## A. Glossary (every term in the track)

**Foundations**
- **Model** — a function learned from data; takes input, produces output.
- **Training** — finding the model's parameters from labeled examples.
- **Inference / prediction** — using a trained model on new input.
- **Features** — the input signals the model sees.
- **Label / target** — the correct answer for a training example.
- **Supervised learning** — learn input→answer from labeled data (most ML).
- **Unsupervised learning** — find structure in unlabeled data (clustering, anomalies).
- **Reinforcement learning** — learn from rewards by acting in an environment.
- **Classification** — predict a category. **Regression** — predict a number.
- **Sentiment analysis** — text classification that predicts the emotional tone of a piece of text (positive/negative/neutral); the canonical applied-NLP example.

**Data**
- **Feature engineering** — crafting useful features from raw data.
- **Train / validation / test split** — learn on train, tune on validation, score *once* on test.
- **Data leakage** — info in training that won't exist at prediction time (or encodes the answer); causes too-good-to-be-true results. Four flavours: **target leakage** (a feature is a consequence of the label), **train/test contamination** (same/near-duplicate rows on both sides), **temporal leakage** (using future data to predict the past; fix by splitting on time), **group leakage** (the same entity on both sides; fix by splitting on entity). Mechanical version: fit scaling/imputation on the whole dataset instead of train-only — split first, fit on train, apply to the rest.
- **Class imbalance** — one class far rarer than another; makes accuracy misleading.
- **Distribution shift** — production data drifts from training data; quality decays.

**Learning machinery**
- **Parameters / weights** — the learned numbers inside a model.
- **Hyperparameters** — settings you choose (learning rate, model size); not learned.
- **Loss function** — single number measuring wrongness; training minimizes it. (MSE for regression, cross-entropy for classification.)
- **Gradient descent** — iteratively step parameters downhill on the loss.
- **Learning rate** — gradient-descent step size.
- **Epoch** — one full pass over the training data.
- **Overfitting** — memorizes training data, fails on new data (great train, poor test).
- **Underfitting** — too simple to capture the pattern (poor on both).
- **Generalization** — performing well on unseen data (the real goal).
- **Bias–variance tradeoff** — too simple (bias/underfit) vs too sensitive (variance/overfit).
- **Regularization** — penalize complexity to reduce overfitting.

**Classic models**
- **Linear regression** — weighted sum → a number.
- **Logistic regression** — weighted sum → a probability (classification baseline).
- **Decision tree** — flowchart of yes/no splits.
- **Random forest** — many trees averaged (robust default).
- **Gradient boosting (XGBoost/LightGBM)** — sequential trees fixing prior errors; usually best on tabular data.
- **Ensemble** — combine many models so errors cancel.
- **kNN** — predict from the k most similar stored examples.

**Evaluation**
- **Accuracy** — fraction correct; misleading under imbalance.
- **Confusion matrix** — TP / TN / FP / FN.
- **Precision** — of flagged positives, how many were right (`TP/(TP+FP)`).
- **Recall** — of actual positives, how many caught (`TP/(TP+FN)`).
- **F1** — harmonic mean of precision and recall.
- **Threshold** — cutoff turning a probability into yes/no; slides the precision/recall tradeoff.
- **ROC / AUC** — threshold-independent ranking quality (0.5 = random, 1.0 = perfect).
- **MAE / RMSE / R²** — regression error metrics (RMSE punishes big misses; R² = variance explained).
- **Cross-validation** — rotate which fold is the test set for a stable estimate.

**Deep learning**
- **Neuron / perceptron** — weighted sum + activation.
- **Activation function** — non-linearity (ReLU, sigmoid) that gives networks their power.
- **Layer / hidden layer** — neurons stacked; depth = "deep."
- **Backpropagation** — assign error-blame to each weight; enables gradient descent across layers.
- **CNN** — convolutional net, workhorse for images.
- **RNN / LSTM** — older sequence models; sequential and forgetful.
- **GPU** — parallel hardware that made deep learning feasible.

**Embeddings & Transformers**
- **Embedding** — a vector capturing meaning; similar things → nearby vectors.
- **Embedding space** — high-dimensional space where location/direction = meaning.
- **Cosine similarity** — angle-based similarity score (−1 to 1).
- **Semantic search** — match by meaning via embeddings (vs keyword match).
- **Hybrid search** — combine keyword + semantic.
- **BM25** — classic keyword ranking: term frequency × inverse document frequency, length-normalized; strong at exact/rare terms.
- **RRF (Reciprocal Rank Fusion)** — merge multiple ranked lists by summing `1/(k+rank)`; the standard way to fuse hybrid-search results.
- **Reranking** — second-stage rescoring of the retrieved top-k for higher precision.
- **Cross-encoder** — reads query + document together for an accurate relevance score; the usual reranker (vs a bi-encoder that embeds each separately).
- **Vector database** — fast nearest-neighbor store over millions of vectors (ANN).
- **Attention** — each token looks at every other token to decide relevance.
- **Transformer** — attention + feed-forward blocks; the architecture behind modern AI.

**LLMs & GenAI**
- **Token** — a chunk of text (~¾ word); billing and context are measured in tokens.
- **Autoregressive** — generate one token at a time, feeding output back in.
- **Hallucination** — confident, fluent, false output; inherent to next-token prediction.
- **Pretraining** — learn language/facts via next-token prediction on massive text.
- **Fine-tuning** — further training to follow instructions / a behavior / a style.
- **RLHF** — tune via human preference ranking to make it helpful and aligned.
- **Context window** — max tokens the model considers at once; its working memory.
- **Knowledge cutoff** — the date the training data stops.
- **Temperature** — randomness in token selection (low = focused, high = creative).
- **Base model** — pretrained but not yet instruction-tuned.
- **Reasoning model / test-time compute** — a model trained to generate an internal chain of thought before answering; spends more compute at *inference* for better results on hard reasoning, at higher latency and cost.

**Applied GenAI**
- **System / user prompt** — developer rules vs end-user request; a security boundary.
- **Zero-shot / few-shot** — no examples vs a few examples in the prompt.
- **Chain-of-thought** — "think step by step"; reasoning by generating intermediate steps.
- **Structured output** — constrain to JSON/schema for parseable results.
- **Prompt injection** — malicious instructions hidden in input/data hijack the model.
- **Indirect prompt injection** — the payload rides in on *retrieved* content (RAG) or a tool result, so an innocent user triggers an attacker's planted instruction.
- **Jailbreaking** — social tricks (role-play, hypotheticals, obfuscation) that talk the model past its safety training.
- **Same-channel problem** — instructions and data share one text stream, so any text the model reads can act as a command; the root cause of injection.
- **Red-teaming** — attacking your own system on purpose to find holes before real attackers do; an adversarial eval set, run on every change.
- **Least privilege** — give an agent the minimum tool permissions it needs, so an injection that reaches a tool can't cause damage.
- **Data poisoning** — corrupting training data or a RAG knowledge base to alter later behavior.
- **RAG** — retrieve relevant data, then generate grounded in it.
- **Chunking** — splitting documents into retrievable passages.
- **Grounding** — basing answers on retrieved evidence; enables citations.
- **Function / tool calling** — model emits a structured request; your code runs it.
- **Agent** — LLM that loops: reason, act with a tool, observe, repeat (ReAct).
- **Guardrails** — input/output checks wrapping the model.
- **LLM-as-judge** — use an LLM to grade outputs against a rubric.
- **Eval set** — curated test cases to measure quality and catch regressions.
- **Semantic caching** — cache answers for *similar* (not just identical) queries.
- **Prompt caching** — provider discount for reusing a static prompt prefix across calls.
- **Routing / cascading** — send each request to the right-sized model; try cheap first, escalate hard cases to the expensive model.
- **Right-sizing** — matching model size to task difficulty instead of using one big model for everything; the biggest cost lever.
- **Cost-per-request** — input tokens × input rate + output tokens × output rate, plus any separately billed work; estimate before optimizing.
- **LLMOps** — logging, monitoring, versioning, and maintaining LLM systems.
- **MLOps** — operating models you *train and deploy*: data/training pipelines, versioning, serving, drift monitoring, retraining.
- **AIOps** — a *different axis*: using AI/ML to run IT operations (anomaly detection, log analysis, incident automation); not about shipping an AI feature.
- **MCP (Model Context Protocol)** — emerging standard for connecting models to tools/data.
- **A2A (Agent-to-Agent) protocol** — an interoperability boundary for agents exchanging tasks and status; distinct from a model application's connection to tools.
- **Workflow** — a code-owned sequence of states/transitions; models can perform steps without choosing the whole path.
- **Bounded autonomy** — agent discretion constrained by explicit budgets for steps, time, cost, tools, and permissions.
- **Durable execution** — persisting workflow state/checkpoints so work can resume safely after waits, crashes, or retries.
- **Idempotency key** — stable logical-operation identifier the receiving service enforces to deduplicate retries; a local key alone does not prevent duplicate remote effects.
- **Trace eval** — grading the path a system took (tool choice, arguments, order, authorization, retries), not only its final answer.
- **Judge calibration** — comparing an LLM judge with rubric-anchored human ratings and inspecting disagreements before using it as a gate.

**Context, memory & workflow reliability**
- **Context engineering** — selecting, structuring, attributing, and budgeting the minimum authorized evidence a model needs for one decision.
- **Context packet / manifest** — typed, versioned record of instructions, workflow state, retrieved evidence, tool results, provenance, and trust levels sent to a model call.
- **Working memory** — temporary state assembled into the current context; it disappears unless the application persists it.
- **Procedural memory** — reusable procedures or skills; distinct from the persisted status of a particular workflow.
- **Episodic memory** — durable record of prior events, decisions, actions, and receipts.
- **Semantic memory** — durable facts/preferences, stored with provenance, scope, freshness, and correction/deletion rules.
- **Procedural state** — current workflow step, pending approvals, retries, deadlines, and allowed transitions.
- **Compaction** — replacing older detail with a smaller derived summary; must preserve invariants and retain a path to source events.
- **Invariant** — constraint or open commitment that compaction may not paraphrase away (approval, denial, correction, safety rule).
- **Provenance** — where a context item came from, with source/version/time/scope so authority and freshness can be checked.
- **Context recall / precision** — whether all required facts were included / whether included material was relevant.

**Multimodal**
- **Multimodal model** — a model that takes and/or produces more than one modality (text, image, audio, video).
- **Shared embedding space / CLIP** — images and text mapped into one vector space so meaning is comparable *across* modalities; makes cross-modal search a nearest-neighbor lookup.
- **Vision-language model (VLM)** — an LLM that also accepts images: patches become vectors fed alongside text tokens.
- **ASR (automatic speech recognition)** — speech → text; powers closed captions and transcripts.
- **TTS (text-to-speech)** — text → natural-sounding audio.
- **Diffusion** — image/video generation by starting from noise and repeatedly denoising toward a prompt.
- **VLM-as-judge** — using a vision-language model to grade multimodal outputs; the multimodal cousin of LLM-as-judge.

---

## B. The roles map at a glance

| Role | Builds | Core skills | This book's core chapters |
|---|---|---|---|
| **AI / GenAI Engineer** | Apps on top of models (RAG, agents, LLM features) | Software eng + applied LLM (prompting, RAG, tools, evals, shipping, context/workflows) | Part 3 (9–17) + Ch 19 + Part 1 concepts |
| **ML Engineer (MLE)** | Models trained & deployed to production | Software eng + ML depth + MLOps | Parts 1–2 + Ch 14 |
| **Data Scientist** | Insight, experiments, classic models | Stats, A/B testing, analysis, communication | Parts 1, Ch 5 |
| **MLOps / Platform** | Infra to train/deploy/monitor/scale | Software/infra, observability, LLMOps | Ch 13–14 |
| **Research Scientist** | New models & methods | Deep math, usually PhD, publishing | Parts 1–2 deeply |

**Natural application-layer path for a working software engineer:** AI Engineer — it builds on software engineering while adding Part 3 and Chapter 19's context/workflow discipline. Read responsibilities, not titles; they vary by company.

---

## C. Tools landscape (concepts, not endorsements — and fast-moving)

Know the *category* each tool fills; specific products churn.

- **Model providers / APIs:** OpenAI, Anthropic, Google, plus open-weight models (Llama, Mistral, Qwen) you can self-host.
- **Frameworks / orchestration:** LangChain, LlamaIndex (RAG and agent plumbing); use judiciously — they help and can also over-abstract.
- **Vector databases:** Pinecone, Weaviate, Chroma, Qdrant, pgvector, FAISS.
- **Classic ML:** scikit-learn (the classic toolbox), XGBoost / LightGBM (boosting), pandas/numpy (data).
- **Deep learning:** PyTorch, TensorFlow; Hugging Face (models, datasets, the `transformers` library).
- **Evaluation / observability:** eval frameworks and LLM-tracing/observability tools (the space is young and shifting).
- **Standards:** MCP for tool/data connectivity; A2A-style protocols for agent-to-agent task exchange. These solve interoperability, not authorization.

> Don't memorize this list for an interview. Know what each *category* is for, and have used one or two yourself.

---

## D. Build these to prove your skills

Hands-on projects beat any amount of reading, and they're what make a résumé credible for AI roles. Roughly in order:

1. **A classic ML model end to end** — take a tabular dataset, split it properly, train logistic regression *and* gradient boosting, evaluate with the right metric, and write up why. Proves Parts 1 fundamentals and the data-first discipline.
2. **A semantic search engine** — embed a set of documents, store the vectors, and answer queries by nearest-neighbor. Proves embeddings (Ch 7).
3. **A RAG chatbot over your own docs** — the single most valuable project: chunk → embed → store → retrieve → grounded generation with citations. Proves Ch 11 and most of Part 3. *If you build one thing, build this.*
4. **A small agent** — an LLM that uses 2–3 tools in a ReAct loop to complete a task, with step limits and guardrails. Proves Ch 12.
5. **An eval harness** — add an eval set and calibrated LLM-as-judge to any of the above and measure a prompt change before/after. Proves Ch 13 and gives you a concrete reliability tradeoff to discuss.
6. **A durable assistant workflow** — add typed context packets, scoped memory writes, checkpoint/resume, version-bound approvals, and an idempotent side effect. Inject a crash after every step and prove no action duplicates. Proves Ch 19.

Ship them somewhere public (GitHub + a short write-up of the *decisions* and *tradeoffs*). The write-up matters as much as the code — it shows judgment.

---

## E. Interview question bank

**Concept checks (be able to explain simply)**
- What is machine learning, and when would you *not* use it?
- Explain overfitting vs underfitting, and the bias–variance tradeoff.
- Why split data into train/validation/test? What is data leakage?
- Name the four ways data leakage sneaks in, and the one-line fix for each. Why does leakage usually show up as *suspiciously high* accuracy?
- Precision vs recall — when does each matter more? Why can accuracy mislead?
- What is an embedding? Why is it the foundation of semantic search?
- Explain attention / the Transformer at a high level.
- What is an LLM really doing? Why does it hallucinate?
- Pretraining vs fine-tuning vs RLHF.
- RAG vs fine-tuning — when each?
- Your RAG system retrieves the wrong chunks — how do you improve retrieval? *(BM25 + hybrid/RRF, reranking with a cross-encoder)*
- What is prompt injection, and how do you defend against it?
- Why can't prompt injection be fixed the way SQL injection can? *(the same-channel problem)*
- What is *indirect* prompt injection, and why does RAG make it possible?
- How would you red-team an LLM feature before shipping it?
- Why is an agent that can take actions held to a higher security bar than a chatbot?
- What is a reasoning model / test-time compute, and when would you use one instead of a standard model?
- MLOps vs LLMOps vs AIOps — how do they differ, and which one is *not* about operating the AI you built?
- How does multimodal AI extend the embeddings idea? *(a shared image–text space turns cross-modal matching into nearest-neighbor search)*
- Long context vs RAG vs a structured tool — how do you choose?
- Workflow vs agent — when is model-chosen control flow worth the reliability cost?
- MCP vs A2A — which boundary does each standardize, and what security work remains?
- Context vs memory — why is resending a transcript not a durable memory design?
- What belongs in a memory write policy? How do scope, provenance, expiry, correction, and deletion work?
- Why do side-effecting tools need idempotency keys and durable receipts?
- How do you evaluate an agent trace and calibrate an LLM judge?
- Quantization vs distillation — what resource cost does each target, and how do you measure quality and escalation rate?
- A real-time voice assistant acts on a partial transcript. What commit, cancellation, and approval rules would prevent a mistaken action?

**ML / AI system design (use DRESS)**
- Design a system to answer questions over our internal documents. *(RAG)*
- Design a product recommendation system.
- Design a fraud / spam detection system.
- How would you reduce hallucination in a customer-facing assistant?
- Design a reliable agent that can take actions on our systems.
- How would you evaluate this LLM feature? *(the one candidates fumble most)*
- This AI feature is too slow / too expensive — how do you fix it?
- Our LLM bill is 5× budget — how do you cut it without wrecking quality? *(estimate cost-per-request, right-size, route, cache, trim tokens)*
- A teammate wants to use the smallest model everywhere to save money — what's your response?
- Design an AI feature that picks the best thumbnail for a video (or auto-generates closed captions). *(multimodal: shared embeddings / VLM / ASR, plus the usual eval + cost discipline)*
- Design a long-running assistant that survives a crash, waits for approval, remembers a corrected preference, and never sends the same message twice.
- A conversation no longer fits in context. Design compaction that preserves active constraints and can retrieve raw history when needed.

**Judgment & responsibility**
- When would you choose *not* to use AI for a problem?
- How do you handle bias / privacy / safety in an AI system?
- The field changes monthly — how do you stay current?
- Walk me through an AI/ML project you built — decisions and tradeoffs. *(Use STAR from the Behavioural track.)*

**The DRESS ritual (memorize)**
**D**ata first → **R**ule out over-engineering / right-size → **E**stimate the approach (prompt→RAG→fine-tune) → **S**hip it (latency, cost, reliability, security) → **S**core it (metrics, evals, monitoring).

---

## F. The six bumper stickers (the whole track, compressed)

1. **Ch 1:** ML learns a function from examples instead of you writing it — use it only when the rule is too messy to code, you have data, and you can tolerate being wrong.
2. **Ch 5:** A single accuracy number hides which mistakes a model makes — pick the metric that matches what being wrong actually costs.
3. **Ch 7:** Embeddings turn meaning into geometry: embed, then search — that one move powers semantic search, recommendations, and RAG.
4. **Ch 9:** An LLM just predicts the next token — fluent but with no built-in truth, memory, or fresh knowledge; every technique manages those limits.
5. **Ch 18:** DRESS every problem — Data, Rule-out, Estimate, Ship, Score — master durable concepts over churning tools, and the field becomes yours to build in.
6. **Ch 19:** The model needs the smallest authorized packet of current evidence, not every token — store memory with a write policy and run actions in checkpointed, idempotent workflows.

> The whole track in one line: **Machine learning is learning a function from data instead of writing it by hand — so the data, not the model, is the real lever. Feel the data before reaching for the model, and an LLM stops being magic and becomes a component you can engineer.**
