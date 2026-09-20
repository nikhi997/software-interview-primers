"""Chapter 18 — A class in front of a class.

Proxy, Facade, and Chain of Responsibility. Dependency-free; run with `python3 ch18.py`.
"""


# --- Proxy -----------------------------------------------------------------

class RealImage:
    def __init__(self, filename):
        self.filename = filename
        self._load_from_disk()

    def _load_from_disk(self):
        print(f"loading {self.filename} from disk")  # pretend: slow and heavy

    def display(self):
        print(f"displaying {self.filename}")


class LazyImage:
    """Virtual proxy: builds the RealImage only on first display()."""

    def __init__(self, filename):
        self.filename = filename
        self._real = None

    def display(self):
        if self._real is None:
            self._real = RealImage(self.filename)
        self._real.display()


class ProtectedImage:
    """Protection proxy: same interface, guards access."""

    def __init__(self, real_image, user):
        self.inner = real_image
        self.user = user

    def display(self):
        if not self.user.is_admin:
            raise PermissionError("admins only")
        self.inner.display()


# --- Facade ----------------------------------------------------------------

class InventoryService:
    def reserve(self, item):
        print(f"reserved {item}")


class PaymentService:
    def charge(self, user, amount):
        print(f"charged {user} ${amount}")


class ShippingService:
    def schedule(self, item, address):
        print(f"shipping {item} to {address}")


class NotificationService:
    def send(self, user, message):
        print(f"[to {user}] {message}")


class OrderFacade:
    def __init__(self, inventory, payment, shipping, notifier):
        self.inventory = inventory
        self.payment = payment
        self.shipping = shipping
        self.notifier = notifier

    def place_order(self, user, item, amount, address):
        self.inventory.reserve(item)
        self.payment.charge(user, amount)
        self.shipping.schedule(item, address)
        self.notifier.send(user, f"your {item} is on the way")


# --- Chain of Responsibility -----------------------------------------------

class Approver:
    def __init__(self, name, limit):
        self.name = name
        self.limit = limit
        self.next = None

    def set_next(self, approver):
        self.next = approver
        return approver  # return it so we can chain set_next calls

    def approve(self, amount):
        if amount <= self.limit:
            print(f"{self.name} approves ${amount}")
        elif self.next is not None:
            self.next.approve(amount)
        else:
            print(f"${amount} exceeds all limits — rejected")


if __name__ == "__main__":
    print("# Proxy")
    gallery = [LazyImage("a.png"), LazyImage("b.png"), LazyImage("c.png")]
    gallery[1].display()  # only b.png loads

    print("\n# Facade")
    facade = OrderFacade(
        InventoryService(), PaymentService(), ShippingService(), NotificationService()
    )
    facade.place_order("alice", "book", 20, "1 Main St")

    print("\n# Chain of Responsibility")
    lead = Approver("team lead", 100)
    manager = Approver("manager", 1000)
    director = Approver("director", 10000)
    lead.set_next(manager).set_next(director)
    for amt in (50, 500, 5000, 50000):
        lead.approve(amt)
