from structs import Carrier, Location, Order

import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from datetime import datetime


def plot_locs_and_vehicles(locations, vehicles):
    def kms(x, _):
        return f'{x * 1e-6:.1f}km'  # Converts to kilometres

    fig, ax = plt.subplots(figsize=(14, 12))
    ax.scatter([loc.coordinates[0] for loc in locations.values()],
               [loc.coordinates[1] for loc in locations.values()],
               marker='.')

    for car in vehicles.values():
        x = float(car.loc.coordinates[0])
        y = float(car.loc.coordinates[1])
        print(f'Start location of vehicle {car.name}: ({x}, {y}).')
        ax.plot(x, y, marker='x', label=car.name)
    ax.legend()
    ax.xaxis.set_major_formatter(FuncFormatter(kms))
    ax.yaxis.set_major_formatter(FuncFormatter(kms))

    ax.set_title('Locations and starting points of carriers')

    return fig, ax


def test(orders):
    test = 0
    os = []
    for index, row in orders.iterrows():
        if not row['TractorOrderId'] == 'TO_' + row['ContainerOrderId']:
            print(f'In row {index}, first and second entry are different.')
            test = 1
        if not row['TractorOrderId'] == 'TO_CO_' + row['ContainerName']:
            print(f'In row {index}, first and third entry are different.')
            test = 1
        os.append(int(row['ContainerName'][7:]))
        if index % 100 == 0:
            print(row['TractorOrderId'], row['ContainerOrderId'], row['ContainerName'])

    if test == 0:
        print('Test passed successfully.')
    print(sorted(os))
