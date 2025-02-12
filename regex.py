import re
from read_files import *
from structs import *

locations, carriers, orders = read_data_to_dicts('VOSimu-InputInformation.xlsx')

# 2024-11-14 10:27:10 INFO SC004 (TO: TO_CO_TFTU000001, CO: CO_TFTU000001, PICK) working at QC001; 60 s
p_work_pick = re.compile('([\d :-]+) INFO ([A-Z\d]+) \(TO: ([A-Z\d_]+).*CO: ([A-Z\d_]+).*PICK\) working at ([A-Z\d.]+); ([\d]+) s')

# 2024-11-14 10:29:22 INFO SC014 (TO: TO_CO_TFTU000005, CO: CO_TFTU000005, DROP) working at YARD001.59; 61 s
p_work_drop = re.compile('([\d :-]+) INFO ([A-Z\d]+) \(TO: ([A-Z\d_]+).*CO: ([A-Z\d_]+).*DROP\) working at ([A-Z\d.]+); ([\d]+) s')

# 2024-11-14 10:28:34 INFO SC019 (TO: TO_CO_TFTU000002, CO: CO_TFTU000002, DROP) driving to WS012.01; 106 s; 586343 mm
# 2024-11-14 10:27:10 INFO SC001 (TO: TO_CO_TFTU000018, CO: CO_TFTU000018, PICK) driving to QC003; 31 s; 172693 mm
p_drive_pick = re.compile('([\d :-]+) INFO ([A-Z\d]+) \(TO: ([A-Z\d_]+).*CO: ([A-Z\d_]+).*PICK\) driving to ([A-Z\d.]+); ([\d]+) s; ([\d]+) mm')
p_drive_drop = re.compile('([\d :-]+) INFO ([A-Z\d]+) \(TO: ([A-Z\d_]+).*CO: ([A-Z\d_]+).*DROP\) driving to ([A-Z\d.]+); ([\d]+) s; ([\d]+) mm')

# 2024-11-14 10:28:07 INFO SC004 (TO: TO_CO_TFTU000001, CO: CO_TFTU000001, PICK) finished at QC001
p_finish_pick = re.compile('([\d :-]+) INFO ([A-Z\d]+) \(TO: ([A-Z\d_]+).*CO: ([A-Z\d_]+).*PICK\) finished at ([A-Z\d.]+)')
# 2024-11-14 10:30:22 INFO SC014 (TO: TO_CO_TFTU000005, CO: CO_TFTU000005, DROP) finished at YARD001.59
p_finish_drop = re.compile('([\d :-]+) INFO ([A-Z\d]+) \(TO: ([A-Z\d_]+).*CO: ([A-Z\d_]+).*DROP\) finished at ([A-Z\d.]+)')

# 2024-11-14 10:28:07 DEBUG SC004 now at position (242320, 993371)
p_pos = re.compile('([\d :-]+) DEBUG ([A-Z\d]+) now at position \(([\d]+), ([\d]+)\)')

# 2024-11-14 10:26:30 INFO SC001 log on
p_logon = re.compile('([\d :-]+) INFO ([A-Z\d]+) log on')

capacity_exceeded = 0

with open('logger_all.log') as file:
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

            assert carriers[car_name].loc.coordinates == (loc_x, loc_y)
            # check that carrier was indeed at current position after last drive action

        if m_work:

            car_name = m_work.group(2)
            order_name = m_work.group(3)
            container_name = m_work.group(4)
            location_name = m_work.group(5)
            start_time = datetime.fromisoformat(m_work.group(1))
            work_time = int(m_work.group(6))

            print('Carrier:', car_name)
            print('Order:', order_name)
            print('Container:', container_name)
            print('Location:', location_name)
            print('Start time:', start_time)
            print('Working time in seconds:', work_time)

            carriers[car_name].orders.append(order_name)
            orders[container_name].pick_carrier.append(carriers[car_name])
            orders[container_name].pick_location.append(locations[location_name])
            carriers[car_name].actions.append(Action(locations[location_name], locations[location_name], start_time,
                                                            work_time, 'PICK'))
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

            print('Carrier:', car_name)
            print('Order:', order_name)
            print('Container:', container_name)
            print('Location:', location_name)
            print('Start time:', start_time)
            print('Working time in seconds:', work_time)
            carriers[car_name].orders.append(order_name)
            orders[container_name].drop_carrier.append(carriers[car_name])
            orders[container_name].drop_location.append(locations[location_name])
            carriers[car_name].actions.append(Action(locations[location_name], locations[location_name], start_time,
                                                            work_time, 'DROP'))
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

            print('Carrier:', car_name)
            print('Order:', order_name)
            print('Location:', location_name)
            print('Working time in seconds:', work_time)
            print('Distance in mm:', distance)
            print('Start time:', start_time)

            act = Action(carriers[car_name].loc, locations[location_name], start_time, work_time, 'DRIVE_PICK')

            carriers[car_name].actions.append(act)
            assert distance == act.origin.dist(act.dest)
            carriers[car_name].loc = locations[location_name]

        if m_drive2:
            car_name = m_drive2.group(2)
            order_name = m_drive2.group(3)
            container_name = m_drive2.group(4)
            location_name = m_drive2.group(5)
            start_time = datetime.fromisoformat(m_drive2.group(1))
            work_time = int(m_drive2.group(6))
            distance = int(m_drive2.group(7))

            print('Carrier:', car_name)
            print('Order:', order_name)
            print('Location:', location_name)
            print('Working time in seconds:', work_time)
            print('Distance in mm:', distance)
            print('Start time:', start_time)

            act = Action(carriers[car_name].loc, locations[location_name], start_time, work_time, 'DRIVE_DROP')

            carriers[car_name].actions.append(act)
            assert distance == act.origin.dist(act.dest)
            carriers[car_name].loc = locations[location_name]

        if m_finish:
            locations[m_finish.group(5)].nr_carriers -= 1

        if m_finish2:
            locations[m_finish2.group(5)].nr_carriers -= 1


