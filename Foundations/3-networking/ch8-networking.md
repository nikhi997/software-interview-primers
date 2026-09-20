# Chapter 8: What happens when you type a URL and hit enter

*[← Chapter 7](ch7-networking.md) · [Contents](../foundations-README.md)*

- [ ] **Mark as read**

This is the single most famous systems interview question — so famous it has its own Wikipedia-length canonical answers. But its real value isn't trivia; it's that one question threads together *everything* in this track: DNS, TCP, TLS, HTTP, load balancers, caches, and databases, all in one journey. If you can narrate this story end to end, you've demonstrated that you understand how the whole machine fits together. This chapter is that narration. The mechanism to feel: a single request is a relay race, each component doing one job and handing off to the next.

---

## The journey, step by step

You type `https://shop.example.com/products/42` and press Enter. Here's the relay, baton by baton.

### 1. URL parsing
The browser breaks the URL into pieces: the **scheme** (`https`), the **host** (`shop.example.com`), the **path** (`/products/42`). The scheme tells it to use HTTPS (HTTP + TLS, port 443 by default).

### 2. DNS resolution — name to address
The browser needs the server's IP. It checks caches first (browser cache → OS cache → router), and if not found, asks a **DNS resolver**, which walks the hierarchy (root → `.com` → `example.com`'s authoritative server) and returns the IP. (Chapter 7.) Now the browser knows *where* to send the request.

> 💡 **Concept notes — why so many caches**
> Notice the request hasn't even left your machine yet and we've already hit multiple cache layers. **Caching** — storing a result so you don't recompute or re-fetch it — appears at *every* layer of this journey (DNS, browser, CDN, server, database). It's the single most important performance technique in all of computing. Watch for it as the story unfolds.

### 3. TCP connection — the handshake
The browser opens a **TCP connection** to that IP via the three-way handshake (SYN, SYN-ACK, ACK). (Chapter 7.) Now there's a reliable pipe.

### 4. TLS handshake — securing the pipe
Because it's HTTPS, a **TLS handshake** follows: the server presents its **certificate** (proving it's really `shop.example.com`), and the two sides establish a shared encryption key. (Chapter 7.) Now the pipe is encrypted.

### 5. The HTTP request goes out
The browser sends an **HTTP request** over the secure connection: `GET /products/42`, plus headers (cookies for your session, accepted formats, etc.). (Chapter 7.)

### 6. It hits the edge: CDN and load balancer
The request usually doesn't reach the application server directly. Two things often sit in front:

> 💡 **Concept notes — CDN and load balancer**
> - A **CDN (Content Delivery Network)** is a network of servers distributed geographically that cache static content (images, CSS, JS) close to users. If `/products/42`'s page image is cached at a CDN node near you, it's served from there in milliseconds — never touching the origin. CDNs cut latency (data travels less distance) and offload the origin.
> - A **load balancer** sits in front of multiple identical application servers and distributes incoming requests among them (round-robin, least-connections, etc.). It's how a service handles more traffic than one machine can (horizontal scaling) and how it survives a server dying (the balancer routes around it). Your request lands on *whichever* server the balancer picks.

### 7. The application server processes it
A web/app server receives the request, routes it to the code for "get product 42," and runs your application logic — authentication, business rules, and fetching data.

