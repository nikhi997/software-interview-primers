# Chapter 9: FastAPI (the Python web framework)

*[← Chapter 8](interview-topics-chapter-8.md) · [Contents](interview-topics-README.md)*

- [ ] **Mark as read**

If your background is Python services rather than Java, **FastAPI** is your headline framework —
the Python parallel to Spring Boot (Chapter 2). And the good news is the same as it was there:
under the decorators, FastAPI is two ideas you already know. It's an **async web framework**
([HLD](../HLD/hld-README.md) concurrency) where **type hints drive validation** (Pydantic) and a
**container hands you your dependencies** (`Depends` — the same dependency injection as Spring).
Name those and the framework stops being magic.

The principle, again: **feel the concept beneath the brand name.** `Depends(...)` is just
"someone hands me my dependencies instead of me constructing them" — dependency inversion from
[LLD](../LLD/lld-README.md), Python flavour. A Pydantic model is just a validated, parsed struct
whose schema *is* the type hint. Once those click, the rest is knowing which piece does what and
where the one big gotcha hides.

---

## The concept under FastAPI

> 💡 **Concept notes — what FastAPI actually is**
> Three things bolted together: **(1)** an **ASGI** async web framework (served by **Uvicorn**),
> **(2)** **Pydantic** for request/response validation and settings, **(3)** a **dependency
> injection** system (`Depends`). It builds on **Starlette** (the ASGI toolkit: routing,
> middleware, requests/responses) and adds the typing + validation + DI + automatic OpenAPI docs.
> The Java parallel is exact: Uvicorn ≈ the embedded server, Pydantic ≈ bean validation,
> `Depends` ≈ `@Autowired`, the auto docs ≈ Springdoc. That mapping *is* your honest pivot if
> FastAPI is the gap and Spring is your reality (or vice-versa).

---

## Async and the event loop: the one gotcha that matters

> 💡 **Concept notes — ASGI vs WSGI, and why it's async**
> Old Python web (WSGI: Flask, Django) is **synchronous** — one request blocks a worker until it
> finishes. **ASGI** lets a single worker handle many requests concurrently by `await`ing on I/O
> (DB, HTTP, disk) and doing other work while it waits. For I/O-bound services (which most web
> services are) that's a big throughput win on one process. Underlying concept: cooperative
> concurrency on an event loop ([Foundations Ch 5](../Foundations/2-operating-systems/ch5-os.md)).

