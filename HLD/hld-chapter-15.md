# Chapter 15: Worked problem — Chat system (WhatsApp)

*[← Chapter 14](hld-chapter-14.md) · [Contents](hld-README.md)*

- [ ] **Mark as read**

Running the six-step ritual again. Attempt it cold first.

The problem: *"Design a real-time chat system like WhatsApp. Users send messages to each other (and to groups), see delivery/read receipts, and get messages instantly even on a flaky phone network."*

Signature lesson: **real-time delivery** — the server must *push* to clients, which breaks the request/response model every previous chapter assumed. This forces a new tool (**persistent connections**) and a new kind of state (**which user is connected to which server**).

---

## Step 1: Clarify

**Functional:**
- 1:1 messaging. ✅
- Group messaging. ✅
- Delivery + read receipts (sent / delivered / read). ✅
- Online/last-seen status. ✅
- Offline delivery — messages wait and arrive when you reconnect. ✅ *(critical — phones go offline constantly)*

**Non-functional:**
- Scale? → *2B users, 100B messages/day.*
- Latency? → *Real-time — sub-second delivery.*
- Consistency? → *Messages must not be lost and must arrive in order within a conversation.*
- Availability? → *High; people rely on it.*

Two demands stand out and shape everything: **real-time push** and **never lose a message / keep order.**

---

## Step 2: Estimate

**Messages:**
$$\frac{100\text{B/day}}{100{,}000} = 1{,}000{,}000 \text{ messages/sec}$$

A million messages/sec — write-heavy, unlike the feed problem.

**Connections:** up to ~2B devices want to stay connected. Even with a fraction online at once, that's *hundreds of millions of simultaneous open connections* — a defining constraint.

**Storage:** messages are small (~100 bytes) but volume is huge: 100B × 100 B = 10 TB/day. Often messages are deleted after delivery (or kept briefly), which changes the storage story a lot — *clarify retention.*

> 💡 The dominating constraints here are **connection count** (hundreds of millions of live connections) and **delivery guarantees**, not raw throughput. That's what makes chat architecturally different from a feed.

---

## Step 3: API + data model

Chat isn't classic REST request/response — the server must *initiate* sending a message to a recipient who didn't ask for it. The connection model (Step 4) carries messages. Logical operations:

```
sendMessage(to, text)              → server routes + persists + delivers
getMessages(conversation, since)   → fetch history / offline backlog
connection events: "delivered", "read", "typing", presence
```

**Data model:**
```
MESSAGE:       message_id, conversation_id, sender_id, text, created_at, status
CONVERSATION:  conversation_id, [participant_ids]
USER_INBOX:    user_id, [undelivered message_ids]    (queue of pending messages)
```

**SQL or NoSQL?** Massive write volume, simple access by conversation, no joins on the hot path → **NoSQL**, sharded by `conversation_id` (so a conversation's messages live together and stay ordered — recall Ch 4: shard by the dominant query's key).

---

## Step 4: High-level design — the connection problem

Every prior chapter used **request/response**: client asks, server answers, done. Chat breaks this. When Alice messages Bob, the server must **push** to Bob — but Bob's phone isn't currently asking for anything. HTTP request/response can't push.

### The tool: persistent connections (WebSockets)

Instead of a new request per message, each client opens **one long-lived connection** to the server and keeps it open. Messages flow *both ways* over it, anytime, in real time.

> 💡 **Concept notes — WebSockets vs polling**
> **Polling:** client repeatedly asks "any new messages?" every few seconds. Simple but wasteful (mostly empty answers) and not truly real-time (up to one interval late).
> **Long polling:** client asks and the server *holds* the request open until there's something to send. Better, still clunky.
> **WebSocket:** a single persistent, **bidirectional** connection held open. The server can push to the client *instantly* whenever a message arrives, with no repeated requests. This is the standard for real-time chat. The cost: the server must *hold open* and track millions of these connections — which creates the next problem.

### The new problem: connection state and routing

Here's the twist that makes chat hard. Those persistent connections are **stateful** — Bob's connection lives on *one specific server* (call it the **connection/gateway server**). But our app servers were supposed to be *stateless* (Ch 2)! Now, to deliver Alice's message to Bob, the system must answer: **which gateway server currently holds Bob's open connection?**

This needs a **session registry** — a fast shared store mapping `user_id → which gateway server holds their connection`:

```
Alice sends "hi" to Bob:
  1. Alice's message arrives at her gateway server
  2. persist the message (durability — must not lose it)
  3. look up in the session registry: "where is Bob connected?"
        → "Bob is on gateway-server-42"
  4. route the message to gateway-server-42
  5. gateway-42 pushes "hi" down Bob's open WebSocket — instant delivery
  6. Bob's app acks → mark "delivered" → notify Alice (receipt)
```

