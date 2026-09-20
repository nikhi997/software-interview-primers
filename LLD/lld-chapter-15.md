# Chapter 15: Worked problem — Library Management

*[← Chapter 14](lld-chapter-14.md) · [Contents](lld-README.md)*

- [ ] **Mark as read**

A worked LLD problem. I'm doing the five-step ritual. Read this *after* trying the problem cold yourself. Otherwise you memorize my solution instead of building the muscle.

The problem: *"Design a library management system. Members borrow books, return them, pay fines for late returns."*

## Step 1: Clarify

- Single library or chain? **Single, for now.**
- Membership types — any tiers? **Two: standard and premium. Premium gets longer loan periods and more books.**
- Reservations on unavailable books? **Yes.**
- Multiple copies of the same book? **Yes — Book is the abstract title; BookCopy is a physical item.**
- Fines — flat per day or escalating? **Flat: $1/day late.**
- Max books per member? **5 standard, 10 premium.**

Scope locked.

## Step 2: Entities

- **Book** — title, author, ISBN (the abstract work)
- **BookCopy** — specific physical copy with a status
- **Member** — user of the library, has a membership type
- **Membership** — rules for loan period and max books
- **Loan** — record of a member borrowing a copy
- **Reservation** — record of a member waiting for a copy
- **Library** — orchestrates everything

Note what *didn't* become a class: `title`, `author`, `isbn`, `due_date` are single values their owner carries — attributes, not classes. The trickiest call is `Book` versus `BookCopy`: a "book" sounds like one thing, but the abstract title (its ISBN and author) and a physical copy (its borrow status) have different state and behavior, so it's really *two* nouns wearing one word — split them. The verbs (*borrow, return, pay a fine*) land on `Library` and `Loan`, the things that own those actions.

Patterns I'm spotting:
- Membership types with different rules → **Strategy** (or just plain classes)
- Fine calculation could vary → potential **Strategy** for fines
- Notifications when books become available → **Observer**

## Step 3: Class diagram (verbal sketch)

```
Library
  ◆── many Books
  ◆── many Members
  ◆── many Loans
  ◆── many Reservations

Book
  ◇── many BookCopies

BookCopy
  has status: AVAILABLE / BORROWED / RESERVED

Member
  has Membership (Standard or Premium)

Loan
  has Member, BookCopy, due_date

Reservation
  has Member, Book, timestamp
```

## Step 4: Code skeleton

```python
import time
from enum import Enum


class CopyStatus(Enum):
    AVAILABLE = "available"
    BORROWED = "borrowed"
    RESERVED = "reserved"


class Book:
    def __init__(self, isbn, title, author):
        self.isbn = isbn
        self.title = title
        self.author = author
        self.copies = []


class BookCopy:
    def __init__(self, copy_id, book):
        self.copy_id = copy_id
        self.book = book
        self.status = CopyStatus.AVAILABLE


class StandardMembership:
    max_books = 5
    loan_period_days = 14


class PremiumMembership:
    max_books = 10
    loan_period_days = 30


class Member:
    def __init__(self, member_id, name, membership):
        self.id = member_id
        self.name = name
        self.membership = membership
        self.current_loans = []


class Loan:
    def __init__(self, loan_id, member, copy, due_date):
        self.id = loan_id
        self.member = member
        self.copy = copy
        self.borrowed_at = time.time()
        self.due_date = due_date
        self.returned_at = None


class Reservation:
    def __init__(self, reservation_id, member, book):
        self.id = reservation_id
        self.member = member
        self.book = book
        self.reserved_at = time.time()


class Library:
    def __init__(self):
        self.books = {}  # isbn -> Book
        self.members = {}  # member_id -> Member
        self.loans = []
        self.reservations = []
        self.fine_per_day = 1

    def borrow(self, member_id, isbn):
        member = self.members[member_id]
        book = self.books[isbn]

        if len(member.current_loans) >= member.membership.max_books:
            raise ValueError("Loan limit reached")

        available = [c for c in book.copies if c.status == CopyStatus.AVAILABLE]
        if not available:
            # auto-reserve
            res = Reservation(len(self.reservations), member, book)
            self.reservations.append(res)
            return None

        copy = available[0]
        copy.status = CopyStatus.BORROWED
        due_date = time.time() + member.membership.loan_period_days * 86400
        loan = Loan(len(self.loans), member, copy, due_date)
        self.loans.append(loan)
        member.current_loans.append(loan)
        return loan

    def return_book(self, loan_id):
        loan = self.loans[loan_id]
        loan.returned_at = time.time()
        loan.copy.status = CopyStatus.AVAILABLE
        loan.member.current_loans.remove(loan)

        fine = self._calculate_fine(loan)

        # if anyone reserved this book, notify them
        for reservation in self.reservations[:]:
            if reservation.book == loan.copy.book:
                # in real system: notify reservation.member
                self.reservations.remove(reservation)
                break

        return fine

    def _calculate_fine(self, loan):
        if loan.returned_at <= loan.due_date:
            return 0
        days_late = (loan.returned_at - loan.due_date) / 86400
        return days_late * self.fine_per_day
```

## Step 5: Walk a flow

*"Alice borrows a book. Returns it 5 days late."*

```python
lib = Library()
book = Book("978-0", "Pragmatic Programmer", "Hunt & Thomas")
book.copies.append(BookCopy(1, book))
lib.books["978-0"] = book

alice = Member(1, "Alice", StandardMembership())
lib.members[1] = alice

loan = lib.borrow(1, "978-0")
# loan exists, due in 14 days

# simulate 5 days overdue
loan.due_date = time.time() - 5 * 86400

fine = lib.return_book(loan.id)
# fine = 5 days * $1 = $5
```

## Step 6: Tradeoffs

- **"Multiple members reserve the same book."** → Queue. FIFO. First reservation gets the next available copy. Add a `position` field to Reservation.

- **"Notify members when reserved books become available."** → Observer. `Library` subscribes to `BookCopy` status changes. On AVAILABLE, check reservations; notify first in line.

- **"Premium members get reservation priority."** → Modify the queue to sort by membership type first, then timestamp.

- **"Different fine rates for different books."** → Move fine calculation to a Strategy. Each Book has a `fine_strategy`.

## Pattern audit

Used:
- **Plain classes** for Book, BookCopy, Member, Loan, Reservation
- **Strategy-ish** for Membership (different rules per type — though here I used simple classes with class attributes; for richer behavior, full Strategy)
- **Enum** for CopyStatus (state-like but no rich behavior, so an enum is enough)

Not used (and why):
- **State pattern** — BookCopy has states, but the behavior in each state is trivial. Enum + if-checks suffices. State pattern would be overkill.
- **Observer** — could add for notifications. Mentioned in tradeoffs. Not needed for basic functionality.
- **Decorator** — no behavior wrapping required.

Patterns are tools. Use them when they earn their keep. Don't shoehorn.

---

<div align="right">

[Chapter 16 →](lld-chapter-16.md)

</div>
