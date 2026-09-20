class VendingMachine:
    def __init__(self):
        self.state = IdleState()
        self.stocks = {"chips": 2, "biscuits": 5}
        self.prices = {"chips": 10, "biscuits": 15}
        self.money_in_machine = 0

    def set_state(self, new_state):
        self.state = new_state

    def insert_money(self, amount):
        self.state.insert_money(self, amount)

    def select_item(self, item):
        self.state.select_item(self, item)

    def dispense(self):
        self.state.dispense(self)

class IdleState:
    def insert_money(self, machine, amount):
        machine.money_in_machine += amount
        machine.set_state(HasMoneyState())
    def select_item(self, machine, item):
        print("insert money first")
    def dispense(self, machine):
        print("insert money first")


class HasMoneyState:
    def select_item(self, machine, item):
        if machine.stocks.get(item, 0) == 0:
            print("out of stock of that item")
            return
        if machine.money_in_machine < machine.prices[item]:
            print("not enough money ,insert more")
            return
        machine.money_in_machine -= machine.prices[item]
        machine.stocks[item] -= 1
        machine.set_state(DispensingState(item))
    def insert_money(self, machine, amount):
        machine.money_in_machine += amount
    def dispense(self, machine):
        print("select item first")

class DispensingState:
    def __init__(self, item):
        self.item = item

    def dispense(self, machine):
        print(f"Dispensing {self.item}")
        machine.set_state(IdleState())
    def insert_money(self, machine, amount):
        print("dispensing in progress, please wait")
    def select_item(self, machine, item):
        print("dispensing in progress, please wait")