print('Number of orders:', len(orders))
for ord in orders.values():
    assert len(ord.pick_carrier) == 1
    assert len(ord.drop_carrier) == 1
    assert len(ord.pick_location) == 1
    assert len(ord.drop_location) == 1

    assert ord.drop_carrier[0] == ord.pick_carrier[0]
    assert ord.pick_location[0] == ord.origin
    assert ord.drop_location[0] == ord.dest


def kms(x, pos):
    return f'{x * 1e-6:.1f}km'  # Converts to kilometres

fig, ax = plt.subplots(figsize=(14, 14))

for i, act in enumerate(carriers['SC001'].actions):
    ax.plot(*act.origin.coordinates, marker='x')
    ax.annotate(f'Action {i+1}', act.origin.coordinates)
    print('Start:', act.origin.name, 'End:', act.dest.name, 'Start time:', act.start_time, 'End time:', act.end_time, 'Distance:', act.dist)
ax.set_title('Actions of carrier SC001')
fig2, ax2 = plt.subplots(figsize=(14, 7))
fig3, ax3 = plt.subplots(figsize=(14, 7))
fig4, ax4 = plt.subplots(figsize=(14, 7))

for i, car in enumerate(carriers.values()):
    dur = timedelta(0)
    pick_dur = 0
    drop_dur = 0
    drive_dur = 0
    dist = 0
    total_time = car.actions[-1].end_time - car.log_on_time
    for act in car.actions:
        dur += act.duration
        dist += act.origin.dist(act.dest)
        if act.type == 'PICK':
            pick_dur += act.duration.total_seconds()
        elif act.type == 'DROP':
            drop_dur += act.duration.total_seconds()
        else:
            drive_dur += act.duration.total_seconds()
    percentage = 100. * dur.total_seconds() / total_time.total_seconds()
    print(f'Number of actions of carrier {car.name}: {len(car.actions)}, total working time: {dur}, time logged on: {total_time}, utilization: {percentage:.2f}%.')
    ax2.bar(car.name, percentage)
    ax3.bar(car.name, dist)
    if i == 0:
        ax4.bar(car.name, pick_dur, label='Pick', color='red')
        ax4.bar(car.name, drop_dur, label='Drop', bottom=pick_dur, color='blue')
        ax4.bar(car.name, drive_dur, label='Drive', bottom=drop_dur+pick_dur, color='green')
    else:
        ax4.bar(car.name, pick_dur, color='red')
        ax4.bar(car.name, drop_dur, bottom=pick_dur, color='blue')
        ax4.bar(car.name, drive_dur, bottom=drop_dur + pick_dur, color='green')
    for i, act in enumerate(car.actions[:-1]):
        next_act = car.actions[i+1]
        if not act.end_time <= next_act.start_time + timedelta(seconds=1):
            print(f'Carrier name: {car.name}, end of action: {act.end_time}, start of next action: {next_act.start_time}')
        if next_act.type == 'DROP':
            assert act.type == 'DRIVE_DROP'
        if next_act.type == 'PICK':
            assert act.type == 'DRIVE_PICK'
        if next_act.type == 'DRIVE_DROP':
            assert act.type == 'PICK'
        if next_act.type == 'DRIVE_PICK':
            assert act.type == 'DROP'

ax2.set_xlabel('Carrier')
ax2.set_ylabel('Percentage of time working')
ax2.set_title('Work load of carriers')

ax3.set_xlabel('Carrier')
ax3.set_ylabel('Distance travelled')
ax3.set_title('Distance travelled by carriers')

ax4.set_xlabel('Carrier')
ax4.set_ylabel('Work time (s)')
ax4.set_title('Total working time of carriers')

ax3.yaxis.set_major_formatter(FuncFormatter(kms))

ax.xaxis.set_major_formatter(FuncFormatter(kms))
ax.yaxis.set_major_formatter(FuncFormatter(kms))
plt.legend()
plt.show()