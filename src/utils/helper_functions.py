import os
import re
import numpy as np
from circadian.models import DynamicalTrajectory, Skeldon23

def find_files_in_dir(directory, file_pattern):
    return [os.path.join(directory, f) for f in os.listdir(directory) if re.match(file_pattern, f)]


def sleep_metrics(time, sleep):
    sleep_onsets = np.where(np.diff(sleep) == 1)[0]
    sleep_offsets = np.where(np.diff(sleep) == -1)[0]
    # If the first offset is before the first onset, remove it
    if sleep_offsets[0] < sleep_onsets[0]:
        sleep_offsets = sleep_offsets[1:]
    # If the last onset is after the last offset, remove it
    if sleep_onsets[-1] > sleep_offsets[-1]:
        sleep_onsets = sleep_onsets[:-1]
    # Check that the number of onsets and offsets are the same
    if len(sleep_onsets) != len(sleep_offsets):
        raise ValueError('Number of sleep onsets and offsets do not match')
    # Calculate metrics
    sleep_duration = time[sleep_offsets] - time[sleep_onsets]
    sleep_onset_time = time[sleep_onsets]
    sleep_offset_time = time[sleep_offsets]
    return sleep_duration, sleep_onset_time, sleep_offset_time


def calculate_cbtmin(time, trajectory_states):
    trajectory = DynamicalTrajectory(time, trajectory_states)
    cbtmin = Skeldon23().cbt(trajectory)[:-1] # ignore the last day
    return cbtmin