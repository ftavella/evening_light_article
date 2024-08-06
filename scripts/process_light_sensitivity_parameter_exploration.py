import numpy as np
import pandas as pd

simulation_setup = np.load("..\data\light_sensitivity_parameter_exploration\light_sensitivity_parameter_exploration_simulation_setup.npz", allow_pickle=True)
light = simulation_setup["simulation_light"]
total_simulations = 5 * 5 * 5

# Calculate sleep time and number of switches
zone_of_interest = [22.0, 30.0] # hours
parameter_exploration = pd.DataFrame({})
for idx in range(total_simulations):
    # Load simulation data
    data = np.load(f'../data/light_sensitivity_parameter_exploration/light_sensitivity_parameter_exploration_{idx}.npz', allow_pickle=True)
    simulation = data['result_data'].item()
    parameters = simulation["parameters"]
    model = simulation["simulation_model"]
    trajectory = simulation["trajectory"]
    time = trajectory.time
    time_of_interest_mask = (time >= zone_of_interest[0]) & (time <= zone_of_interest[1])
    time_of_interest = time[time_of_interest_mask]
    sleep = model.sleep_state
    sleep_of_interest = sleep[time_of_interest_mask]
    # percentage of sleep equal to 1
    sleep_time_fraction = np.sum(sleep_of_interest) / len(sleep_of_interest)
    sleep_time = sleep_time_fraction * (zone_of_interest[1] - zone_of_interest[0])
    # number of switches
    number_of_switches = np.sum(np.abs(np.diff(sleep_of_interest)))
    # final state of the simulation
    final_state = trajectory.states[-1, :]
    result = pd.DataFrame({
        'p': parameters['p'],
        'k': parameters['k'],
        'tauc': parameters['tauc'],
        'sleep_time': sleep_time,
        'number_of_switches': number_of_switches,
        'x_f': final_state[0],
        'xc_f': final_state[1],
        'n_f': final_state[2],
        'H_f': final_state[3],
        'S_f': sleep[-1],
    }, index=[idx])
    parameter_exploration = pd.concat([parameter_exploration, result])

desired_number_of_switches = parameter_exploration['number_of_switches'] <= 2.0
selected_parameters = parameter_exploration[desired_number_of_switches]
print(selected_parameters)
# save selected parameters
selected_parameters.to_csv('../data/light_sensitivity_parameter_exploration/light_sensitivity_selected_parameters.csv')