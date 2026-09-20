# Chapter 13: Drawing what you've been building

*[← Chapter 12](lld-chapter-12.md) · [Contents](lld-README.md)*

- [ ] **Mark as read**

When an interviewer asks you to design something, they often expect you to draw a class diagram. This is UML — Unified Modeling Language. There's a whole textbook of UML. You need about 10% of it for LLD interviews. Here's that 10%.

## What a class looks like

A class is a box with three sections:

```
┌────────────────────┐
│   URLShortener     │
├────────────────────┤
│ - urls: dict       │
│ - clicks: dict     │
│ - storage: Storage │
├────────────────────┤
│ + shorten(): str   │
│ + expand(): str    │
│ + click_count(): int│
│ - _save(): void    │
└────────────────────┘
```

Top: class name.
Middle: attributes (instance variables). `-` means private, `+` means public.
Bottom: methods. Same visibility marks. Sometimes return types.

In an interview, don't agonize over formatting. A labeled box with three sections is enough. Most interviewers skip return types.

## How classes relate

Five relationships matter.

### 1. Association — "A uses B"

A simple line between two classes. One class knows about the other, calls its methods, has a reference to it.

```
[URLShortener]──────[Storage]
```

URLShortener has a Storage. Calls Storage's methods. Association.

### 2. Aggregation — "A has B, but B can exist independently"

A line with an *empty* diamond at the owner end.

```
[Library]◇──────[Book]
```

A library has books. Books also exist outside libraries. If the library closes, the books still exist.

### 3. Composition — "A has B, and B can't exist without A"

A line with a *filled* diamond at the owner end.

```
[Order]◆──────[OrderLine]
```

An order has order lines. Delete the order, the order lines go with it. They have no meaning without their parent.

The diamond difference (empty vs filled) is the lifecycle difference. In practice, the distinction often doesn't matter for an interview — interviewers care that you used *some* relationship.

### 4. Inheritance — "A is a B"

A line with an empty *triangle* at the parent end.

```
[Motorcycle]──────▷[Vehicle]
[Car]─────────────▷[Vehicle]
[Truck]───────────▷[Vehicle]
```

The triangle points at the parent.

### 5. Dependency — "A depends on B briefly"

A dashed line with an arrow.

```
[OrderProcessor]- - - ->[Logger]
```

OrderProcessor uses Logger inside one method (passed in, say) but doesn't hold it as an attribute. *Weaker* than association.

Dependency vs association is a fuzzy line in practice. Don't sweat it in interviews.

## Multiplicity — how many

Numbers on line ends. Common ones:

- `1` — exactly one
- `0..1` — zero or one
- `*` — many (zero or more)
- `1..*` — at least one
- `5` — exactly five

```
[Floor] 1───────* [Spot]
```

A floor has many spots. Each spot belongs to one floor.

## Putting it together: the parking lot

The parking lot from Ch10 as UML (rough ASCII version):

```
                 ┌──────────────────┐
                 │   ParkingLot     │
                 ├──────────────────┤
                 │ - floors         │
                 │ - pricing        │
                 │ - listeners      │
                 ├──────────────────┤
                 │ + park()         │
                 │ + leave()        │
                 │ + subscribe()    │
                 └──────────────────┘
                  ◆ *                  ◇ 1                ◇ *
                  │                     │                  │
          ┌────────────────┐  ┌───────────────────┐  ┌─────────────┐
          │     Floor      │  │ PricingStrategy   │  │  Listener   │
          ├────────────────┤  ├───────────────────┤  ├─────────────┤
          │ - number       │  │ + calculate()     │  │ + handle()  │
          │ - spots        │  └───────────────────┘  └─────────────┘
          └────────────────┘            ▲                   ▲
            ◆ *                         │                   │
            │                ┌──────────┴──────┐    ┌───────┴──────┐
         ┌──────┐            │FlatHourly│PerVeh│    │Email │Gate   │
         │ Spot │            └──────────┴──────┘    └───────┴──────┘
         ├──────┤
         │ size │
         │ park()│
         └──────┘
            │ 0..1
            ▼
         ┌─────────┐
         │ Vehicle │◁── Motorcycle, Car, Truck
         └─────────┘
```

What this conveys:
- ParkingLot is composed of Floors
- ParkingLot has a PricingStrategy (Strategy pattern visible)
- ParkingLot has many Listeners (Observer pattern visible)
- Floors have many Spots
- Spots have zero-or-one Vehicle
- Vehicle has subclasses

The diagram tells the design story in one image. That's its job.

## How to draw fast in an interview

You won't have time for clean boxes. Shortcuts:

1. **Boxes:** rough rectangles, class name only. Add fields if asked.
2. **Lines:** plain lines between classes. Add diamonds/triangles only when the relationship type matters to the question.
3. **Talk while drawing.** "ParkingLot has Floors — composition because spots don't make sense outside a lot. Each Floor has many Spots. The lot uses a Pricing Strategy — I'll show three concretes below the abstraction."

Speed beats precision. The interviewer wants your thinking. The diagram is the prop.

## What you should be able to do

After this chapter, given any class you've written in this book:

1. Draw a box with attributes and methods
2. Draw boxes for collaborators
3. Connect with the right kind of line
4. Explain the design verbally while drawing

Practice. Take Ch10's parking lot, close the file, draw the UML on paper from memory. Compare. Note what's missing.

## Before you turn the page

**Exercise 1:** Draw UML for the URL shortener with all its storage classes (Ch3 + Ch8 decorators). Include FileStorage, MemoryStorage, RedisStorage, EncryptedStorage, LoggedStorage. Show the relationships.

**Exercise 2:** Draw UML for the vending machine (Ch7) including state classes. Show that the machine has a current state and that states transition the machine.

**Exercise 3:** Take a class from your professional codebase. Draw it. Then draw its three closest collaborators. Notice what's clear from the diagram and what's still confusing.

---

<div align="right">

[Chapter 14 →](lld-chapter-14.md)

</div>
