from structs import *

import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

try:
    from adjustText import adjust_text  # Import the library
except ImportError:
    print('adjustText not installed.')


def kms(x, _):
    """Converts millimeters to kilometres for axis formatting."""
    return f'{x * 1e-6:.1f}km'


def plot_locs_and_vehicles(locations: Dict[str, Location],
                           vehicles: Dict[str, Carrier],
                           adjust_labels: bool = False):
    """Plots all locations and starting positions of carriers as scatter plot."""

    fig, ax = plt.subplots(figsize=(14, 12))
    ax.scatter([loc.coordinates[0] for loc in locations.values()],
               [loc.coordinates[1] for loc in locations.values()],
               marker='.', label='Locations')
    texts = []
    for car in vehicles.values():
        x = float(car.loc.coordinates[0])
        y = float(car.loc.coordinates[1])
        if adjust_labels:
            ax.plot(x, y, marker='x')
            texts.append(plt.text(x, y, car.name, fontsize=12))
        else:
            ax.plot(x, y, marker='x', label=car.name)

    if adjust_labels:  # automatically put carrier names in positions where they do not overlap
        adjust_text(texts, ax=ax, expand=(1.4, 1.4), force_text=(0.15, 0.25),
                    arrowprops=dict(arrowstyle="-", color='black', lw=0.5))

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
    """Plots total driving distance to pick/drop locations per carrier."""
    fig, ax = plt.subplots(figsize=(14, 7))
    ax.bar(vehicles.keys(), [car.travelled_distance_pick() for car in vehicles.values()],
           label='Drive to pick', color='b')
    ax.bar(vehicles.keys(), [car.travelled_distance_drop() for car in vehicles.values()],
           bottom=[car.travelled_distance_pick() for car in vehicles.values()],
           label='Drive to drop', color='g')

    ax.set_xlabel('Carrier')
    ax.set_ylabel('Distance travelled')
    ax.set_title('Distance travelled by carriers')
    ax.legend()
    ax.yaxis.set_major_formatter(FuncFormatter(kms))

    return fig, ax


def plot_work_percentage(vehicles: Dict[str, Carrier]):
    """Plots percentage of time carrier did something."""
    total_times = [(car.actions[-1].end_time - car.actions[0].start_time).total_seconds() for car in vehicles.values()]
    durations = [car.pick_duration() + car.drop_duration() + car.drive_pick_duration() + car.drive_drop_duration()
                 for car in vehicles.values()]
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
    ax.bar(vehicles.keys(), [car.big_overlaps for car in vehicles.values()], color='r', label='Overlap of >1s')
    ax.bar(vehicles.keys(), [car.overlaps for car in vehicles.values()],
           bottom=[car.big_overlaps for car in vehicles.values()], color='y', label='Overlap of 1s')
    ax.set_xlabel('Carrier')
    ax.set_ylabel('Number of overlaps')
    ax.set_title('Number of action overlaps per carrier')
    ax.legend()

    return fig, ax


def plot_action_times(vehicles: Dict[str, Carrier]):
    """Plot times carrier spent on actions drive, drop, pick."""
    pick_durations = [car.pick_duration() for car in vehicles.values()]
    drop_durations = [car.drop_duration() for car in vehicles.values()]
    travel_pick_durations = [car.drive_pick_duration() for car in vehicles.values()]
    travel_drop_durations = [car.drive_drop_duration() for car in vehicles.values()]

    fig, ax = plt.subplots(figsize=(14, 7))

    ax.bar(vehicles.keys(), pick_durations, label='Pick', color='dodgerblue')
    ax.bar(vehicles.keys(), drop_durations, label='Drop', color='limegreen', bottom=pick_durations)
    ax.bar(vehicles.keys(), travel_pick_durations, label='Drive to pick', color='darkblue',
           bottom=[sum(x) for x in zip(pick_durations, drop_durations)])
    ax.bar(vehicles.keys(), travel_drop_durations, label='Drive to drop', color='darkgreen',
           bottom=[sum(x) for x in zip(pick_durations, drop_durations, travel_pick_durations)])

    ax.set_xlabel('Carrier')
    ax.set_ylabel('Work time (s)')
    ax.set_title('Total working time of carriers')
    ax.legend()

    return fig, ax


def plot_first_distances(vehicles: Dict[str, Carrier]):
    """Plot distance carrier travelled from initial location to first action."""
    fig, ax = plt.subplots(figsize=(14, 7))
    distances = [car.actions[1].dist() for car in vehicles.values()]

    ax.bar(vehicles.keys(), distances)

    ax.set_xlabel('Carrier')
    ax.set_ylabel('Distance for first action')
    ax.set_title('Distance travelled for first job')
    ax.yaxis.set_major_formatter(FuncFormatter(kms))

    return fig, ax
