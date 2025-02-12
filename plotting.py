
from structs import Carrier, Location, Order

import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from datetime import datetime

data = pd.read_excel('VOSimu-InputInformation.xlsx', [0, 1, 2])

counter = 0
lengths = []
with open('logger_all.log') as file:
    for line in file:
        counter += 1
        if counter % 1000 == 0:
            print(line)
        lengths.append(len(line))
print('Number of lines:', counter)
print('Maximal, minimal line length:', max(lengths), min(lengths))
#plt.hist(lengths, bins=20)
#plt.show()

locations = data[0]
vehicles = data[1]
orders = data[2]

loc_dict = dict()
for index, row in locations.iterrows():
    name = row['Location Name']
    x = row['X-Coordinate [mm]']
    y = row['Y-Coordinate [mm]']
    cap = row['Capacity limitation (# SC)']

    loc_dict[name] = Location(name, (x, y), cap)

carrier_dict = dict()
for index, row in vehicles.iterrows():
    name = row['ID']
    loc = row['StartLocation']

    carrier_dict[name] = Carrier(name, loc_dict[loc])

order_dict = dict()
for index, row in orders.iterrows():
    name = row['ContainerName']
    orig = row['OriginLocation']
    dest = row['DestinationLocation']
    first_time = datetime.fromisoformat(row['Time first known'])

    order_dict[name] = Order(name, loc_dict[orig], loc_dict[dest], first_time)

print(carrier_dict)

print(loc_dict)

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


def kms(x, pos):
    return f'{x * 1e-6:.1f}km'  # Converts to kilometres


loc_x = locations['X-Coordinate [mm]']
loc_y = locations['Y-Coordinate [mm]']

fig, ax = plt.subplots(figsize=(14, 14))
ax.scatter(loc_x, loc_y, marker='.')

vehicle_names = vehicles['ID']
vehicle_locs = vehicles['StartLocation']

for n, l in zip(vehicle_names, vehicle_locs):
    row = locations.loc[(locations['Location Name'] == l)]
    x = float(row['X-Coordinate [mm]'].iloc[0])
    y = float(row['Y-Coordinate [mm]'].iloc[0])
    print(f'Start location of vehicle {n}: ({x}, {y}).')
    ax.plot(x, y, marker='x', label=n)
plt.legend()
ax.xaxis.set_major_formatter(FuncFormatter(kms))
ax.yaxis.set_major_formatter(FuncFormatter(kms))
plt.show()