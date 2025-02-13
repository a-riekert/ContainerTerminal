from read_files import *
from structs import *
from plotting import *

locations, carriers, orders, test = read_data_to_dicts('data/VOSimu-InputInformation.xlsx')

locations, carriers, orders, infos = read_logs('data/logger_all.log', locations, carriers, orders)

# find out if any inconsistencies in log file were found.
if any([test,
        infos['capacity_exceeded'],
        infos['wrong_location'],
        infos['wrong_distance'],
        infos['incomplete_jobs']]):
    raise RuntimeWarning('Inconsistencies in data found.')

calculate_overlaps(carriers)
if check_consistency(carriers):
    raise RuntimeWarning('Some carrier actions were inconsistent.')

fig_jobs, _ = plot_nr_jobs(carriers, orders)

fig_work, _ = plot_work_percentage(carriers)

fig_dist, _ = plot_distance(carriers)

fig_times, _ = plot_action_times(carriers)

fig_overlaps, _ = plot_overlaps(carriers)

fig_locs, _ = plot_locs_and_vehicles(locations, carriers)
fig_locs_adjust, _ = plot_locs_and_vehicles(locations, carriers, adjust_labels=True)

fig_first_dist, _ = plot_first_distances(carriers)

fig_jobs.savefig('plots/plot_nr_jobs')
fig_work.savefig('plots/plot_work_percentage')
fig_dist.savefig('plots/plot_distances')
fig_times.savefig('plots/plot_action_times')
fig_overlaps.savefig('plots/plot_overlaps')
fig_locs.savefig('plots/plot_locs')
fig_locs_adjust.savefig('plots/plot_locs_adjust')
fig_first_dist.savefig('plots/plot_initial_distances')

plt.show()
