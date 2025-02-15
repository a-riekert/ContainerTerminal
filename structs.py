import math
from datetime import datetime, time, timedelta
from typing import Dict


class Location:
    """Class describing a location in the terminal.
    name: name of the location
    coordinates: tuple of (x,y)-coordinates
    capacity: number of carrier lanes (default: infinity)"""
    def __init__(self,
                 name: str,
                 coordinates: tuple[int, int],
                 capacity=math.inf):
        self.name = name
        self.coordinates = coordinates
        self.capacity = capacity
        self.nr_carriers = 0

    def dist(self, other_loc):
        """Manhattan (L1) distance to another location"""
        return abs(self.coordinates[0] - other_loc.coordinates[0]) + abs(self.coordinates[1] - other_loc.coordinates[1])


class Carrier:
    """Class describing a straddle carrier.
    name: name of the carrier,
    loc: initial location"""
    def __init__(self,
                 name: str,
                 loc: Location):
        self.name = name
        self.loc = loc
        self.orders = []
        self.actions = []
        self.overlaps = 0
        self.big_overlaps = 0

    def duration(self):
        """Total time carrier spent on all actions."""
        dur = sum([act.duration.total_seconds() for act in self.actions])
        return dur

    def pick_duration(self):
        """Total time carrier spent on all pick actions."""
        dur = sum([act.duration.total_seconds() for act in self.actions if act.type == 'PICK'])
        return dur

    def drop_duration(self):
        """Total time carrier spent on all drop actions."""
        dur = sum([act.duration.total_seconds() for act in self.actions if act.type == 'DROP'])
        return dur

    def drive_pick_duration(self):
        """Total time carrier spent on all drive-to-pick actions."""
        dur = sum([act.duration.total_seconds() for act in self.actions if act.type == 'DRIVE_PICK'])
        return dur

    def drive_drop_duration(self):
        """Total time carrier spent on all drive-to-drop actions."""
        dur = sum([act.duration.total_seconds() for act in self.actions if act.type == 'DRIVE_DROP'])
        return dur

    def travelled_distance_pick(self):
        """Total distance carrier drove to pick locations."""
        dist_pick = sum([act.dist() for act in self.actions if act.type == 'DRIVE_PICK'])
        return dist_pick

    def travelled_distance_drop(self):
        """Total distance carrier drove to drop locations."""
        dist_drop = sum([act.dist() for act in self.actions if act.type == 'DRIVE_DROP'])
        return dist_drop


class Order:
    """Class describing a container order.
    name: id of the container order
    origin: start location
    dest: destination location
    first_time: time order first becomes known."""
    def __init__(self,
                 name: str,
                 origin: Location,
                 dest: Location,
                 first_time: datetime):
        self.name = name
        self.origin = origin
        self.dest = dest
        self.first_time = first_time

        self.pick_carrier = []
        self.drop_carrier = []
        self.drop_location = []
        self.pick_location = []


class Action:
    """Class describing what a carrier does.
    carrier: vehicle that does the action,
    order: container order the action belongs to,
    origin: location where it starts,
    dest: location where it ends,
    start_time: time the action starts,
    duration: number of seconds the action takes,
    action_type: describes what exactly it does.
    Can be LOGON, PICK, DROP, DRIVE_PICK, DRIVE_DROP, FINISH_PICK, FINISH_DROP."""
    def __init__(self,
                 carrier: Carrier,
                 order: Order | None,
                 origin: Location,
                 dest: Location,
                 start_time: datetime,
                 duration: int,
                 action_type: str):
        self.carrier = carrier
        self.order = order
        self.origin = origin
        self.dest = dest
        self.start_time = start_time
        self.duration = timedelta(seconds=duration)
        self.end_time = self.start_time + self.duration
        self.type = action_type

    def dist(self):
        return self.origin.dist(self.dest)


def calculate_overlaps(vehicles: Dict[str, Carrier]):
    """Calculates number of actions that overlap in time for each carrier."""
    for i, car in enumerate(vehicles.values()):

        for i, act in enumerate(car.actions[:-1]):
            next_act = car.actions[i + 1]
            if act.end_time > next_act.start_time + timedelta(seconds=1):
                # overlap of more than 1s.
                car.big_overlaps += 1
            elif act.end_time > next_act.start_time:
                # overlap of 1s, could be due to rounding errors.
                car.overlaps += 1


def check_consistency(vehicles: Dict[str, Carrier]):
    """Checks if actions of each carrier are consistent."""
    inconsistent_actions = []
    for car in vehicles.values():

        for i, act in enumerate(car.actions[:-1]):
            next_act = car.actions[i + 1]

            if next_act.type == 'DROP':
                # e.g. to drop a container, the carrier first has to drive there with the same container.
                if not (act.type == 'DRIVE_DROP' and act.order == next_act.order):
                    inconsistent_actions.append(act)
            if next_act.type == 'PICK':
                if not(act.type == 'DRIVE_PICK' and act.order == next_act.order):
                    inconsistent_actions.append(act)
            if next_act.type == 'DRIVE_DROP':
                if not (act.type == 'FINISH_PICK' and act.order == next_act.order):
                    inconsistent_actions.append(act)
            if next_act.type == 'DRIVE_PICK':
                # to drive to pickup location the carrier first has to finish the previous drop, etc.
                if not (act.type == 'FINISH_DROP' or act.type == 'LOGON'):
                    inconsistent_actions.append(act)
            if next_act.type == 'FINISH_PICK':
                if not (act.type == 'PICK' and act.order == next_act.order):
                    inconsistent_actions.append(act)
            if next_act.type == 'FINISH_DROP':
                if not (act.type == 'DROP' and act.order == next_act.order):
                    inconsistent_actions.append(act)
            if i == 0:  # first action should be LOGON
                if not act.type == 'LOGON':
                    inconsistent_actions.append(act)
            if i == 1:  # second action should be PICK or drive to PICK
                if not (act.type == 'PICK' or act.type == 'DRIVE_PICK'):
                    inconsistent_actions.append(act)

    return inconsistent_actions
