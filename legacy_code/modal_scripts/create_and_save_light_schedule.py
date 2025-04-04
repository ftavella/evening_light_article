import modal

# Simulation config
INDOOR_LUX = 240
READING_START_TIME = 18
READING_DURATION = 22 - READING_START_TIME
APP_NAME = f"light_schedule_{INDOOR_LUX}_lux_{READING_DURATION}_hours"
REMOTE_RESULTS_SAVE_FOLDER = f"data/light_schedules"
TIMEOUT_HOURS = 2
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
    .pip_install(circadian_pip)
    .run_commands(["echo 'Built'"])
)

volume = modal.Volume.from_name(VOLUME_NAME)

@app.function(volumes={VOLUME_LOCATION: volume},
              image=image, gpu=GPU, timeout=TIMEOUT,
              mounts=[modal.Mount.from_local_dir(LOCAL_UTILS_LOCATION, 
                                                 remote_path=REMOTE_UTILS_LOCATION)])
def calculate_light_schedule(indoor_lux=INDOOR_LUX, 
                             reading_start_time=READING_START_TIME,
                             reading_duration=READING_DURATION, 
                             remote_results_save_folder=REMOTE_RESULTS_SAVE_FOLDER, 
                             volume_location=VOLUME_LOCATION,
                             dt=0.005, days=14, 
                             default_chang14_parameters=DEFAULT_CHANG14_PARAMETERS
                             ):
    import os
    import numpy as np
    from circadian.lights import LightSchedule

    time = np.arange(0, 24 * days, dt)

    ebook_first_schedule = LightSchedule.Chang14(**default_chang14_parameters, 
                                                   typical_indoor_lux=indoor_lux, 
                                                   reading_start_time=reading_start_time, 
                                                   reading_duration=reading_duration, 
                                                   first_reading_condition="eReader")
    ebook_first_light = ebook_first_schedule(time)

    ebook_second_schedule = LightSchedule.Chang14(**default_chang14_parameters,
                                                    typical_indoor_lux=indoor_lux,
                                                    reading_start_time=reading_start_time,
                                                    reading_duration=reading_duration,
                                                    first_reading_condition="Book")
    ebook_second_light = ebook_second_schedule(time)

    save_location = os.path.join(volume_location, remote_results_save_folder)
    if not os.path.exists(save_location):
        os.makedirs(save_location)

    save_name = f"light_schedule_{indoor_lux}_lux_{reading_duration}_hours.npz"

    np.savez(os.path.join(save_location, save_name),
             indoor_lux=indoor_lux, reading_start_time=reading_start_time,
             reading_duration=reading_duration, ebook_first_light=ebook_first_light,
             ebook_second_light=ebook_second_light)

    volume.commit()
    return "Done"


@app.local_entrypoint()
def main():
    msg = calculate_light_schedule.remote()
    print(msg)