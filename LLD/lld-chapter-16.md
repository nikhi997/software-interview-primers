# Chapter 16: Worked problem — Online Shopping

*[← Chapter 15](lld-chapter-15.md) · [Contents](lld-README.md)*

- [ ] **Mark as read**

The problem: *"Design an online shopping system. Users browse products, add to cart, checkout, pay."*

## Step 1: Clarify

- Single or multiple sellers? **Single seller for now.**
- Inventory tracking? **Yes — products have stock counts.**
- Payment methods? **Credit card, PayPal, gift card.**
- Promotions? **Yes — coupon codes for % off or $ off.**
- Shipping? **Flat $5 for now.**
- Order states? **Placed → Confirmed → Shipped → Delivered. Plus Cancelled.**

## Step 2: Entities

- **Product** — sku, name, price, stock
- **CartItem** — product + quantity
- **Cart** — list of CartItems, belongs to a User
- **User** — id, email, addresses
- **Order** — placed cart, state, total, payment
- **Payment** — method + amount
- **Discount** — % or $ off

`sku`, `price`, `stock`, `email` are single values their owner holds — attributes, not classes. `CartItem` earns class-hood the other way: a product *plus* a quantity *plus* the behavior of knowing its own line total is more than one value, so it's a class, not a field on `Cart`. The relationships are all `has-a` — a `User` *has* a `Cart`, a `Cart` *has* many `CartItem`s — none of these is a true `is-a`.

Patterns I see:
- Payment methods → **Strategy**
- Discount types → **Strategy** (or Decorator if stacking)
- Order state lifecycle → **State** or Enum + checks
- Order status notifications → **Observer**

## Step 3: Class diagram (verbal)

```
User ◆── Cart ◆── many CartItems ─── Product
User ◆── many Orders
Order has PaymentStrategy
Order has DiscountStrategy
Order has status (Placed/Confirmed/...)
Order has Listeners (Observer)
```

## Step 4: Code skeleton

```python
from enum import Enum


class Product:
    def __init__(self, sku, name, price, stock):
        self.sku = sku
        self.name = name
        self.price = price
        self.stock = stock


class CartItem:
    def __init__(self, product, quantity):
        self.product = product
        self.quantity = quantity

    def subtotal(self):
        return self.product.price * self.quantity


class User:
    def __init__(self, user_id, email):
        self.id = user_id
        self.email = email


class Cart:
    def __init__(self, user):
        self.user = user
        self.items = []

    def add(self, product, quantity):
        for item in self.items:
            if item.product.sku == product.sku:
                item.quantity += quantity
                return
        self.items.append(CartItem(product, quantity))

    def total(self):
        return sum(item.subtotal() for item in self.items)


# Payment Strategy
class CreditCardPayment:
    def __init__(self, card_number, cvv):
        self.card_number = card_number
        self.cvv = cvv

    def pay(self, amount):
        print(f"Charging ${amount} to card {self.card_number[-4:]}")
        return True


class PayPalPayment:
    def __init__(self, email):
        self.email = email

    def pay(self, amount):
        print(f"Charging ${amount} via PayPal {self.email}")
        return True


class GiftCardPayment:
    def __init__(self, card_code, balance):
        self.code = card_code
        self.balance = balance

    def pay(self, amount):
        if amount > self.balance:
            print("Gift card balance insufficient")
            return False
        self.balance -= amount
        return True


# Discount Strategy
class PercentageDiscount:
    def __init__(self, percent):
        self.percent = percent

    def apply(self, amount):
        return amount * (1 - self.percent / 100)


class FixedDiscount:
    def __init__(self, amount):
        self.discount = amount

    def apply(self, amount):
        return max(0, amount - self.discount)


class NoDiscount:
    def apply(self, amount):
        return amount


class OrderStatus(Enum):
    PLACED = "placed"
    CONFIRMED = "confirmed"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class Order:
    def __init__(self, order_id, cart, payment, discount=None):
        self.id = order_id
        self.user = cart.user
        self.items = cart.items[:]  # copy
        self.subtotal = cart.total()
        self.discount = discount or NoDiscount()
        self.total = self.discount.apply(self.subtotal) + 5  # shipping
        self.payment = payment
        self.status = OrderStatus.PLACED
        self.listeners = []

    def subscribe(self, listener):
        self.listeners.append(listener)

    def _notify(self, event):
        for listener in self.listeners:
            listener.handle(event, self)

    def confirm(self):
        if self.status != OrderStatus.PLACED:
            raise ValueError(f"Cannot confirm from {self.status}")
        success = self.payment.pay(self.total)
        if not success:
            self.status = OrderStatus.CANCELLED
            self._notify("order_cancelled")
            return False
        for item in self.items:
            item.product.stock -= item.quantity
        self.status = OrderStatus.CONFIRMED
        self._notify("order_confirmed")
        return True

    def ship(self):
        if self.status != OrderStatus.CONFIRMED:
            raise ValueError(f"Cannot ship from {self.status}")
        self.status = OrderStatus.SHIPPED
        self._notify("order_shipped")

    def deliver(self):
        if self.status != OrderStatus.SHIPPED:
            raise ValueError(f"Cannot deliver from {self.status}")
        self.status = OrderStatus.DELIVERED
        self._notify("order_delivered")

    def cancel(self):
        if self.status in (OrderStatus.SHIPPED, OrderStatus.DELIVERED):
            raise ValueError("Cannot cancel shipped order")
        self.status = OrderStatus.CANCELLED
        self._notify("order_cancelled")


class EmailNotifier:
    def handle(self, event, order):
        print(f"Email to {order.user.email}: {event}")
```

## Step 5: Walk a flow

```python
prod = Product("BOOK1", "Pragmatic Programmer", 30, 10)
user = User(1, "alice@x.com")
cart = Cart(user)
cart.add(prod, 2)

payment = CreditCardPayment("4111111111111111", "123")
discount = PercentageDiscount(10)

order = Order(1, cart, payment, discount)
order.subscribe(EmailNotifier())

order.confirm()  # charges card, decrements stock, emails confirmation
order.ship()     # emails shipped
order.deliver()  # emails delivered
```

## Step 6: Tradeoffs

- **"Discounts should stack."** → Switch from Strategy to Decorator. Discounts wrap each other. `BlackFridayDiscount(LoyaltyDiscount(NoDiscount()))`. Order calls `.apply` once; wrappers chain.

- **"Inventory race conditions when two users buy the last item."** → Move stock decrement into a transaction. DB-backed: `UPDATE products SET stock = stock - 1 WHERE sku = ? AND stock > 0`. The atomic check matters.

- **"Order state transitions should be more rigorous."** → Move to full State pattern. Each status becomes a class with allowed transitions. Currently we use if-checks in each method.

- **"Multiple sellers."** → Add Seller entity. Each Product belongs to a Seller. Cart can have items from multiple sellers; checkout splits into multiple Orders.

## Pattern audit

Used:
- **Strategy** for payment (Credit/PayPal/GiftCard)
- **Strategy** for discount (Percentage/Fixed/None)
- **Observer** for order events
- **Enum + if-checks** for status (lighter than full State)

Not used:
- **Full State pattern** for Order — overkill for 5 statuses with simple rules. If transitions get complex (partial returns, refunds, exchanges), revisit.
- **Singleton** — no shared singletons needed here.

The check: each pattern earned its place. None was added because it was named.

---

<div align="right">

[Chapter 17 →](lld-chapter-17.md)

</div>
