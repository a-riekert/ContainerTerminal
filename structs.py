import math
from datetime import datetime, time, timedelta

class Carrier:
    def __init__(self, name, loc):
        self.name = name
        self.loc = loc
        self.log_on_time = None
        self.orders = []
        self.actions = []


class Location:
    def __init__(self, name, coordinates, capacity=math.inf):
        self.name = name
        self.coordinates = coordinates
        self.capacity = capacity
        self.nr_carriers = 0

    def dist(self, other_loc):
        return abs(self.coordinates[0] - other_loc.coordinates[0]) + abs(self.coordinates[1] - other_loc.coordinates[1])


class Order:
    def __init__(self, name, origin, dest, first_time):
        self.name = name
        self.origin = origin
        self.dest = dest
        self.first_time = first_time

        self.pick_carrier = []
        self.drop_carrier = []
        self.drop_location = []
        self.pick_location = []


class Action:
    def __init__(self, origin, dest, start_time, duration, action_type):
        self.origin = origin
        self.dest = dest
        self.start_time = start_time
        self.duration = timedelta(seconds=duration)
        self.end_time = self.start_time + self.duration
        self.type = action_type
        self.dist = self.origin.dist(self.dest)

