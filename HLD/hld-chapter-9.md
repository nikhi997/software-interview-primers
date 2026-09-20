# Chapter 9: When the files get large

*[← Chapter 8](hld-chapter-8.md) · [Contents](hld-README.md)*

- [ ] **Mark as read**

Every system so far moved small rows: a short code, a URL, a user record. Real products also move **big binary files** — profile pictures, uploaded videos, PDFs, audio. The moment files enter the picture, two beginner instincts cause real outages. Let's kill both.

The pain has two parts: *where do big files live*, and *how do you serve them to users far away without melting your servers*. The answers are **blob storage** and the **CDN.**

---

## Instinct #1 that breaks: storing files in the database

A new engineer's first thought: "files are data, the database stores data, put the files in the database." Don't.

Databases are tuned for small, structured rows you query and index. Stuffing a 2 GB video into a row:
- **Bloats the database**, making *every* operation slower — backups take forever, replication lag balloons, your nice indexes drown in binary blobs.
- **Wastes the database's strengths.** You never query *inside* a video. You don't need transactions or indexes on its bytes. You just need to store and retrieve the whole thing.
- **Is wildly expensive.** Database storage (with its replication, indexing, fast disks) costs far more per GB than storage designed for bulk files.

The right home for big files is **blob/object storage.**

> 💡 **Concept notes — blob / object storage**
> **Blob storage** (a.k.a. object storage — Amazon **S3**, Google Cloud Storage, Azure Blob) is a service built for one job: store and retrieve large files ("objects") by a key, cheaply and durably, at unlimited scale. It's not a filesystem and not a database — there are no queries, no joins, just `put(key, bytes)` and `get(key)`. It handles replication and durability for you (S3 famously targets *eleven nines* of durability). It's cheap per GB and scales effectively without limit.

**The standard pattern: store the file in blob storage, store a *pointer* in the database.**

```
database row:
  user_id: 123
  name: "Alice"
  avatar_url: "https://blobstore/avatars/123.jpg"   ← just a string pointer
                                                       the bytes live in S3
```

The database stays small and fast (it holds a URL string, not the image). The blob store holds the heavy bytes. Each tool does what it's good at. This separation is one of the most common real-world patterns in all of system design — *metadata in the database, bytes in blob storage.*

---

## Instinct #2 that breaks: serving files from your own servers

Now the file is in blob storage. A user in Tokyo requests it; your servers are in Virginia. Naively, the bytes travel Virginia → Tokyo for every request.

Two problems:
1. **Distance = latency.** Data can't beat the speed of light. Virginia↔Tokyo is ~150–200 ms *each way*, before any processing. A page full of images feels sluggish for anyone far from your servers.
2. **Repeated waste.** The *same* popular image gets shipped across the Pacific millions of times. That's enormous, redundant bandwidth — slow for users and expensive for you.

This is the same shape as Chapter 5's caching problem (paying full price for a repeated answer), but now the cost is *geographic distance*, and the fix is to cache the file **physically near the user.** That's a CDN.

> 💡 **Concept notes — CDN (Content Delivery Network)**
> A **CDN** (Cloudflare, Akamai, CloudFront, Fastly) is a network of cache servers — **edge locations** or **PoPs (points of presence)** — spread across cities worldwide. You put your static files behind it. The first time someone in a region requests a file, the CDN fetches it from your origin (the blob store) and **caches it at the edge location near that user.** Every subsequent request from that region is served from the nearby edge in a few milliseconds — never touching your origin or crossing an ocean.
> It's caching from Ch 5, applied to *static files*, with **geography** as the axis: instead of "cache the hot data in fast memory," it's "cache the file in a server near the user."

```
without CDN:  Tokyo user ───── 200 ms ─────▶ Virginia origin   (every time)

with CDN:     Tokyo user ─ 5 ms ─▶ Tokyo edge cache ─(only on miss)─▶ Virginia origin
              Osaka user ─ 8 ms ─▶ Tokyo edge cache  (already warm — instant)
```

---

## What belongs on a CDN (and what doesn't)

