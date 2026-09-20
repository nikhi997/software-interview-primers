# Chapter 7: Networking — how machines talk

*[← Chapter 6](../2-operating-systems/ch6-os.md) · [Contents](../foundations-README.md)*

- [ ] **Mark as read**

Every web app, API call, and database connection rides on the network, yet networking is the layer most developers treat as pure magic. Interviewers know this, so "what happens when you type a URL and hit enter?" and "TCP vs UDP?" are perennial questions — they instantly reveal whether you understand the pipes your code runs through. This chapter builds the vocabulary; the next walks a full request end to end. The mechanism to feel: a message between two machines is wrapped in layers, like an envelope inside an envelope, each layer handling one job.

---

## The layered model: envelopes inside envelopes

Networking is built in **layers**, each responsible for one concern and unaware of the others' details. You don't need the full 7-layer OSI model memorized, but the idea matters: your application data gets wrapped by lower layers for transport and unwrapped on the other side.

> 💡 **Concept notes — the layers that matter**
> From the bottom up, the four you'll actually discuss:
> - **IP (network layer):** addressing and routing — getting a packet from machine A to machine B across the internet, identified by **IP addresses** (like `142.250.72.14`). IP is "best effort": it tries, but packets can be lost, duplicated, or arrive out of order.
> - **TCP / UDP (transport layer):** managing the conversation *between programs* on those machines (via **ports**). This is where reliability is added (or not) — see below.
> - **TLS (security layer):** encryption, sitting between transport and application.
> - **HTTP (application layer):** the actual request/response your app speaks.
> Each layer wraps the one above it with its own header — your HTTP request is wrapped in a TLS envelope, in a TCP segment, in an IP packet. The receiver unwraps in reverse. That nesting *is* the architecture of the internet.

---

## TCP vs UDP: reliable conversation vs fast fire-and-forget

The single most common networking interview question. Both carry data between programs, but with opposite priorities.

> 💡 **Concept notes — TCP**
> **TCP (Transmission Control Protocol)** is the **reliable, ordered** transport. It guarantees that bytes arrive, in order, without duplication — retransmitting anything lost and reassembling out-of-order pieces. It's **connection-oriented**: the two sides establish a connection first (the handshake, below). The cost of all this reliability is overhead and latency. Use TCP when *every byte matters*: web pages (HTTP), APIs, file transfers, database connections, email.

> 💡 **Concept notes — UDP**
> **UDP (User Datagram Protocol)** is **fast and connectionless** — it just fires packets off with no guarantee of arrival, order, or deduplication, and no handshake. Less overhead, lower latency, but unreliable. Use UDP when *speed beats completeness* and a lost packet doesn't matter: live video/voice calls (a dropped frame is better than a stalled stream), online gaming, DNS lookups, streaming.
> The crisp contrast: **"TCP is reliable and ordered but slower — use it when every byte matters; UDP is fast and connectionless but unreliable — use it when speed matters more than perfection, like video calls or gaming."** That answer, with one example each, is exactly what's wanted.

---

## The TCP handshake: establishing a connection

Because TCP is connection-oriented, the two machines must first agree to talk. This is the **three-way handshake**, and being able to sketch it is a common follow-up.

> 💡 **Concept notes — the three-way handshake**
> Three messages set up a TCP connection:
> 1. **SYN** — the client says "I want to talk" (synchronize).
> 2. **SYN-ACK** — the server replies "okay, and I want to talk too" (acknowledge + its own synchronize).
> 3. **ACK** — the client confirms "great, let's go."
> Three *messages*, but count the waiting: the client sends SYN and waits for SYN-ACK — that's one round trip — and its final ACK travels alongside or just before the first data. So the takeaway beyond the names is that establishing a TCP connection **costs one round trip** *before any data is sent* — which is why connection reuse (keep-alive) and connection pooling matter for performance, and why this setup latency adds up across many small requests.

---

## HTTP and HTTPS: the language of the web

On top of TCP, the web speaks **HTTP** — the request/response protocol between browsers/clients and servers.

> 💡 **Concept notes — HTTP basics**
> **HTTP (HyperText Transfer Protocol)** is a request/response protocol: the client sends a request (a **method** + path + headers + optional body), the server sends a response (a **status code** + headers + body). Methods you must know: **GET** (read), **POST** (create), **PUT** (replace/update), **DELETE** (remove). Status codes by family: **2xx** success (200 OK), **3xx** redirect (301 moved), **4xx** client error (404 not found, 401 unauthorized, 403 forbidden), **5xx** server error (500 internal, 503 unavailable). HTTP is also **stateless** — each request is independent and the server remembers nothing between them by default, which is why we need cookies/tokens to carry identity (see the next chapter).

> 💡 **Concept notes — HTTPS and the TLS handshake**
> **HTTPS** is just HTTP wrapped in **TLS** (Transport Layer Security) encryption — the *S* is "secure." Without it, anyone between you and the server (on the same Wi-Fi, at an ISP) can read and tamper with the traffic. TLS provides three things: **encryption** (eavesdroppers see gibberish), **integrity** (tampering is detected), and **authentication** (a certificate proves the server is really who it claims, validated by a trusted Certificate Authority). The **TLS handshake** happens after the TCP handshake: the client and server agree on encryption parameters, the server presents its **certificate**, and they establish a shared secret key — using *asymmetric* crypto (public/private keys) to safely set up a fast *symmetric* key for the actual data. The practical point for interviews: HTTPS adds another setup round trip on top of TCP's, and it's why "always use HTTPS" is non-negotiable for anything sensitive.

---

## DNS: turning names into addresses

You type `google.com`, but the network routes by IP address. **DNS** is the translation layer — "the phonebook of the internet."

> 💡 **Concept notes — DNS**
> **DNS (Domain Name System)** translates human-friendly domain names (`google.com`) into the IP addresses machines route by (`142.250.72.14`). When you visit a site, your machine asks a **DNS resolver**, which walks a hierarchy (root servers → top-level-domain servers like `.com` → the domain's authoritative server) to find the IP, then **caches** the answer (with a TTL — time to live) so it doesn't repeat the lookup every time. The mental model: DNS is a distributed, cached phonebook mapping names to numbers. It matters in interviews because it's the *first* step of loading any URL — and a frequent real-world failure point ("it's always DNS," runs the sysadmin joke).

---

## Try it

1. Explain TCP vs UDP, giving one real use case for each and the core tradeoff between them.
2. Sketch the three-way handshake. Why does it matter for performance that it costs a round trip before data flows?
3. List the four main HTTP methods and what each does, plus what the 2xx/4xx/5xx status families mean.
4. What does the "S" in HTTPS add, and what three guarantees does TLS provide?
5. What does DNS do, and why is it the first thing that happens when you load a web page?
6. Why is connection reuse (keep-alive / pooling) a meaningful optimization? Tie your answer to the handshakes.

*Write your answers in [ch7-networking-tryit.md](../code/ch7-networking-tryit.md).*

---

## The bumper sticker

> *Networking is envelopes inside envelopes: your HTTP request rides in TLS, in TCP, in IP. TCP is reliable and ordered for when every byte matters; UDP is fast and loose for when speed wins. HTTPS adds TLS encryption, and DNS is the phonebook that turns names into the addresses machines actually route by.*

Next: put it all together — follow a single request from a browser keystroke all the way to the database and back.

---

<div align="right">

[Chapter 8 →](ch8-networking.md)

</div>
