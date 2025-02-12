from structs import *

import pandas as pd
from datetime import datetime
import math
import re


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


def read_logs(file_name, locations, carriers, orders):
    # 2024-11-14 10:27:10 INFO SC004 (TO: TO_CO_TFTU000001, CO: CO_TFTU000001, PICK) working at QC001; 60 s
    p_work_pick = re.compile(
        '([\d :-]+) INFO ([A-Z\d]+) \(TO: ([A-Z\d_]+).*CO: ([A-Z\d_]+).*PICK\) working at ([A-Z\d.]+); ([\d]+) s')

    # 2024-11-14 10:29:22 INFO SC014 (TO: TO_CO_TFTU000005, CO: CO_TFTU000005, DROP) working at YARD001.59; 61 s
    p_work_drop = re.compile(
        '([\d :-]+) INFO ([A-Z\d]+) \(TO: ([A-Z\d_]+).*CO: ([A-Z\d_]+).*DROP\) working at ([A-Z\d.]+); ([\d]+) s')

    # 2024-11-14 10:28:34 INFO SC019 (TO: TO_CO_TFTU000002, CO: CO_TFTU000002, DROP) driving to WS012.01; 106 s; 586343 mm
    # 2024-11-14 10:27:10 INFO SC001 (TO: TO_CO_TFTU000018, CO: CO_TFTU000018, PICK) driving to QC003; 31 s; 172693 mm
    p_drive_pick = re.compile(
        '([\d :-]+) INFO ([A-Z\d]+) \(TO: ([A-Z\d_]+).*CO: ([A-Z\d_]+).*PICK\) driving to ([A-Z\d.]+); ([\d]+) s; ([\d]+) mm')
    p_drive_drop = re.compile(
        '([\d :-]+) INFO ([A-Z\d]+) \(TO: ([A-Z\d_]+).*CO: ([A-Z\d_]+).*DROP\) driving to ([A-Z\d.]+); ([\d]+) s; ([\d]+) mm')

    # 2024-11-14 10:28:07 INFO SC004 (TO: TO_CO_TFTU000001, CO: CO_TFTU000001, PICK) finished at QC001
    p_finish_pick = re.compile(
        '([\d :-]+) INFO ([A-Z\d]+) \(TO: ([A-Z\d_]+).*CO: ([A-Z\d_]+).*PICK\) finished at ([A-Z\d.]+)')
    # 2024-11-14 10:30:22 INFO SC014 (TO: TO_CO_TFTU000005, CO: CO_TFTU000005, DROP) finished at YARD001.59
    p_finish_drop = re.compile(
        '([\d :-]+) INFO ([A-Z\d]+) \(TO: ([A-Z\d_]+).*CO: ([A-Z\d_]+).*DROP\) finished at ([A-Z\d.]+)')

    # 2024-11-14 10:28:07 DEBUG SC004 now at position (242320, 993371)
    p_pos = re.compile('([\d :-]+) DEBUG ([A-Z\d]+) now at position \(([\d]+), ([\d]+)\)')

    # 2024-11-14 10:26:30 INFO SC001 log on
    p_logon = re.compile('([\d :-]+) INFO ([A-Z\d]+) log on')

    capacity_exceeded = 0
    wrong_location = 0
    wrong_distance = 0
    incomplete_jobs = 0

    with open(file_name) as file:
        for line in file:
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

                carriers[car_name].log_on_time = start_time

            if m_pos:
                start_time = datetime.fromisoformat(m_pos.group(1))
                car_name = m_pos.group(2)
                loc_x = int(m_pos.group(3))
                loc_y = int(m_pos.group(4))

                if carriers[car_name].loc.coordinates != (loc_x, loc_y):
                    wrong_location += 1
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
                carriers[car_name].actions.append(Action(order=orders[container_name],
                                                         origin=locations[location_name],
                                                         dest=locations[location_name],
                                                         start_time=start_time,
                                                         duration=work_time,
                                                         action_type='PICK'))
                locations[location_name].nr_carriers += 1

                if locations[location_name].nr_carriers > locations[location_name].capacity:
                    capacity_exceeded += 1

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
                carriers[car_name].actions.append(Action(order=orders[container_name],
                                                         origin=locations[location_name],
                                                         dest=locations[location_name],
                                                         start_time=start_time,
                                                         duration=work_time,
                                                         action_type='DROP'))
                locations[location_name].nr_carriers += 1

                if locations[location_name].nr_carriers > locations[location_name].capacity:
                    capacity_exceeded += 1

            if m_drive:
                car_name = m_drive.group(2)
                order_name = m_drive.group(3)
                container_name = m_drive.group(4)
                location_name = m_drive.group(5)
                start_time = datetime.fromisoformat(m_drive.group(1))
                work_time = int(m_drive.group(6))
                distance = int(m_drive.group(7))

                act = Action(order=orders[container_name],
                             origin=carriers[car_name].loc,
                             dest=locations[location_name],
                             start_time=start_time,
                             duration=work_time,
                             action_type='DRIVE_PICK')

                carriers[car_name].actions.append(act)
                if distance != act.origin.dist(act.dest):
                    wrong_distance += 1

                carriers[car_name].loc = locations[location_name]

            if m_drive2:
                car_name = m_drive2.group(2)
                order_name = m_drive2.group(3)
                container_name = m_drive2.group(4)
                location_name = m_drive2.group(5)
                start_time = datetime.fromisoformat(m_drive2.group(1))
                work_time = int(m_drive2.group(6))
                distance = int(m_drive2.group(7))

                act = Action(order=orders[container_name],
                             origin=carriers[car_name].loc,
                             dest=locations[location_name],
                             start_time=start_time,
                             duration=work_time,
                             action_type='DRIVE_DROP')

                carriers[car_name].actions.append(act)
                if distance != act.origin.dist(act.dest):
                    wrong_distance += 1

                carriers[car_name].loc = locations[location_name]

            if m_finish:
                locations[m_finish.group(5)].nr_carriers -= 1

            if m_finish2:
                locations[m_finish2.group(5)].nr_carriers -= 1

    for order in orders.values():
        if any([len(order.pick_carrier) != 1,
                len(order.drop_carrier) != 1,
                len(order.pick_location) != 1,
                len(order.drop_location) != 1,
                order.drop_carrier[0] != order.pick_carrier[0],
                order.pick_location[0] != order.origin,
                order.drop_location[0] != order.dest]):
            incomplete_jobs += 1

    error_dict = {'nr_orders': len(orders),
                  'capacity_exceeded': capacity_exceeded,
                  'wrong_location': wrong_location,
                  'wrong_distance': wrong_distance,
                  'incomplete_jobs': incomplete_jobs}

    return locations, carriers, orders, error_dict
