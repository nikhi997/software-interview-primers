# Chapter 2: Spring Boot

*[← Chapter 1](interview-topics-chapter-1.md) · [Contents](interview-topics-README.md)*

- [ ] **Mark as read**

For most Java backend roles, "Spring Boot" is the **headline skill** — the interviewer will spend real time here, and they'll dig. The good news: under all the annotations, Spring is one idea you already met in [LLD](../LLD/lld-README.md). It's **dependency injection** — the dependency-inversion principle, automated — with a pile of conveniences bolted on. Name that concept and the framework stops being magic.

The principle for the chapter: **feel the concept beneath the brand name.** `@Autowired` is just "someone hands me my dependencies instead of me constructing them." Once that clicks, the rest is knowing which annotation does what and where the famous gotchas hide.

---

## Dependency injection: the concept under the annotations

> 💡 **Concept notes — IoC and the container**
> **Inversion of Control:** instead of a class constructing its own dependencies, a **container** creates them and hands them in. Spring's container scans for beans — classes marked `@Component` (or the stereotypes `@Service`, `@Repository`, `@Configuration`) — instantiates them, and **wires** them together. That's dependency inversion ([LLD](../LLD/lld-README.md)) done for you at startup.

> 💡 **Concept notes — why constructor injection wins**
> Three ways to inject: constructor, setter, field. Prefer **constructor injection** because:
> - Dependencies are **explicit and required** — you can't construct the object without them.
> - Fields can be **`final`** (immutable).
> - The class is **testable without Spring** — just `new` it with mocks, no container needed.
> - **Circular dependencies fail loudly at startup** instead of hiding.
> Field injection (`@Autowired` on a field) hides dependencies and can't be `final` — know this; "constructor vs field injection" is a near-guaranteed question.

---

## REST: turning a class into an API

> 💡 **Concept notes — the REST annotations**
> - `@RestController` marks a class as an HTTP API; `@GetMapping`/`@PostMapping`/etc. map methods to routes.
> - Bind input with `@RequestBody` (JSON body), `@PathVariable` (`/users/{id}`), `@RequestParam` (`?q=`).
> - Return `ResponseEntity` to control status code and headers.
> - Validate input with `@Valid` + bean-validation annotations.

> 💡 **Concept notes — centralized error handling**
> Don't `try/catch` in every controller. Use `@ControllerAdvice` + `@ExceptionHandler` to map exceptions to a **consistent error response** with the right status code — 400 validation, 404 not found, 409 conflict, 500 unexpected — a stable error body shape, and **no leaked stack traces**. This is the professional answer to "how do you handle errors in a REST API?"

---

## Data: JPA, transactions, and the famous traps

> 💡 **Concept notes — what `@Transactional` actually does**
> Spring wraps the method in a **proxy** that begins a transaction, commits on normal return, and rolls back on a **runtime** exception (not checked exceptions, by default — configurable via `rollbackFor`). Three gotchas interviewers love:
> 1. **Self-invocation** — calling a `@Transactional` method from *another method in the same bean* bypasses the proxy, so the annotation does nothing. (The single most-asked Spring gotcha.)
> 2. **Rollback only on unchecked** exceptions unless you set `rollbackFor`.
> 3. **Propagation** (`REQUIRED` vs `REQUIRES_NEW`) matters when transactional methods call each other.

> 💡 **Concept notes — the N+1 problem**
> Lazily loading a collection issues **one query per parent row** (1 + N queries) — a silent performance killer in JPA. Fix it with a **fetch join**, an `@EntityGraph`, or a batch fetch size, so related rows load in one or a few queries. Know lazy vs eager loading and why lazy is the default. (Underlying concept: [Foundations Ch 2](../Foundations/1-sql-and-databases/sql/ch2-sql.md).)

---

## Beans, config, and autoconfiguration: what makes it "Boot"

Plain Spring is the DI container; **Boot** is the conveniences. Interviewers ask what they actually buy you.

> 💡 **Concept notes — scopes, profiles, autoconfiguration**
> - **Bean scopes** — beans are **singletons** by default (one shared instance); `prototype` makes a new one per request. Singletons must be stateless or thread-safe.
> - **`@Qualifier` / `@Primary`** resolve "which bean?" when two implement the same interface.
> - **Profiles + config** — `@Profile("prod")` and `application-{env}.yml` swap behaviour per environment; inject values with `@Value` or `@ConfigurationProperties`. Secrets come from env/vault, never the jar.
> - **Autoconfiguration** is the magic: a starter on the classpath + sensible defaults wires beans for you (see a DB driver → configure a `DataSource`). You override by defining your own bean. "What does Boot add over Spring?" → starters, autoconfig, embedded server, actuator.

> 💡 **Concept notes — security & AOP, at recall depth**
> - **Spring Security** sits in a **filter chain**: authenticate (who are you), then authorize (`@PreAuthorize`/role rules). Stateless APIs use a **JWT** — signed token sent per request, validated without a server session. Sessions for server-rendered apps, JWT for APIs.
> - **AOP** is the mechanism behind `@Transactional` and `@Cacheable`: a proxy wraps your bean to run cross-cutting code (transactions, logging, metrics) around the method. Knowing "AOP = proxies" closes the self-invocation gotcha above.

---

## Testing: the slices

6. What does Spring Boot add over plain Spring? Explain autoconfiguration and bean scopes.
7. How do you secure a REST API — sessions vs JWT — and what is AOP doing under `@Transactional`?
> 💡 **Concept notes — test at the right level**
> - **Unit** — business logic with Mockito, no Spring context (fast).
> - **Slice tests** — `@WebMvcTest` + `MockMvc` for controllers, `@DataJpaTest` for repositories; load only the relevant slice.
> - **`@SpringBootTest`** — full integration when you genuinely need the whole context (slow; use sparingly).

---

## Try it

Answer aloud:

1. Constructor vs field injection — which do you use and *why* (give at least three reasons)?
2. What does `@Transactional` actually do under the hood, and what are the three classic gotchas?
3. A teammate's `@Transactional` method "isn't rolling back" when called from another method in the same class. What's wrong?
4. What is the N+1 problem and how do you fix it?
5. How do you handle errors consistently across a REST API in Spring?

*Write your answers in [interview-topics-chapter-2-tryit.md](code/interview-topics-chapter-2-tryit.md).*

## The bumper sticker

> *Spring Boot is dependency injection with conveniences — name that concept and the annotations stop being magic. Then know the three things interviewers always probe: why constructor injection, what `@Transactional`'s proxy really does (and the self-invocation trap), and how you'd kill an N+1.*

Next: the data layer those services talk to — **PostgreSQL**, the "Have" skill most likely to be exposed as shallow.

---

<div align="right">

[Chapter 3 →](interview-topics-chapter-3.md)

</div>
