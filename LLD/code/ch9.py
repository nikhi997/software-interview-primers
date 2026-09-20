class Engineer:
    def __init__(self, name, employee_id, language):
        self.name = name
        self.language = language
        self.employee_id = employee_id
        self.base_salary = 100000

    def baddge(self):
        return f"EMP-{self.employee_id:05d}({self.name})"

    def monthly_pay(self):
        return self.base_salary / 12

class Manager:
    def __inti__(self, name, employee_id, reports):
        self.name = name
        self.employee_id = employee_id
        self.reports = reports
        self.base_salary = 150000

    def badge(self):
        return f"EMP-{self.employee_id:05d} ({self.name})"

    def monthly_pay(self):
        return self.base_salary / 12



class Employee:

    badge_prefix = "EMP"

    def __init__(self, name, employee_id, base_salary):
        self.name = name
        self.employee_id = employee_id
        self.base_salary = base_salary

    def badge(self):
        return f"{self.badge_prefix}-{self.employee_id:05d} ({self.name})"

    def monthly_pay(self):
        return self.base_salary / 12


class Engineer1(Employee):
    def __init__(self, name, employee_id, language):
        super().__init__(name, employee_id, base_salary=100000)
        self.language = language

    def writes_code_in(self):
        return self.language

class Manager1(Employee):
    def __init__(self, name, employee_id, reports):
        super().__init__(name, employee_id, base_salary=150000)
        self.reports = reports

    def run_one_on_one(self):
        return [f"1:1 with {report.name}" for report in self.reports]


from abc import ABC, abstractmethod

class Employee1(ABC):

    badge_prefix = "EMP"

    def __init__(self, name, employee_id, base_salary):
        self.name = name
        self.employee_id = employee_id
        self.base_salary = base_salary

    @abstractmethod
    def badge(self):
        pass

    @abstractmethod
    def monthly_pay(self):
        pass

class CodingSkill:
    def __init__(self, language):
        self.language = language

    def writes_code_in(self):
        return self.language