> 💡 **Concept notes — the security checks the app actually runs**
> Two words get confused constantly, so separate them: **authentication** is *who are you?* (verifying identity — checking the cookie/token from step 6, or a password at login), and **authorization** is *what are you allowed to do?* (can *this* user delete *that* product). You authenticate once, then authorize every action. A second must-know: **never store passwords as plaintext.** You store a **hash** — a one-way function (bcrypt, scrypt, argon2) — plus a per-user random **salt** so two users with the same password get different hashes and precomputed "rainbow table" attacks fail. At login you hash the submitted password and compare. Third, the app is where the classic **OWASP** web vulnerabilities are defended: **SQL injection** (never build queries by string-concatenating user input — use parameterized queries, Chapter 1) and **XSS / cross-site scripting** (escape user-supplied content before rendering it as HTML, so a comment can't smuggle in `<script>`). TLS (step 4) secured the *pipe*; these checks secure the *application* — both layers are needed, and interviewers probe the difference.

> 💡 **Concept notes — OWASP Top 10, the rest of the list**
> SQLi and XSS are two famous entries, but they live on a bigger checklist: the **OWASP Top 10**, the industry's consensus list of the most common web-app security risks. You don't memorize it cold — you recognize the shape of each so you don't *build* one by accident. The ones worth naming: **Broken access control** (the #1 risk — the app authenticates you but forgets to *authorize*, so changing an `id` in the URL shows someone else's order); **Cryptographic failures** (sensitive data sent or stored without encryption — the reason for TLS and password hashing above); **Injection** (SQLi and friends — untrusted input interpreted as a command); **Security misconfiguration** (default passwords, verbose error pages, an open admin panel); **CSRF / cross-site request forgery** (another site tricks your logged-in browser into firing a state-changing request — defended with anti-CSRF tokens and `SameSite` cookies); and **SSRF / server-side request forgery** (tricking *your server* into fetching an internal URL it shouldn't). The meta-lesson is the same one as authN/authZ: **never trust input, and check permission on every action** — most of the list collapses into those two habits.



### 8. Cache and database
To get product 42's data, the server typically checks a **cache** first, then the **database**:

> 💡 **Concept notes — the cache-then-database pattern**
> The server often checks a fast in-memory cache (like Redis) for "product 42" before querying the database. **Cache hit** → return instantly. **Cache miss** → query the database (which uses an *index* on the product id to find the row fast — Chapter 3), then store the result in the cache for next time. This "cache-aside" pattern spares the database from repeated identical reads. This is the same caching principle from step 2, now protecting the most expensive resource in the system — the database.

### 9. The response travels back
The server builds an **HTTP response** — a status code (200 OK), headers, and a body (the HTML/JSON for product 42). It travels back over the same encrypted TCP connection, through the load balancer, to the browser.

### 10. The browser renders
The browser parses the returned HTML, discovers it needs more resources (CSS, JS, images), and fires off *more* requests for them (often served by the CDN), then paints the page. What felt like one action was dozens of coordinated requests.

---

## Why this question is loved

> 💡 **Concept notes — what the interviewer is really checking**
> No one expects every micro-detail. The question is a **breadth probe**: can you move smoothly across layers — naming DNS, TCP/TLS, HTTP, the load balancer, cache, and database, and *why each exists* — without getting stuck or hand-waving? The strongest answers also surface the recurring themes: **caching at every layer**, **horizontal scaling via load balancers**, and **indexes at the database**. You can pitch the answer at any depth; what's tested is the *coherent end-to-end mental model*. That's why it's the perfect capstone for this track.

---

## A note on statelessness and sessions

One thread worth pulling: HTTP is **stateless** (Chapter 7), so how does the server know *you're* logged in across requests?

> 💡 **Concept notes — cookies, sessions, tokens**
> Because each HTTP request is independent, identity is carried *in* the request. After you log in, the server gives the browser a **cookie** (a small stored value) or a **token** (like a JWT). The browser sends it with every subsequent request, so the server can recognize you without re-authenticating. A **session** is the server-side notion of "this user's current logged-in state," keyed by that cookie/token. This is how a stateless protocol supports staying logged in — a common follow-up to the URL question.

> 💡 **Concept notes — OAuth: logging in *as you* without your password**
> The pain: you want a third-party app (say a calendar tool) to read your Google contacts. Handing it your Google *password* would be reckless — it could do anything, forever, and you'd have to change your password to revoke it. **OAuth 2.0** is the protocol that fixes exactly this: **delegated authorization** — granting one app *scoped, revocable* access to your data on another, without sharing your credentials. The mechanism in one breath: you're redirected to Google, you log in *there* and consent to specific **scopes** ("read contacts"), Google hands the app a short-lived **authorization code**, the app exchanges that code (server-to-server, with its own secret) for an **access token**, and it then calls Google's API with that token. The token is *narrow* (only the scopes you approved), *expiring* (a **refresh token** quietly gets new ones), and *revocable* (kill it without touching your password). This is also what's under "Sign in with Google" buttons — though strictly, identity sign-in adds **OpenID Connect**, a thin layer on top of OAuth. The one-line answer: *OAuth lets you grant limited, revocable access to your data without giving away your password.*

---

## Try it

1. Narrate the full journey from typing a URL to seeing the page, naming at least seven distinct steps/components.
2. At how many points in the journey does caching appear? List them.
3. What does a load balancer do, and what two problems does it solve (scaling and failure)?
4. Explain the cache-then-database pattern for fetching product data, including what happens on a hit vs a miss.
5. HTTP is stateless, yet you stay logged in across pages. How? Explain cookies/tokens and sessions.
6. Authentication vs authorization — define each and give an example of where the app enforces each one.
7. How should a service store user passwords, and why hash with a per-user salt rather than encrypt or store plaintext?
8. A third-party app wants to read your Google contacts. Why is OAuth a better answer than giving it your password? Name what makes the access token safe (scoped, expiring, revocable).
9. Beyond SQL injection and XSS, name three other OWASP Top 10 risks and the one-line defense for each. Which single risk is currently #1, and which two habits prevent most of the list?
10. An interviewer asks this question and you have only 90 seconds. What's your skeleton answer — the must-hit beats?

*Write your answers in [ch8-networking-tryit.md](../code/ch8-networking-tryit.md).*

---

## The bumper sticker

> *Typing a URL kicks off a relay: DNS finds the address, TCP and TLS open a secure pipe, HTTP carries the request through a load balancer to a server, which checks a cache before the indexed database, then the response races back. Every layer caches, and naming each handoff is how you prove you see the whole machine.*

That closes networking. Next: the modern concurrency patterns sitting on top of all this — async/await, event loops, and why "I/O-bound vs CPU-bound" decides everything.

---

<div align="right">

[Chapter 9 →](../4-putting-it-together/ch9-concurrency.md)

</div>
