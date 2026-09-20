# Chapter 15: Worked problem — Chat system (WhatsApp) — Try it

*Answers for the Try it questions in [hld-chapter-15.md](../hld-chapter-15.md).*

1. Why can't a normal HTTP request/response model deliver a message to Bob the instant Alice sends it? What replaces it and how?


2. Trace a message from Alice to an *offline* Bob, then to Bob reconnecting. Where is durability guaranteed, and why "persist before deliver"?


3. The session registry is new state in a system that prized statelessness. Explain why it's necessary and how the design contains the statefulness.


4. A 200-person group chat gets a message. Describe delivery and connect it to Chapter 14's fanout.


5. A gateway server crashes with 1M live connections. Walk through what happens and why no messages are lost.
