# nouns:
#     parking lot,
#     floors
#     spots,
#     sizes
#     vehicles
#     flat fee

#     verbs:
#     vehicle_fits ?
#     is_occupied ?
#     vehicle_leave
#     calculate_parking_fee
#     pricing -flat or hourly or weekend
#     is_full
#     park_vehicle
#     unpark_vehicle


#     class
#     parkinglot
#         -holds floors
#         -park()
#         -unpark()
#         -is_full()
#         -calculate_fee()
#     floor
#         -holds spots
#         -is_full()
#         -find_a_spot
#     spot
#         -size
#         -is_occupied
#         -vehicle_fits()
#     vehicle
#         -size
#         -license_number


from abc import ABC
from time import time


class Vehicle(ABC):
    def __init__(self, license_number, size):
        self.license_number = license_number
        self.size = size

    def get_size(self):
        return self.size
class Motorcycle(Vehicle):
    def __init__(self, license_number):
        super().__init__(license_number, 'small')

class Car(Vehicle):
    def __init__(self, license_number):
        super().__init__(license_number, 'medium')
class Bus(Vehicle):
    def __init__(self, license_number):
        super().__init__(license_number, 'large')

class Spot:
    def __init__(self, id, size):
        self.id = id
        self.size = size
        self.occupied_by = None
        self.parked_time = None

    def is_occupied(self):
        return self.occupied_by is not None

    def vehicle_fits(self, vehicle):
        return vehicle.get_size() == self.size
    def park_vehicle(self, vehicle):
        if self.is_occupied():
            raise Exception("Spot is already occupied")
        if not self.vehicle_fits(vehicle):
            raise Exception("Vehicle does not fit in this spot")
        self.occupied_by = vehicle
        self.parked_time = time.time()  # Store the time when the vehicle was parked

    def unpark_vehicle(self):
        vehicle = self.occupied_by
        duration = time.time() - self.parked_time  # Calculate the duration of parking
        if not self.is_occupied():
            raise Exception("Spot is already empty")
        self.occupied_by = None
        return vehicle, duration

class Floor:
    def __init__(self, floor_number, spots):
            self.floor_number = floor_number
            self.spots = spots

    def is_full(self):
            return all(spot.is_occupied() for spot in self.spots)

    def find_a_spot(self, vehicle):
        for spot in self.spots:
                if not spot.is_occupied() and spot.vehicle_fits(vehicle):
                    return spot
        return None

class ParkingLot:
    def __init__(self, floors, pricing_strategy):
        self.floors = floors
        self.pricing_strategy = pricing_strategy
        self.listeners = []

    def park(self, vehicle):
        for floor in self.floors:
            if not floor.is_full():
                spot = floor.find_a_spot(vehicle)
                if spot:
                    spot.park_vehicle(vehicle)
                    self._notify_listeners(f"Vehicle {vehicle.license_number} parked at spot {spot.id} on floor {floor.floor_number}")
                    return
        raise Exception("Parking lot is full")

    def _notify_listeners(self, message):
        for listener in self.listeners:
            listener.update(message)
    def unpark(self, license_number):
        for floor in self.floors:
            for spot in floor.spots:
                if spot.is_occupied() and spot.occupied_by.license_number == license_number:
                    vehicle, duration = spot.unpark_vehicle()
                    fee = self.pricing_strategy.calculate_fee(duration)
                    self._notify_listeners(f"Vehicle {vehicle.license_number} unparked from spot {spot.id} on floor {floor.floor_number}. Parking fee: ${fee:.2f}")
                    return fee
        raise Exception("Vehicle not found in the parking lot")

    def subscribe(self, listener):
        self.listeners.append(listener)
