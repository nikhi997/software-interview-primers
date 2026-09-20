# Chapter 7: Auth (authentication, authorization, and tokens)

*[← Chapter 6](interview-topics-chapter-6.md) · [Contents](interview-topics-README.md)*

- [ ] **Mark as read**

Every application has to answer two questions before it does anything sensitive: *who are you?* and *what are you allowed to do?* A JD names the tools that answer them — "OAuth2," "JWT," "SSO," "Spring Security" — and a design round almost always reaches a moment where the interviewer asks "…and how do you handle auth?" The brands sound like a lot, but underneath they're two ideas and one primitive. The concept beneath the brand here: **a token is just a claim someone can verify without calling you back.**

The principle, again: **feel the concept beneath the brand name.** JWT, session cookie, OAuth access token — they're all "a credential the server can trust." Lead with the two questions and the primitive; the brand is a detail.

---

## The two words people mix up

> 💡 **Concept notes — authentication vs authorization**
> - **Authentication (authn) — *who are you?*** Proving identity: a password, a Google login, a token. The failure is `401 Unauthorized` (you haven't proven who you are). *(The status-code pair from [Chapter 6](interview-topics-chapter-6.md).)*
> - **Authorization (authz) — *what may you do?*** Deciding whether the proven identity is allowed this action. The failure is `403 Forbidden` (we know who you are; you still can't). Usually done with **roles** (RBAC — admin/user) or finer **permissions/scopes**.
> Interviewers listen for you keeping these separate. "Authenticated but not authorized" is a real, common state — a logged-in user hitting an admin endpoint — and 401 vs 403 is the tell that you know the difference.

---

## Sessions vs tokens: the core choice

Once someone logs in, the server needs to remember it on the *next* request (HTTP is stateless — [Foundations Ch 8](../Foundations/3-networking/ch8-networking.md)). There are two ways, and the tradeoff between them is the most common auth interview question.

> 💡 **Concept notes — session cookies vs JWTs**
> - **Server session (stateful):** on login the server creates a session, stores it (memory/Redis/DB), and hands the browser a **cookie** holding an opaque session id. Every request sends the cookie; the server looks the session up. *Pro:* revoking is trivial — delete the session. *Con:* the server must store and look up state, and at scale that store is shared infrastructure (often Redis).
> - **JWT (stateless):** on login the server returns a **signed token** containing claims (user id, roles, expiry). The client sends it on each request; the server *verifies the signature* and trusts the claims — **no lookup**. *Pro:* nothing to store; any service can verify it independently (great for microservices). *Con:* you can't easily revoke one before it expires — it's valid until then. Mitigations: keep access tokens short-lived and pair them with a **refresh token**, plus a denylist for emergencies.
> The one-liner interviewers want: **"sessions are stateful and easy to revoke; JWTs are stateless and scale across services but hard to revoke early — so I keep them short-lived with refresh tokens."**

---

## OAuth2 and OIDC: "log in with Google," demystified

"OAuth2" and "OpenID Connect" scare people because of the jargon, but the shape is simple: **let a user grant your app limited access without giving you their password.**

> 💡 **Concept notes — OAuth2 vs OIDC, and the tokens**
> - **OAuth2 is *authorization delegation*.** Four roles: the **resource owner** (the user), the **client** (your app), the **authorization server** (Google's login), and the **resource server** (the API holding the data). The user logs in at the auth server, which hands your app an **access token** scoped to specific permissions (`scopes`) — your app never sees the password.
> - **OIDC (OpenID Connect) adds *authentication* on top of OAuth2.** It introduces the **ID token** (a JWT describing *who the user is*), which is what makes "Sign in with Google" actually a login rather than just an API-access grant.
> - **Three tokens to keep straight:** **access token** (call the API, short-lived), **refresh token** (get a new access token without re-login, long-lived, guarded), **ID token** (who the user is — OIDC only).
> - **SSO (Single Sign-On)** is the payoff: one identity provider, many apps — log in once, and OIDC/SAML lets every app trust the same login.
> Don't try to recite the full redirect dance in an interview. Say what it's *for* ("delegated access without sharing the password") and name the token types. That's the senior signal; the exact HTTP redirects are lookup-able.

---

## Auth in microservices: from the UI to the services

This is the question the To-Do behind this chapter really wanted: a browser logs in — how does auth flow through a system of many services?

> 💡 **Concept notes — the end-to-end flow**
> 1. **Login at the edge.** The UI sends credentials (or is redirected to an identity provider) and gets back a token — stored by the browser, ideally in an **httpOnly cookie** so JavaScript can't read it (XSS defense).
> 2. **The API gateway is the bouncer.** Every request enters through a **gateway** that validates the token *once* (checks signature and expiry, maybe calls the identity provider). Invalid → rejected at the door, before any service is touched. Centralizing validation here keeps each service from re-implementing it.
> 3. **Propagate identity inward.** The gateway forwards the request to internal services with the verified identity attached — either the JWT itself or a signed internal header (`X-User-Id`, scopes). Downstream services either **trust the gateway** (simplest) or **re-verify the token** (defense in depth).
> 4. **Secure service-to-service calls.** Services shouldn't blindly trust the network. **mTLS** (mutual TLS — both sides present certificates, often provided by a service mesh, [Chapter 6](interview-topics-chapter-6.md)) proves each service's identity to the other; internal tokens carry the *user's* identity.
> The distinction to state out loud: **the gateway authenticates the user; the mesh/mTLS authenticates the services; the token carried inward is how the user's identity travels between them.**

---

## The bits people forget

> 💡 **Concept notes — the cross-cutting must-knows**
> - **Never store passwords in plaintext.** Hash them with a slow, salted algorithm (**bcrypt / argon2** — deliberately slow to resist brute force). Never MD5/SHA-1, never reversible encryption.
> - **Where the token lives in the browser matters.** `httpOnly` cookie (safe from XSS-reading JS, but needs **CSRF** protection) vs `localStorage` (easy for SPAs, but readable by any injected script). Name the tradeoff; there's no free option.
> - **Short-lived access + refresh token** is the standard pattern — it bounds the damage of a leaked token while avoiding constant re-logins.
> - **Secrets rotation.** The signing key and client secrets must be rotatable and never in source control (Foundations/cloud secret managers).

---

## The arc that answers "how does auth work?"

> 💡 **Concept notes — a strong end-to-end answer**
> "User logs in → identity provider verifies and returns a **short-lived JWT access token** + **refresh token**, stored in an httpOnly cookie → every request hits the **API gateway**, which **validates the token once** → the gateway forwards the request inward with the user's identity, and **mTLS** secures the service-to-service hops → services authorize by **role/scope** in the token → when the access token expires, the refresh token silently gets a new one; on logout or compromise, revoke the refresh token."
> That sentence names authn, authz, tokens, the gateway, propagation, and revocation — everything the question is probing.

---

## Try it

Answer aloud, as if to an interviewer:

1. Authentication vs authorization — define each, and give the status code each failure returns.
2. Sessions vs JWTs — walk the tradeoff. Why are JWTs harder to revoke, and how do you mitigate it?
3. What problem does OAuth2 solve, and what does OIDC add on top? Name the access, refresh, and ID tokens' jobs.
4. A React app talks to five microservices. Trace how a logged-in user's identity reaches service #5, and where each hop is secured.
5. Where should the browser store the token, and what attack does each choice expose you to?
6. How are passwords stored safely, and why is a *slow* hash the point?
7. *Honest pivot:* you've used session-cookie auth but never OAuth2 in production. Bridge the gap out loud.

*Write your answers in [interview-topics-chapter-7-tryit.md](code/interview-topics-chapter-7-tryit.md).*

## The bumper sticker

> *Auth is two questions and one primitive: authentication (who are you?), authorization (what may you do?), and a token — a claim the server can verify. Sessions are stateful and revocable; JWTs are stateless and scale across services; OAuth2/OIDC delegate login without sharing passwords. In a microservice system the gateway checks the token once, mTLS secures the hops, and the token carries the user inward.*

Next: the layer all of this runs on — **cloud** — where GCP is the brand and the portable primitives are the concept that survives a provider switch.

---

<div align="right">

[Chapter 8 →](interview-topics-chapter-8.md)

</div>
