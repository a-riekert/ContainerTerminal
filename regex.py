import re
from read_files import *
from structs import *
from plotting import plot_locs_and_vehicles

locations, carriers, orders = read_data_to_dicts('VOSimu-InputInformation.xlsx')

locations, carriers, orders, errors = read_logs('logger_all.log', locations, carriers, orders)

print('Number of orders:', errors['nr_orders'])
print('Number of times capacity was exceeded:', errors['capacity_exceeded'])
print('Number of times position information was wrong:', errors['wrong_location'])
print('Number of times distance information was wrong:', errors['wrong_distance'])
print('Number of incomplete/failed jobs:', errors['incomplete_jobs'])


def kms(x, _):
    return f'{x * 1e-6:.1f}km'  # Converts to kilometres


fig, ax = plt.subplots(figsize=(14, 14))

for i, act in enumerate(carriers['SC001'].actions):
    ax.plot(*act.origin.coordinates, marker='x')
    ax.annotate(f'Action {i + 1}', act.origin.coordinates)
    # print('Start:', act.origin.name, 'End:', act.dest.name, 'Start time:', act.start_time, 'End time:', act.end_time, 'Distance:', act.dist)

ax.set_title('Actions of carrier SC001')
fig1, ax1 = plt.subplots(figsize=(14, 7))
fig2, ax2 = plt.subplots(figsize=(14, 7))
fig3, ax3 = plt.subplots(figsize=(14, 7))
fig4, ax4 = plt.subplots(figsize=(14, 7))
fig5, ax5 = plt.subplots(figsize=(14, 7))

time_overlaps = 0
big_time_overlaps = 0

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

    ax1.bar(car.name, len(car.actions))
    ax2.bar(car.name, percentage)
    ax3.bar(car.name, dist)
    if i == 0:
        ax4.bar(car.name, pick_dur, label='Pick', color='red')
        ax4.bar(car.name, drop_dur, label='Drop', bottom=pick_dur, color='blue')
        ax4.bar(car.name, drive_dur, label='Drive', bottom=drop_dur + pick_dur, color='green')
    else:
        ax4.bar(car.name, pick_dur, color='red')
        ax4.bar(car.name, drop_dur, bottom=pick_dur, color='blue')
        ax4.bar(car.name, drive_dur, bottom=drop_dur + pick_dur, color='green')
    for i, act in enumerate(car.actions[:-1]):
        next_act = car.actions[i + 1]
        if act.end_time > next_act.start_time + timedelta(seconds=1):
            car.big_overlaps += 1
        elif act.end_time > next_act.start_time:
            car.overlaps += 1

        if next_act.type == 'DROP':
            assert act.type == 'DRIVE_DROP' and act.order == next_act.order
        if next_act.type == 'PICK':
            assert act.type == 'DRIVE_PICK' and act.order == next_act.order
        if next_act.type == 'DRIVE_DROP':
            assert act.type == 'PICK' and act.order == next_act.order
        if next_act.type == 'DRIVE_PICK':
            assert act.type == 'DROP'


ax1.set_xlabel('Carrier')
ax1.set_ylabel('Number of actions')
ax1.set_title('Number of actions per carrier')

ax2.set_xlabel('Carrier')
ax2.set_ylabel('Percentage of time working')
ax2.set_title('Work load of carriers')

ax3.set_xlabel('Carrier')
ax3.set_ylabel('Distance travelled')
ax3.set_title('Distance travelled by carriers')

ax4.set_xlabel('Carrier')
ax4.set_ylabel('Work time (s)')
ax4.set_title('Total working time of carriers')
ax4.legend()


ax5.bar([car.name for car in carriers.values()], [car.big_overlaps for car in carriers.values()], color='red', label='Overlap of >1s')
ax5.bar([car.name for car in carriers.values()], [car.overlaps for car in carriers.values()], bottom=[car.big_overlaps for car in carriers.values()], color='orange', label='Overlap of 1s')
ax5.set_xlabel('Carrier')
ax5.set_ylabel('Number of overlaps')
ax5.set_title('Number of action overlaps per carrier')
ax5.legend()

ax3.yaxis.set_major_formatter(FuncFormatter(kms))

ax.xaxis.set_major_formatter(FuncFormatter(kms))
ax.yaxis.set_major_formatter(FuncFormatter(kms))

fig6, ax6 = plot_locs_and_vehicles(locations, carriers)
fig5.savefig('plot_overlaps')
fig6.savefig('plot_locs')
#.legend()
plt.show()
