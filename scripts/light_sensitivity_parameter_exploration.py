import numpy as np
import pandas as pd
from tqdm import tqdm
from circadian.models import Skeldon23
from circadian.lights import LightSchedule

# Simulation setup
dt = 0.005 # hours
equilibration_days = 3
equilibration_loops = 10
equilibration_time = np.arange(0.0, 24 * equilibration_days, dt)
simulation_days = 2
lights_on = 6.0
lights_off = 22.0
typical_indoor_lux = 1000.0
initial_sleep = 1.0 # asleep
forced_wakeup_threshold = 0.5 # lux
simulation_time = np.arange(0.0, 24 * simulation_days, dt)
regular_schedule = LightSchedule.Regular(typical_indoor_lux, lights_on=lights_on,
                                         lights_off=lights_off)
equilibration_light = regular_schedule(equilibration_time)
simulation_light = regular_schedule(simulation_time)

save_path = "../data/light_sensitivity_parameter_exploration"
sim_prefix = "light_sensitivity_parameter_exploration"

# Reference homeostat parameters, simulation 84 from homeostat parameter exploration
mu = 19.0
delta = 6.0
chi = 11.0

# Parameters to explore
p_values = np.linspace(0.2, 1.0, 5)
k_values = np.linspace(-1.0, 1.0, 5)
tauc_values = np.linspace(23.5, 24.7, 5)

# Save simulation setup information
np.savez(f"{save_path}/{sim_prefix}_simulation_setup.npz",
         dt=dt,
         equilibration_days=equilibration_days,
         equilibration_loops=equilibration_loops,
         equilibration_time=equilibration_time,
         simulation_days=simulation_days,
         lights_on=lights_on,
         lights_off=lights_off,
         typical_indoor_lux=typical_indoor_lux,
         initial_sleep=initial_sleep,
         forced_wakeup_threshold=forced_wakeup_threshold,
         simulation_time=simulation_time,
         equilibration_light=equilibration_light,
         simulation_light=simulation_light,
         p_values=p_values,
         k_values=k_values,
         tauc_values=tauc_values,)

simulation_idx = 0
for p in tqdm(p_values):
    for k in tqdm(k_values):
        for tauc in tqdm(tauc_values):         
            parameters = {'S0': initial_sleep, 'mu': mu, 'Delta': delta, 'chi': chi,
                          'p': p, 'k': k, 'tauc': tauc,
                          'forced_wakeup_light_threshold': forced_wakeup_threshold,}
            equilibration_model = Skeldon23(params=parameters)
            initial_condition = equilibration_model.equilibrate(equilibration_time, 
                                                                equilibration_light, 
                                                                num_loops=equilibration_loops)
            simulation_model = Skeldon23(params=parameters)
            trajectory = simulation_model.integrate(simulation_time, initial_condition, 
                                                   simulation_light)
            result_data = {
                'parameters': parameters,
                'simulation_model': simulation_model,
                'trajectory': trajectory,
            }
            np.savez(f'{save_path}/{sim_prefix}_{simulation_idx}.npz', 
                     result_data=result_data)
            simulation_idx += 1