CDNs cache **static content** — files that are the same for everyone and change rarely:
- ✅ Images, videos, audio, PDFs
- ✅ CSS, JavaScript, fonts (your website's static assets)
- ✅ Anything large, popular, and identical across users

They generally do **not** serve **dynamic, personalized content** — your specific account balance, your personalized feed — because that's different for every user and every moment, so there's nothing reusable to cache. (Though modern CDNs blur this with edge compute and short-TTL caching of semi-dynamic content.)

> 💡 **Concept notes — static vs dynamic, the reusability test**
> The question for "can a CDN cache this?" is: *is this byte-for-byte identical for many users over some time window?* A product image: yes (cache it). Your personalized cart: no (compute it fresh). The more reusable across users and time, the better the CDN payoff. Same TTL/invalidation tradeoffs as Ch 5 apply — a CDN entry can be stale, so you set cache lifetimes or use **cache-busting** (versioned filenames like `app.v37.js`) to force fresh fetches when content changes.

---

## Bonus pattern: let clients talk to blob storage directly

Here's an elegant move interviewers love. When a user *uploads* a big file, you don't want those gigabytes flowing *through* your app servers (which would tie up your app capacity moving bytes around). Instead:

```
1. Client asks your app: "I want to upload a video."
2. App generates a short-lived PRE-SIGNED URL granting permission to write
   one specific object to blob storage, and returns it. (App did almost no work.)
3. Client uploads the bytes DIRECTLY to blob storage using that URL.
   Your app servers never touch the file's bytes.
4. Blob storage notifies your app (or the client tells it) "upload done."
5. App saves the pointer in the database.
```

> 💡 **Concept notes — pre-signed URLs**
> A **pre-signed URL** is a temporary, permission-scoped link that lets a client read or write *one specific object* directly in blob storage, without your servers proxying the data. It keeps heavy byte-shuffling off your app tier entirely — your app just hands out permission slips and records pointers. Downloads work the same way in reverse (serve a pre-signed or CDN URL instead of streaming the file through your app). This is how every serious file-upload feature works.

---

## Bringing it together: uploading and serving a profile picture

The full lifecycle, using everything from this chapter:

```
UPLOAD:
  client → app: "uploading avatar"
  app → client: pre-signed URL
  client → blob storage: PUT the image bytes (direct, app untouched)
  app → database: save avatar_url pointer

SERVE:
  another user loads Alice's profile
  app → database: read the row (tiny, fast) → get avatar_url (a CDN URL)
  client → CDN edge near them: GET the image (cached, ~5 ms)
       (CDN fetches from blob storage once on a miss, then serves the region)
```

Notice every tier does only what it's best at: the **database** holds tiny fast-to-query metadata, **blob storage** holds the cheap durable bytes, the **CDN** serves them fast worldwide, and the **app servers** never get bogged down shuffling gigabytes — they just coordinate.

---

## What we have now — the complete component vocabulary

That closes Part 2. You now have every core building block:

```
                         ┌── CDN (static files, near users)
client ──▶ load balancer ─┤
                         └─▶ app servers (stateless)
                               ├─▶ cache (hot reads)
                               ├─▶ database (sharded + replicated metadata)
                               ├─▶ blob storage (big files)
                               └─▶ queue ─▶ workers (async work)
            + rate limiting / backpressure protecting it all
```

Every box here exists because a *specific pain* forced it — a failure, a number, a distance, a spike. None of it is decoration. That's the entire method of Part 1 and 2: derive the architecture from the pains, never from a template.

---

## A word on "the cloud": you rent most of these boxes

Notice how many boxes above named a product — S3, Redis, CloudFront. That's not incidental. In a real interview you rarely *build* a load balancer or an object store; you *rent* a managed one. "The cloud" is just someone else running these building blocks so you don't have to — and knowing the model keeps you from re-inventing infrastructure you can summon in one API call.

> 💡 **Concept notes — managed cloud building blocks**
> The pain that birthed the cloud: every box above (database, cache, queue, blob store, load balancer) needs provisioning, patching, failover, and capacity planning — undifferentiated work that has nothing to do with your product. A **cloud provider** (AWS, GCP, Azure) runs these as **managed services** so you consume them as an API instead of operating them. Three terms worth being able to place: **IaaS** (rent raw machines — you still install everything), **PaaS** (rent a managed database/queue — they operate it, you just use it), and **serverless** (rent *per-request execution* — e.g. AWS Lambda — with no servers to size at all; you pay only when code runs and it scales to zero). Two more you'll be asked to reason about: a **region** is a geographic location (us-east-1), and an **availability zone (AZ)** is an isolated datacenter *within* a region — you spread replicas across AZs so one datacenter failure doesn't take you down (it's Chapter 2's "remove the single point of failure," at datacenter granularity). And **autoscaling** is the managed version of Chapter 8's spike problem: the provider adds and removes app instances automatically as load moves. The interview takeaway: name the *building block and the pain*, then note you'd reach for the managed version — "a managed queue like SQS" beats "I'd run my own Kafka cluster" unless you can justify the operational cost.

This doesn't change the method one bit — you still derive each box from a pain. The cloud only changes *who operates the box*, not *why it exists*.

---

Part 3 steps back to *name* what you've been doing — the vocabulary of tradeoffs (CAP, consistency, latency vs throughput) and how to *draw* a system — so you can talk about all this fluently. Then Part 4 puts it to work on real interview problems.

---

## Try it

1. A teammate proposes storing user-uploaded videos as binary columns in the main database. Give three concrete reasons this hurts, and the standard alternative.
2. Explain why a CDN helps a user in Australia load a US-hosted image, in terms of both latency and bandwidth. What kind of content does it *not* help with, and why?
3. Walk through the pre-signed URL upload flow. What's the specific benefit of the client uploading directly to blob storage instead of through your app servers?
4. You update your site's logo but users keep seeing the old one for hours. What CDN behavior causes this, and what are two ways to force the new version to appear?
5. For each, say where it lives (database / blob storage / CDN) and why: a user's display name, their uploaded résumé PDF, your site's main stylesheet, a movie file, a movie's title and rating.
6. An interviewer asks you to "design X at scale." You sketch a queue and a cache. Why is "I'd use a managed service like SQS / a managed Redis" usually the stronger answer than "I'd run my own"? When would you defend running your own instead?
7. What's the difference between a region and an availability zone, and why do you spread database replicas across AZs rather than across regions for failover?

*Write your answers in [hld-chapter-9-tryit.md](code/hld-chapter-9-tryit.md).*

---

## The bumper sticker

> *Big files live in cheap durable blob storage with only a pointer in the database, and reach distant users fast through a CDN that caches them at the edge — keep the heavy bytes off your database and off your app servers entirely.*

That's the full toolkit. Next, Part 3: put names to the tradeoffs you've been making, and learn to draw the system on a whiteboard.

---

<div align="right">

[Chapter 10 →](hld-chapter-10.md)

</div>
