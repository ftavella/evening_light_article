import modal

# Simulation config
INDOOR_LUX = 240
READING_START_TIME = 18
READING_DURATION = 22 - READING_START_TIME
APP_NAME = f"simulation_{INDOOR_LUX}_lux_{READING_DURATION}_hours"
REMOTE_RESULTS_SAVE_FOLDER = "data/chang14_realistic_conditions"
REMOTE_LIGHT_DATA_LOCATION = "data/light_schedules"
REMOTE_SELECTED_PARAMETERS_LOCATION = "data/sleep_parameter_exploration"
SELECTED_PARAMETERS_FILE_NAME = "selected_sleep_parameters.csv"
TIMEOUT_HOURS = 4
TIMEOUT = TIMEOUT_HOURS * 60 * 60
GPU = None

DEFAULT_CHANG14_PARAMETERS = {
    "dim_lux": 3.0,
    "ereader_lux": 31.73,
    "book_lux": 0.91,
}

LOCAL_UTILS_LOCATION = "../utils"
REMOTE_UTILS_LOCATION = "/root/utils"
PYTHON_VERSION = "3.11"
VOLUME_NAME = "evening-light"
VOLUME_LOCATION = "/root/evening_light"

circadian_pip = "git+https://github.com/ftavella/circadian.git@chang14-light"

app = modal.App(name=APP_NAME)

image = (
    modal.Image.debian_slim(python_version=PYTHON_VERSION)
    .apt_install("git")
    .pip_install("tqdm")
    .pip_install(circadian_pip)
    .run_commands(["echo 'Built'"])
)

volume = modal.Volume.from_name(VOLUME_NAME)

@app.function(volumes={VOLUME_LOCATION: volume},
              image=image, gpu=GPU, timeout=TIMEOUT,
              mounts=[modal.Mount.from_local_dir(LOCAL_UTILS_LOCATION, 
                                                 remote_path=REMOTE_UTILS_LOCATION)])
def simulate_light_schedule(indoor_lux=INDOOR_LUX, 
                            reading_duration=READING_DURATION, 
                            remote_results_save_folder=REMOTE_RESULTS_SAVE_FOLDER, 
                            volume_location=VOLUME_LOCATION, 
                            dt=0.005, days=14, 
                            forced_wakeup_threshold=0.5,
                            light_data_location=REMOTE_LIGHT_DATA_LOCATION,
                            selected_parameters_location=REMOTE_SELECTED_PARAMETERS_LOCATION,
                            selected_parameters_file_name=SELECTED_PARAMETERS_FILE_NAME,
                            ):
    import os
    import numpy as np
    import pandas as pd
    from tqdm import tqdm
    from circadian.models import Skeldon23
    from utils.helper_functions import H_thresholds

    time = np.arange(0, 24 * days, dt)
    light_file_name = f"light_schedule_{indoor_lux}_lux_{reading_duration}_hours.npz"
    light_file_location = os.path.join(volume_location, light_data_location, light_file_name)
    light_data = np.load(light_file_location)
    
    chang14_ebook_first_light = light_data["ebook_first_light"]
    chang14_ebook_second_light = light_data["ebook_second_light"]

    selected_parameters_file_location = os.path.join(volume_location, 
                                                     selected_parameters_location, 
                                                     selected_parameters_file_name)
    selected_parameters = pd.read_csv(selected_parameters_file_location, index_col=0)

    for idx in tqdm(selected_parameters.index, desc='Simulating', total=len(selected_parameters)):
        # Parameters
        mu = selected_parameters.loc[idx, 'mu']
        delta = selected_parameters.loc[idx, 'Delta']
        chi = selected_parameters.loc[idx, 'chi']
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
            'forced_wakeup_light_threshold': forced_wakeup_threshold,
        }
        # ebook first simulation
        chang14_ebook_first_model = Skeldon23(params=parameters)
        chang14_ebook_first_trajectory = chang14_ebook_first_model.integrate(time, 
                                                                            initial_condition=initial_condition, 
                                                                            input=chang14_ebook_first_light)
        chang14_ebook_first_H_plus, chang14_ebook_first_H_minus = H_thresholds(chang14_ebook_first_model, chang14_ebook_first_trajectory)
        # ebook second simulation
        chang14_ebook_second_model = Skeldon23(params=parameters)
        chang14_ebook_second_trajectory = chang14_ebook_second_model.integrate(time, 
                                                            initial_condition=initial_condition,
                                                            input=chang14_ebook_second_light)
        chang14_ebook_second_H_plus, chang14_ebook_second_H_minus = H_thresholds(chang14_ebook_second_model, chang14_ebook_second_trajectory)

        save_location = os.path.join(volume_location, remote_results_save_folder, f"{indoor_lux}_lux_{reading_duration}_hours")
        if not os.path.exists(save_location):
            os.makedirs(save_location)
        save_file_name = f"simulation_{indoor_lux}_lux_{reading_duration}_hours_{idx}.npz"
        save_file_location = os.path.join(save_location, save_file_name)

        # Save data
        np.savez(save_file_location, parameters=parameters,
                initial_condition=initial_condition,
                chang14_ebook_first_trajectory_states=chang14_ebook_first_trajectory.states,
                chang14_ebook_first_light=chang14_ebook_first_light,
                chang14_ebook_first_sleep=chang14_ebook_first_model.sleep_state,
                chang14_ebook_first_H_plus=chang14_ebook_first_H_plus,
                chang14_ebook_first_H_minus=chang14_ebook_first_H_minus,
                chang14_ebook_second_trajectory_states=chang14_ebook_second_trajectory.states,
                chang14_ebook_second_light=chang14_ebook_second_light,
                chang14_ebook_second_sleep=chang14_ebook_second_model.sleep_state,
                chang14_ebook_second_H_plus=chang14_ebook_second_H_plus,
                chang14_ebook_second_H_minus=chang14_ebook_second_H_minus,
        )
        volume.commit()

    return "Done"


@app.local_entrypoint()
def main():
    msg = simulate_light_schedule.remote()
    print(msg)