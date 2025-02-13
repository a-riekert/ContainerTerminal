from structs import *

import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter


def kms(x, _):
    """Converts millimeters to kilometres for axis formatting."""
    return f'{x * 1e-6:.1f}km'


def plot_locs_and_vehicles(locations: Dict[str, Location],
                           vehicles: Dict[str, Carrier]):
    """Plots all locations and starting positions of carriers as scatter plot."""

    fig, ax = plt.subplots(figsize=(14, 12))
    ax.scatter([loc.coordinates[0] for loc in locations.values()],
               [loc.coordinates[1] for loc in locations.values()],
               marker='.')

    for car in vehicles.values():
        x = float(car.loc.coordinates[0])
        y = float(car.loc.coordinates[1])
        ax.plot(x, y, marker='x', label=car.name)
    ax.legend()
    ax.xaxis.set_major_formatter(FuncFormatter(kms))
    ax.yaxis.set_major_formatter(FuncFormatter(kms))

    ax.set_title('Locations and starting points of carriers')

    return fig, ax


def plot_nr_jobs(vehicles: Dict[str, Carrier],
                 orders: Dict[str, Order]):
    """Plots number of completed jobs per carrier."""
    carrier_dict = {car: 0 for car in vehicles.keys()}
    for order in orders.values():
        carrier_dict[order.pick_carrier[0].name] += 1

    fig, ax = plt.subplots(figsize=(14, 7))
    ax.bar(*zip(*carrier_dict.items()))

    ax.set_xlabel('Carrier')
    ax.set_ylabel('Number of jobs')
    ax.set_title('Number of completed jobs per carrier')

    return fig, ax


def plot_distance(vehicles: Dict[str, Carrier]):
    """Plots total driving distance per carrier."""
    fig, ax = plt.subplots(figsize=(14, 7))
    ax.bar(vehicles.keys(), [car.travelled_distance() for car in vehicles.values()])

    ax.set_xlabel('Carrier')
    ax.set_ylabel('Distance travelled')
    ax.set_title('Distance travelled by carriers')

    ax.yaxis.set_major_formatter(FuncFormatter(kms))

    return fig, ax


def plot_work_percentage(vehicles: Dict[str, Carrier]):
    """Plots percentage of time carrier did something."""
    total_times = [(car.actions[-1].end_time - car.log_on_time).total_seconds() for car in vehicles.values()]
    durations = [car.pick_duration() + car.drop_duration() + car.drive_duration() for car in vehicles.values()]
    percentages = [100. * dur / total_time for (dur, total_time) in zip(durations, total_times)]

    fig, ax = plt.subplots(figsize=(14, 7))
    ax.bar(vehicles.keys(), percentages)

    ax.set_xlabel('Carrier')
    ax.set_ylabel('Percentage of time working')
    ax.set_title('Percentage of time carriers are working')

    return fig, ax


def plot_overlaps(vehicles: Dict[str, Carrier]):
    """Plot number of overlapping actions per carrier."""
    fig, ax = plt.subplots(figsize=(14, 7))
    ax.bar(vehicles.keys(), [car.big_overlaps for car in vehicles.values()], color='red', label='Overlap of >1s')
    ax.bar(vehicles.keys(), [car.overlaps for car in vehicles.values()],
           bottom=[car.big_overlaps for car in vehicles.values()], color='orange', label='Overlap of 1s')
    ax.set_xlabel('Carrier')
    ax.set_ylabel('Number of overlaps')
    ax.set_title('Number of action overlaps per carrier')
    ax.legend()

    return fig, ax


def plot_action_times(vehicles: Dict[str, Carrier]):
    """Plot times carrier spent on actions drive, drop, pick."""
    pick_durations = [car.pick_duration() for car in vehicles.values()]
    drop_durations = [car.drop_duration() for car in vehicles.values()]
    travel_durations = [car.drive_duration() for car in vehicles.values()]

    fig, ax = plt.subplots(figsize=(14, 7))

    ax.bar(vehicles.keys(), pick_durations, label='Pick', color='red')
    ax.bar(vehicles.keys(), drop_durations, label='Drop', color='blue', bottom=pick_durations)
    ax.bar(vehicles.keys(), travel_durations, label='Drive', color='green',
           bottom=[sum(x) for x in zip(pick_durations, drop_durations)])

    ax.set_xlabel('Carrier')
    ax.set_ylabel('Work time (s)')
    ax.set_title('Total working time of carriers')
    ax.legend()

    return fig, ax
