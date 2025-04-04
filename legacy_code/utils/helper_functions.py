import numpy as np
from circadian.models import DynamicalTrajectory, Skeldon23


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

def calculate_sleep_onset(time, data, simulation_condition):
    # Ignore the last day
    sleep = data[f'{simulation_condition}_sleep']
    sleep_onset_idx = np.where(np.diff(sleep) == 1)[0]
    sleep_onset_time = time[sleep_onset_idx][:-1]
    return sleep_onset_time

def calculate_cbtmin(time, data, simulation_condition):
    # Ignore the last day
    trajectory = DynamicalTrajectory(time, data[f'{simulation_condition}_trajectory_states'])
    cbtmin = Skeldon23().cbt(trajectory)[:-1]
    return cbtmin

def calculate_sleep_duration(time, data, simulation_condition, light_condition='early_light'):
    sleep = data[f'{simulation_condition}_sleep']
    if light_condition == 'early_light':
        sleep_onset_idx = np.where(np.diff(sleep) == 1)[0][:-1] # Ignore the last onset
        sleep_offset_idx = np.where(np.diff(sleep) == -1)[0][1:] # Ignore the first offset
    elif light_condition == 'late_light':
        sleep_onset_idx = np.where(np.diff(sleep) == 1)[0][1:-1] # Ignore the first and last onset
        sleep_offset_idx = np.where(np.diff(sleep) == -1)[0][1:] # Ignore the first offset
    else:
        raise ValueError(f'light_condition must be either "early_light" or "late_light" but got {light_condition}')
    min_length = min(len(sleep_onset_idx), len(sleep_offset_idx))
    sleep_onset_idx = sleep_onset_idx[:min_length]
    sleep_offset_idx = sleep_offset_idx[:min_length]
    sleep_duration = time[sleep_offset_idx] - time[sleep_onset_idx]
    return sleep_duration