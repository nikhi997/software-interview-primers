

class OrderServiceLegacy:

    def place_order(self,user,items):
        self._send_email(user,"order confirmed")
        self._send_sms(user,"order confirmed")

    def _send_email(self, user, message):
        print(f"Email to {user.email}:{message}")

    def _send_sms(self, user, message):
        print(f"Sms to {user.email}:{message}")

class OrderService:

    def __init__(self):
        self.listeners=[]

    def subscribe(self,listener):
        self.listeners.append(listener)


    def unsubscribe(self,listener):
        self.listeners.remove(listener)

    def place_order(self, user,items):

        for listener in self.listeners:
            listener.handle(user,items)

class EmailService:
    def handle(self, user,items):
        print(f"Email to {user.email},items:{items}")

class SMSService:
    def handle(self, user,items):
        print(f"SMS to {user.email}, items:{items}")


class OrderService2:

    def _init__(self) :
        self.listeners=[]

    def subscribe(self,listener):
        self.listeners.append(listener)
    def unsubscribe(self,listener):
        self.listeners.remove(listener)
    def place_order(self,user,items):
        for listener in self.listeners:
            listener.handle(user,items)

class EmailService2:
    def handle(self,user,items):
        print(f"Email to {user.email},items:{items}")
