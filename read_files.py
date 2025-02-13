from structs import *

import pandas as pd
from datetime import datetime
import math
import re


def read_data_to_dicts(file):
    """Saving data from Excel file in dictionaries containing locations, carriers and orders."""
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

    test = 0
    # testing if columns TractorOrderId, ContainerOrderId, ContainerName are the same up to first few characters
    # so these can be used interchangeably
    for index, row in orders.iterrows():
        if not row['TractorOrderId'] == 'TO_' + row['ContainerOrderId']:
            print(f'In row {index}, first and second entry are different.')
            test += 1
        if not row['TractorOrderId'] == 'TO_CO_' + row['ContainerName']:
            print(f'In row {index}, first and third entry are different.')
            test += 1

    return loc_dict, carrier_dict, order_dict, test


def read_logs(file_name, locations, carriers, orders):
    """Analyzing data from log file using regex."""

    # regular expression for line of the following form, which describes that carrier is working on a pick
    # 2024-11-14 10:27:10 INFO SC004 (TO: TO_CO_TFTU000001, CO: CO_TFTU000001, PICK) working at QC001; 60 s
    p_work_pick = re.compile(r'([\d :-]+) INFO ([A-Z\d]+) \(TO: ([A-Z\d_]+).*CO: ([A-Z\d_]+).*PICK\) working at (['
                             r'A-Z\d.]+); (\d+) s')

    # regular expression for line of the following form, which describes that carrier is working on a drop
    # 2024-11-14 10:29:22 INFO SC014 (TO: TO_CO_TFTU000005, CO: CO_TFTU000005, DROP) working at YARD001.59; 61 s
    p_work_drop = re.compile(r'([\d :-]+) INFO ([A-Z\d]+) \(TO: ([A-Z\d_]+).*CO: ([A-Z\d_]+).*DROP\) working at (['
                             r'A-Z\d.]+); (\d+) s')

    # regular expressions for lines of the following form, which describe that carrier is driving to a location
    # 2024-11-14 10:28:34 INFO SC019 (TO: TO_CO_TFTU000002, CO: CO_TFTU000002, DROP) driving to WS012.01; 106 s; 586343 mm
    # 2024-11-14 10:27:10 INFO SC001 (TO: TO_CO_TFTU000018, CO: CO_TFTU000018, PICK) driving to QC003; 31 s; 172693 mm
    p_drive_pick = re.compile(r'([\d :-]+) INFO ([A-Z\d]+) \(TO: ([A-Z\d_]+).*CO: ([A-Z\d_]+).*PICK\) driving to (['
                              r'A-Z\d.]+); (\d+) s; (\d+) mm')
    p_drive_drop = re.compile(r'([\d :-]+) INFO ([A-Z\d]+) \(TO: ([A-Z\d_]+).*CO: ([A-Z\d_]+).*DROP\) driving to (['
                              r'A-Z\d.]+); (\d+) s; (\d+) mm')

    # regular expression for line of the following form, which describes that carrier has finished a pick
    # 2024-11-14 10:28:07 INFO SC004 (TO: TO_CO_TFTU000001, CO: CO_TFTU000001, PICK) finished at QC001
    p_finish_pick = re.compile(r'([\d :-]+) INFO ([A-Z\d]+) \(TO: ([A-Z\d_]+).*CO: ([A-Z\d_]+).*PICK\) finished at (['
                               r'A-Z\d.]+)')

    # regular expression for line of the following form, which describes that carrier has finished a drop
    # 2024-11-14 10:30:22 INFO SC014 (TO: TO_CO_TFTU000005, CO: CO_TFTU000005, DROP) finished at YARD001.59
    p_finish_drop = re.compile(r'([\d :-]+) INFO ([A-Z\d]+) \(TO: ([A-Z\d_]+).*CO: ([A-Z\d_]+).*DROP\) finished at (['
                               r'A-Z\d.]+)')

    # regular expression for line of the following form, which describes that carrier is at certain position
    # 2024-11-14 10:28:07 DEBUG SC004 now at position (242320, 993371)
    p_pos = re.compile(r'([\d :-]+) DEBUG ([A-Z\d]+) now at position \((\d+), (\d+)\)')

    # regular expression for line of the following form, which describes when carrier logs on
    # 2024-11-14 10:26:30 INFO SC001 log on
    p_logon = re.compile(r'([\d :-]+) INFO ([A-Z\d]+) log on')

    capacity_exceeded = []
    wrong_location = []
    wrong_distance = []
    incomplete_jobs = []

    with open(file_name) as file:
        for line in file:
            # matches for each of the regular expressions
            m_work = p_work_pick.search(line)
            m_work2 = p_work_drop.search(line)
            m_drive = p_drive_pick.search(line)
            m_drive2 = p_drive_drop.search(line)
            m_finish = p_finish_pick.search(line)
            m_finish2 = p_finish_drop.search(line)
            m_pos = p_pos.search(line)
            m_logon = p_logon.search(line)

            if m_logon:
                start_time = datetime.fromisoformat(m_logon.group(1))
                car_name = m_logon.group(2)

                act = Action(carriers[car_name],
                             None,
                             carriers[car_name].loc,
                             carriers[car_name].loc,
                             start_time,
                             duration=0,
                             action_type='LOGON')

                carriers[car_name].actions.append(act)

            if m_pos:
                start_time = datetime.fromisoformat(m_pos.group(1))
                car_name = m_pos.group(2)
                loc_x = int(m_pos.group(3))
                loc_y = int(m_pos.group(4))

                if carriers[car_name].loc.coordinates != (loc_x, loc_y):
                    wrong_location.append(carriers[car_name].loc)
                # check that carrier was indeed at current position after last drive action

            if m_work:

                car_name = m_work.group(2)
                order_name = m_work.group(3)
                container_name = m_work.group(4)
                location_name = m_work.group(5)
                start_time = datetime.fromisoformat(m_work.group(1))
                work_time = int(m_work.group(6))

                carriers[car_name].orders.append(order_name)
                orders[container_name].pick_carrier.append(carriers[car_name])
                orders[container_name].pick_location.append(locations[location_name])
                act = Action(carrier=carriers[car_name],
                             order=orders[container_name],
                             origin=locations[location_name],
                             dest=locations[location_name],
                             start_time=start_time,
                             duration=work_time,
                             action_type='PICK')
                carriers[car_name].actions.append(act)
                locations[location_name].nr_carriers += 1

                if locations[location_name].nr_carriers > locations[location_name].capacity:
                    capacity_exceeded.append(act)
                # check if too many carriers are now at location

            if m_work2:
                car_name = m_work2.group(2)
                order_name = m_work2.group(3)
                container_name = m_work2.group(4)
                location_name = m_work2.group(5)
                start_time = datetime.fromisoformat(m_work2.group(1))
                work_time = int(m_work2.group(6))

                carriers[car_name].orders.append(order_name)
                orders[container_name].drop_carrier.append(carriers[car_name])
                orders[container_name].drop_location.append(locations[location_name])

                act = Action(carrier=carriers[car_name],
                             order=orders[container_name],
                             origin=locations[location_name],
                             dest=locations[location_name],
                             start_time=start_time,
                             duration=work_time,
                             action_type='DROP')
                carriers[car_name].actions.append(act)
                locations[location_name].nr_carriers += 1

                if locations[location_name].nr_carriers > locations[location_name].capacity:
                    capacity_exceeded.append(act)
                # check if too many carriers are now at location

            if m_drive:
                car_name = m_drive.group(2)
                order_name = m_drive.group(3)
                container_name = m_drive.group(4)
                location_name = m_drive.group(5)
                start_time = datetime.fromisoformat(m_drive.group(1))
                work_time = int(m_drive.group(6))
                distance = int(m_drive.group(7))

                act = Action(carrier=carriers[car_name],
                             order=orders[container_name],
                             origin=carriers[car_name].loc,
                             dest=locations[location_name],
                             start_time=start_time,
                             duration=work_time,
                             action_type='DRIVE_PICK')

                carriers[car_name].actions.append(act)
                if distance != act.origin.dist(act.dest):
                    wrong_distance.append(act)
                    # check that travelled distance is indeed the distance to the previous location

                carriers[car_name].loc = locations[location_name]

            if m_drive2:
                car_name = m_drive2.group(2)
                order_name = m_drive2.group(3)
                container_name = m_drive2.group(4)
                location_name = m_drive2.group(5)
                start_time = datetime.fromisoformat(m_drive2.group(1))
                work_time = int(m_drive2.group(6))
                distance = int(m_drive2.group(7))

                act = Action(carrier=carriers[car_name],
                             order=orders[container_name],
                             origin=carriers[car_name].loc,
                             dest=locations[location_name],
                             start_time=start_time,
                             duration=work_time,
                             action_type='DRIVE_DROP')

                carriers[car_name].actions.append(act)
                if distance != act.origin.dist(act.dest):
                    wrong_distance.append(act)
                # check that travelled distance is indeed the distance to the previous location

                carriers[car_name].loc = locations[location_name]

            if m_finish:
                car_name = m_finish.group(2)
                order_name = m_finish.group(3)
                container_name = m_finish.group(4)
                location_name = m_finish.group(5)
                start_time = datetime.fromisoformat(m_finish.group(1))

                act = Action(carrier=carriers[car_name],
                             order=orders[container_name],
                             origin=locations[location_name],
                             dest=locations[location_name],
                             start_time=start_time,
                             duration=0,
                             action_type='FINISH_PICK')
                carriers[car_name].actions.append(act)

                locations[location_name].nr_carriers -= 1

            if m_finish2:
                car_name = m_finish2.group(2)
                order_name = m_finish2.group(3)
                container_name = m_finish2.group(4)
                location_name = m_finish2.group(5)
                start_time = datetime.fromisoformat(m_finish2.group(1))

                act = Action(carrier=carriers[car_name],
                             order=orders[container_name],
                             origin=locations[location_name],
                             dest=locations[location_name],
                             start_time=start_time,
                             duration=0,
                             action_type='FINISH_DROP')
                carriers[car_name].actions.append(act)

                locations[location_name].nr_carriers -= 1

    for order in orders.values():
        # check that every order was completed by exactly 1 carrier
        if any([len(order.pick_carrier) != 1,
                len(order.drop_carrier) != 1,
                len(order.pick_location) != 1,
                len(order.drop_location) != 1,
                order.drop_carrier[0] != order.pick_carrier[0],
                order.pick_location[0] != order.origin,
                order.drop_location[0] != order.dest]):
            incomplete_jobs.append(order)

    info_dict = {'capacity_exceeded': capacity_exceeded,
                 'wrong_location': wrong_location,
                 'wrong_distance': wrong_distance,
                 'incomplete_jobs': incomplete_jobs}

    return locations, carriers, orders, info_dict