> 💡 **Concept notes — the connection registry**
> The session registry (e.g., in Redis) is the heart of a chat system: it tracks who's connected where, so messages can be *routed* to the right gateway server. When Bob connects, he registers ("I'm on gateway-42"); when he disconnects, he's removed. This is the carefully-managed exception to "stateless servers": the *connection* is inherently stateful, so we isolate that state in dedicated gateway servers plus a shared registry, keeping the rest of the system stateless.

### Offline delivery

Bob's phone is off. The session registry shows no active connection. So:
- Persist the message and queue it in Bob's **inbox** (USER_INBOX — pending messages).
- When Bob reconnects, his gateway pulls the inbox and delivers the backlog, in order.
- This is why messages survive a dead phone — they're **persisted first, delivered second.** Persist-then-deliver is the rule that guarantees no message is lost (durability, Ch 7).

### The full diagram

```
  Alice's phone ══persistent WebSocket══╗
                                        ▼
                              ┌──────────────────┐      ┌─────────────────┐
                              │ gateway servers  │◀────▶│ session registry│
                              │ (hold open conns)│      │ user→gateway    │
                              └────────┬─────────┘      │ (Redis)         │
                                       │                └─────────────────┘
                              route to recipient's gateway
                                       │
                                       ▼
                              ┌──────────────────┐
                              │ message service  │──▶ queue (Ch 6) for
                              │ persist + route  │    fanout/offline
                              └────────┬─────────┘
                                       ▼
                              ┌──────────────────────────┐
                              │ NoSQL: messages, inboxes  │ sharded by
                              │ (sharded by conversation) │ conversation_id
                              └──────────────────────────┘
   Bob's phone ══persistent WebSocket══╝  (on gateway-42)
```

### Groups = fanout, again

A group message to 50 people? **Fanout** (Ch 14 returns): persist once, then look up each of the 50 recipients in the registry and push to each one's gateway (or queue for the offline ones). For *huge* groups, this is the same fanout-cost tradeoff as the feed — you might fan out via workers/queue rather than inline.

---

## Step 5: Deep dive

- *"Message ordering?"* → Sharding by `conversation_id` keeps a conversation on one shard; assign monotonic sequence numbers per conversation so clients can order/detect gaps. (Order *within* a conversation is what matters, not global order — same insight as Ch 6's per-partition ordering.)
- *"Exactly-once delivery?"* → Truly exactly-once is famously near-impossible; do **at-least-once + idempotency** (Ch 6): each message has a unique ID, clients dedupe on it. Receipts (sent/delivered/read) are themselves messages flowing back.
- *"Hundreds of millions of connections?"* → Many gateway servers, each holding a slice of connections; the registry routes between them. Connections are cheap to *hold* but you need many boxes to hold that many — scale the gateway tier horizontally.
- *"A gateway server dies?"* → All its connections drop; clients auto-reconnect (to a different gateway), re-register in the registry, and pull any missed messages from their persisted inbox. Persist-then-deliver makes this safe — nothing is lost.

---

## Step 6: Bottlenecks & tradeoffs

- **Next bottleneck:** the session registry (every message does a lookup) → it must be fast and sharded; or co-locate routing logic. Huge groups stress fanout → workers + queues.

To extend this design across regions, including home-region routing, ordering, replay, and duplicate effects, use the [multi-region and event-driven design drills](hld-multi-region-event-driven-drills.md).
- **Tradeoffs made:** we **persist every message before delivering** (durability over raw latency — a few extra ms to never lose a message; correct call for chat). We accept **at-least-once + idempotency** rather than chasing impossible exactly-once. We carve out **stateful gateway servers** as a deliberate exception to statelessness, isolating the connection state so the rest stays stateless and scalable.

---

## The one thing to remember

Chat flips the model: the server must **push**, so you need **persistent connections** (WebSockets), which forces **connection state** (the session registry mapping user → gateway), and **persist-then-deliver** guarantees no message is lost across flaky networks. *Real-time delivery = persistent connections + a routing registry + durable inboxes.*

---

## Try it

1. Why can't a normal HTTP request/response model deliver a message to Bob the instant Alice sends it? What replaces it and how?
2. Trace a message from Alice to an *offline* Bob, then to Bob reconnecting. Where is durability guaranteed, and why "persist before deliver"?
3. The session registry is new state in a system that prized statelessness. Explain why it's necessary and how the design contains the statefulness.
4. A 200-person group chat gets a message. Describe delivery and connect it to Chapter 14's fanout.
5. A gateway server crashes with 1M live connections. Walk through what happens and why no messages are lost.

*Write your answers in [hld-chapter-15-tryit.md](code/hld-chapter-15-tryit.md).*

---

## The bumper sticker

> *Real-time chat means the server pushes: hold persistent WebSocket connections on stateful gateway servers, route via a user→gateway registry, and always persist before delivering so a dead phone never loses a message.*

Last problem: ride-sharing, where the signature challenge is *geography* — matching riders and drivers in physical space, in real time.

---

<div align="right">

[Chapter 16 →](hld-chapter-16.md)

</div>