> 💡 **Concept notes — the blocking-call trap (the #1 FastAPI question)**
> The event loop runs on **one thread**. If you make a **blocking** call inside an `async def`
> route — a synchronous DB/HTTP client, `time.sleep`, heavy CPU — you **block the entire loop**
> and every concurrent request stalls. Two fixes: use an **async library** (`httpx`, async Mongo
> driver) so you can `await` it, or push the blocking call to a **threadpool**
> (`await run_in_executor(...)`, or just define the route as plain `def` and FastAPI runs it in a
> threadpool for you). This is the single most-asked FastAPI gotcha, and it's a real production
> failure mode — a synchronous SDK called from an async route silently caps your throughput.

> 💡 **Concept notes — async ≠ parallel**
> `async` gives **concurrency for I/O waits**, not CPU parallelism — it's still one thread. For
> CPU-bound work you still need processes/workers (Gunicorn with multiple Uvicorn workers) or a
> task queue. "async makes it faster" is only true for I/O-bound work; say that precisely.

---

## Pydantic: the type hints *are* the schema

> 💡 **Concept notes — validation, parsing, settings**
> A **Pydantic model** is a class of typed fields; FastAPI uses it to **parse and validate** the
> request body (bad input → an automatic 422) and to **serialize** the response. The type hint on
> the parameter is the contract — no separate schema file. `BaseSettings` (pydantic-settings) does
> the same for **config**: env vars → a typed settings object, per-environment. Know **v1 vs v2**:
> v2 is a near-rewrite (Rust core, faster), with renames like `.model_dump()` /
> `model_config` — a common "which version?" follow-up.

---

## Dependency injection with `Depends`

> 💡 **Concept notes — Depends is dependency inversion**
> A dependency is any callable; put `param = Depends(get_thing)` in a route and FastAPI **calls it
> and injects the result**. Use it for auth (`Depends(get_current_user)`), a DB session, a
> validated payload, pagination — anything shared. **`yield` dependencies** run setup before the
> route and teardown after (open/close a session), like a `try/finally`. Dependencies **nest and
> cache** within a request. This is exactly Spring's DI concept: the framework constructs and hands
> you your collaborators, which keeps routes thin and testable.

---

## The app: factory, lifespan, background work

> 💡 **Concept notes — app factory + lifespan**
> An **app factory** (`create_application()` returning a `FastAPI`) keeps startup explicit and
> **testable** (no import-time side effects). The **`lifespan`** async context manager runs
> **startup and shutdown** — the place to open/close client pools (DB, cache, HTTP), and to
> **fail fast** if a dependency is unreachable. (This replaced the older `@app.on_event`
> startup/shutdown hooks.)

> 💡 **Concept notes — BackgroundTasks vs a real queue**
> `BackgroundTasks` runs work **after** the response is sent — good for fire-and-forget side
> effects (send an email, warm a cache). But it runs **in the same process**, so it's lost on a
> crash and doesn't survive a deploy. When the work must be durable, retried, or scaled
> independently, reach for a **task queue** (Celery, or a Pub/Sub-triggered worker) — not
> `BackgroundTasks`. Knowing that boundary is the senior answer.

---

## Errors, middleware, serving

> 💡 **Concept notes — consistent errors and cross-cutting concerns**
> Don't `try/except` in every route. Register **exception handlers** to map exceptions to a
> **consistent error body** with the right status (422 validation, 404, 409, 500) and no leaked
> stack traces — the same discipline as Spring's `@ControllerAdvice`. **Middleware** wraps every
> request for cross-cutting work (correlation IDs, timing, CORS). This is the professional answer
> to "how do you handle errors and cross-cutting concerns?"

> 💡 **Concept notes — testing and running it**
> Test with the `TestClient` (httpx under the hood) — no server needed; override dependencies with
> `app.dependency_overrides` to inject fakes (DI paying off again). In production you run
> **Uvicorn** (ASGI) directly, or **Gunicorn managing multiple Uvicorn workers** for CPU
> parallelism across cores; containerized on Cloud Run / K8s. "One worker is concurrent for I/O;
> multiple workers give you cores" is the crisp way to say it.

---

## Try it

Answer aloud:

1. What *is* FastAPI in one sentence, and what are the three pieces it bolts together?
2. You put a synchronous database call in an `async def` route. What happens under load, and what
   are the two fixes?
3. Is `async` the same as parallel? When does it actually make a service faster?
4. What does `Depends` do, and what concept from the other tracks is it?
5. `BackgroundTasks` vs a task queue — when is `BackgroundTasks` the wrong choice?
6. What does the `lifespan` context manager do, and why an app factory?
7. Give your honest-pivot answer for "we use Spring/Java, your background is FastAPI/Python" (or
   the reverse).

*Write your answers in [interview-topics-chapter-9-tryit.md](code/interview-topics-chapter-9-tryit.md).*

## The bumper sticker

> *FastAPI is an ASGI async framework where Pydantic validates by type hint and `Depends` is
> dependency injection — the Python Spring Boot. Learn the one real gotcha (a blocking call in an
> async route stalls the whole event loop), know that async buys I/O concurrency not CPU
> parallelism, and the rest is naming the concept beneath each decorator.*

Next: getting that application into production safely. Chapter 10 maps containers, Kubernetes,
CI/CD, IaC, secrets, OpenTelemetry, rollout, and incident response to the portable operational
concepts beneath their brand names.

---

<div align="right">

[Chapter 10 →](interview-topics-chapter-10.md)

</div>
