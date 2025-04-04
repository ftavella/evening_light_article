import numpy as np
import pandas as pd
from tqdm import tqdm
from circadian.models import Skeldon23
from circadian.lights import LightSchedule

def circadian_modulation_of_sleep(model, trajectory):
    x = trajectory.states[:, 0]
    xc = trajectory.states[:, 1]
    linear_term = model.c20 + model.alpha21 * xc + model.alpha22 * x
    quadratic_term = model.beta21 * xc * xc + model.beta22 * xc * x + model.beta23 * x * x
    C = linear_term + quadratic_term
    return C

def H_thresholds(model, trajectory):
    C = circadian_modulation_of_sleep(model, trajectory)
    H_plus = model.H0 + 0.5 * model.Delta + model.ca * C
    H_minus = model.H0 - 0.5 * model.Delta + model.ca * C 
    return H_plus, H_minus

# load selected parameter sets and simulation setup
selected_parameters = pd.read_csv('../data/light_sensitivity_parameter_exploration/light_sensitivity_selected_parameters.csv', index_col=0)
simulation_setup = np.load("../data/light_sensitivity_parameter_exploration/light_sensitivity_parameter_exploration_simulation_setup.npz", allow_pickle=True)

mu = 19.0
delta = 6.0
chi = 11.0

dt = 0.005 # hours
days = 14.0
time = np.arange(0, days * 24.0, dt)
typical_indoor_lux = simulation_setup['typical_indoor_lux'].item()
lights_on = simulation_setup['lights_on'].item()
lights_off = simulation_setup['lights_off'].item()
forced_wakeup_threshold = simulation_setup['forced_wakeup_threshold'].item()

light_data_location = '../data/light_schedules/'
light_schedule_time = np.load(light_data_location + 'time.npy')
regular_light = np.load(light_data_location + 'regular_light.npy')
ebook_first_light = np.load(light_data_location + 'chang14_ebook_first_light.npy')
ebook_second_light = np.load(light_data_location + 'chang14_ebook_second_light.npy')

for idx in tqdm(selected_parameters.index, desc='Simulating', total=len(selected_parameters)):
    # Parameters
    p = selected_parameters.loc[idx, 'p']
    k = selected_parameters.loc[idx, 'k']
    tauc = selected_parameters.loc[idx, 'tauc']
    # Initial condition
    initial_condition = np.array([
        selected_parameters.loc[idx, 'x_f'],
        selected_parameters.loc[idx, 'xc_f'],
        selected_parameters.loc[idx, 'n_f'],
        selected_parameters.loc[idx, 'H_f'],
    ])
    S0 = selected_parameters.loc[idx, 'S_f']
    parameters = {
        'S0': S0,
        'mu': mu, 'Delta': delta, 'chi': chi,
        'p': p, 'k': k, 'tauc': tauc,
        'forced_wakeup_light_threshold': forced_wakeup_threshold,
    }
    # Regular simulation
    regular_model = Skeldon23(params=parameters)
    regular_trajectory = regular_model.integrate(time, 
                                                 initial_condition=initial_condition,
                                                 input=regular_light)
    regular_H_plus, regular_H_minus = H_thresholds(regular_model, regular_trajectory)
    # Ebook first simulation
    ebook_first_model = Skeldon23(params=parameters)
    ebook_first_trajectory = ebook_first_model.integrate(time, 
                                                         initial_condition=initial_condition,
                                                         input=ebook_first_light)
    ebook_first_H_plus, ebook_first_H_minus = H_thresholds(ebook_first_model, ebook_first_trajectory)
    # Ebook second simulation
    ebook_second_model = Skeldon23(params=parameters)
    ebook_second_trajectory = ebook_second_model.integrate(time, 
                                                          initial_condition=initial_condition,
                                                          input=ebook_second_light)
    ebook_second_H_plus, ebook_second_H_minus = H_thresholds(ebook_second_model, ebook_second_trajectory)
    # Save data
    np.savez(f"../data/light_sensitivity_chang14/light_sensitivity_chang14_simulation_{idx}.npz",
             time=time,
             parameters=parameters,
             initial_condition=initial_condition,
             regular_trajectory_states=regular_trajectory.states,
             regular_light=regular_light,
             regular_sleep=regular_model.sleep_state,
             regular_H_plus=regular_H_plus,
             regular_H_minus=regular_H_minus,
             ebook_first_trajectory_states=ebook_first_trajectory.states,
             ebook_first_light=ebook_first_light,
             ebook_first_sleep=ebook_first_model.sleep_state,
             ebook_first_H_plus=ebook_first_H_plus,
             ebook_first_H_minus=ebook_first_H_minus,
             ebook_second_trajectory_states=ebook_second_trajectory.states,
             ebook_second_light=ebook_second_light,
             ebook_second_sleep=ebook_second_model.sleep_state,
             ebook_second_H_plus=ebook_second_H_plus,
             ebook_second_H_minus=ebook_second_H_minus,
    )