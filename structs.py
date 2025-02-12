import math
from datetime import datetime, time, timedelta


class Carrier:
    def __init__(self, name, loc):
        self.name = name
        self.loc = loc
        self.log_on_time = None
        self.orders = []
        self.actions = []
        self.overlaps = 0
        self.big_overlaps = 0

    def duration(self):
        dur = sum([act.duration.total_seconds() for act in self.actions])
        return dur

    def pick_duration(self):
        dur = sum([act.duration.total_seconds() for act in self.actions if act.type == 'PICK'])
        return dur

    def drop_duration(self):
        dur = sum([act.duration.total_seconds() for act in self.actions if act.type == 'DROP'])
        return dur

    def drive_duration(self):
        dur_pick = sum([act.duration.total_seconds() for act in self.actions if act.type == 'DRIVE_PICK'])
        dur_drop = sum([act.duration.total_seconds() for act in self.actions if act.type == 'DRIVE_DROP'])

        return dur_pick + dur_drop

    def travelled_distance(self):
        dist = sum([act.origin.dist(act.dest) for act in self.actions])
        return dist


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
    def __init__(self, order, origin, dest, start_time, duration, action_type):
        self.order = order
        self.origin = origin
        self.dest = dest
        self.start_time = start_time
        self.duration = timedelta(seconds=duration)
        self.end_time = self.start_time + self.duration
        self.type = action_type
        self.dist = self.origin.dist(self.dest)


def calculate_overlaps(vehicles):
    for i, car in enumerate(vehicles.values()):

        for i, act in enumerate(car.actions[:-1]):
            next_act = car.actions[i + 1]
            if act.end_time > next_act.start_time + timedelta(seconds=1):
                car.big_overlaps += 1
            elif act.end_time > next_act.start_time:
                car.overlaps += 1


def check_consistency(vehicles):
    inconsistent_actions = 0
    for car in vehicles.values():

        for i, act in enumerate(car.actions[:-1]):
            next_act = car.actions[i + 1]

            if next_act.type == 'DROP':
                if not (act.type == 'DRIVE_DROP' and act.order == next_act.order):
                    inconsistent_actions += 1
            if next_act.type == 'PICK':
                if not(act.type == 'DRIVE_PICK' and act.order == next_act.order):
                    inconsistent_actions += 1
            if next_act.type == 'DRIVE_DROP':
                if not (act.type == 'PICK' and act.order == next_act.order):
                    inconsistent_actions += 1
            if next_act.type == 'DRIVE_PICK':
                if not act.type == 'DROP':
                    inconsistent_actions += 1

    print('Number of action inconsistencies found:', inconsistent_actions)
