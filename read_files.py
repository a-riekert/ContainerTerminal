from structs import *

import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from datetime import datetime
import math

def read_data_to_dicts(file):
    data = pd.read_excel(file, [0, 1, 2])

    locations = data[0]
    vehicles = data[1]
    orders = data[2]

    loc_dict = dict()
    for index, row in locations.iterrows():
        name = str(row['Location Name']).strip()
        x = int(row['X-Coordinate [mm]'])
        y = int(row['Y-Coordinate [mm]'])
        try:
            cap = int(row['Capacity limitation (# SC)'])
        except ValueError:
            cap = math.inf

        loc_dict[name] = Location(name, (x, y), cap)

    carrier_dict = dict()
    for index, row in vehicles.iterrows():
        name = str(row['ID']).strip()
        loc = str(row['StartLocation']).strip()

        carrier_dict[name] = Carrier(name, loc_dict[loc])

    order_dict = dict()
    for index, row in orders.iterrows():
        name = str(row['ContainerOrderId']).strip()
        orig = str(row['OriginLocation']).strip()
        dest = str(row['DestinationLocation']).strip()
        first_time = datetime.fromisoformat(str(row['Time first known']))

        order_dict[name] = Order(name, loc_dict[orig], loc_dict[dest], first_time)

    return loc_dict, carrier_dict, order_dict

