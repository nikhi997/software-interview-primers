class VendingMachine:
    def __init__(self):
        self.state = IdleState()
        self.money = 0
        self.stock = {"chips": 5, "soda": 3}
        self.prices = {"chips": 2, "soda": 3}

    def set_state(self, new_state):
        self.state = new_state
    def insert_money(self, amount):
        self.state.insert_money(self, amount)
    def select_item(self, item):
        self.state.select_item(self, item)
    def take_item(self):
        self.state.take_item(self)
    def cancel(self):
        self.state.cancel(self)
    def enter_maintenance(self):
        self.set_state(MaintenanceState())
    def exit_maintenance(self):
        self.set_state(IdleState() if any(self.stock.values()) else OutOfStockState())

class IdleState:
    def insert_money(self, machine, amount):
        machine.money += amount
        machine.set_state(HasMoneyState())
    def select_item(self, machine, item):
        print("Insert money first")
    def take_item(self, machine):
        print("Nothing to take")
    def cancel(self, machine):
        print("Nothing to cancel")

class HasMoneyState:
    def insert_money(self, machine, amount):
        machine.money += amount
    def select_item(self, machine, item):
        if machine.stock.get(item, 0) == 0:
            print("Out of that item")
            return
        if machine.money < machine.prices[item]:
            print("Not enough money")
            return
        machine.money -= machine.prices[item]
        machine.stock[item] -= 1
        machine.set_state(DispensingState())
        print(f"Dispensing {item}")
    def take_item(self, machine):
        print("Nothing to take")
    def cancel(self, machine):
        print(f"Refunding {machine.money}")
        machine.money = 0
        machine.set_state(IdleState())

class DispensingState:
        def insert_money(self, machine, amount):
            print("Wait, currently dispensing")
        def select_item(self, machine, item):
            print("Already dispensing")
        def take_item(self, machine):
            machine.set_state(IdleState() if any(machine.stock.values()) else OutOfStockState())
            print("Item taken")
        def cancel(self, machine):
            print("Can't cancel while dispensing")

class OutOfStockState:
        def insert_money(self, machine, amount):
            print(f"Machine empty, refunding {amount}")
        def select_item(self, machine, item):
            print("Machine empty")
        def take_item(self, machine):
            print("Nothing to take")
        def cancel(self, machine):
            print("Nothing to cancel")

class MaintenanceState:
        def insert_money(self, machine, amount):
            print("Machine under maintenance")
        def select_item(self, machine, item):
            print("Machine under maintenance")
        def take_item(self, machine):
            print("Machine under maintenance")
        def cancel(self, machine):
            print("Machine under maintenance")


    # def insert_money(self, amount):
    #     if self.state == "idle":
    #         self.money = amount
    #         self.state = "has_money"
    #     elif self.state == "has_money":
    #         self.money += amount
    #     elif self.state == "dispensing":
    #         print("Wait, currently dispensing")
    #     elif self.state == "out_of_stock":
    #         print(f"Machine empty, refunding {amount}")

    # def select_item(self, item):
    #     if self.state == "idle":
    #         print("Insert money first")
    #     elif self.state == "has_money":
    #         if self.stock.get(item, 0) == 0:
    #             print("Out of that item")
    #             return
    #         if self.money < self.prices[item]:
    #             print("Not enough money")
    #             return
    #         self.money -= self.prices[item]
    #         self.stock[item] -= 1
    #         self.state = "dispensing"
    #         print(f"Dispensing {item}")
    #     elif self.state == "dispensing":
    #         print("Already dispensing")
    #     elif self.state == "out_of_stock":
    #         print("Machine empty")

    # def take_item(self):
    #     if self.state == "dispensing":
    #         self.state = "idle" if any(self.stock.values()) else "out_of_stock"
    #         print("Item taken")
    #     else:
    #         print("Nothing to take")
