from read_files import *
from structs import *
from plotting import *

locations, carriers, orders = read_data_to_dicts('VOSimu-InputInformation.xlsx')

locations, carriers, orders, errors = read_logs('logger_all.log', locations, carriers, orders)

# print total number of orders and number of things that went wrong (should all be 0)
print('Number of orders:', errors['nr_orders'])
print('Number of times capacity was exceeded:', errors['capacity_exceeded'])
print('Number of times position information was wrong:', errors['wrong_location'])
print('Number of times distance information was wrong:', errors['wrong_distance'])
print('Number of incomplete/failed jobs:', errors['incomplete_jobs'])

calculate_overlaps(carriers)
check_consistency(carriers)

fig1, ax1 = plot_nr_jobs(carriers, orders)

fig2, ax2 = plot_work_percentage(carriers)

fig3, ax3 = plot_distance(carriers)

fig4, ax4 = plot_action_times(carriers)

fig5, ax5 = plot_overlaps(carriers)

fig6, ax6 = plot_locs_and_vehicles(locations, carriers)

fig1.savefig('plot_nr_jobs')
fig2.savefig('plot_work_percentage')
fig3.savefig('plot_distances')
fig4.savefig('plot_action_times')
fig5.savefig('plot_overlaps')
fig6.savefig('plot_locs')

plt.show()
