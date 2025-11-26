# **From Sunlight to Screens: Modeling When Light Exposure Matters Most for Sleep and Circadian Health**

Franco Tavella, Michael Gradisar, Renske Lok, Olivia Walch

## About

This repository provides the implementation of the mathematical models used to simulate the effects of light on the human circadian clock and sleep patterns. The code allows you to reproduce the results presented in the paper, explore different light schedules, and investigate the impact of various parameters on sleep and circadian metrics.

## Paper Abstract

Understanding the effects of light on the body at different times of the 24-hr solar day is a topic of increasing interest. In this paper, we use mathematical models from the literature to simulate what would be expected of the human circadian clock from different light schedules. We reproduce an experiment which showed eReaders capable of delaying sleep and melatonin onset. The model is able to match the delay in sleep timing (~ 5 minutes) when results are averaged across parameter sets, but not the full phase shift reported empirically.  However, certain initial conditions and parameters are capable of phase shifts of achieving a phase shift of 1.5 hours, consistent with the original study’s magnitude. We next examine the same paradigm under higher daytime light levels (increasing baseline illumination from 90 to 500 lux) , and find that brighter daytime exposure reduces both  sleep onset latency and phase delay  caused by evening eReader light. Finally, we explore how the timing of a bright light pulse during the day changes outcomes, such as sleep onset and circadian amplitude, and how these effects interact with light during the other hours of the 24-hour day. Together, these modeling results suggest robust daytime light exposure confers resilience against the circadian-disruptive effects of evening light and generate testable predictions regarding the timing and intensity of beneficial light interventions for maintaining circadian alignment. 


## Repository Contents

-   `src/`: Contains the source code for the mathematical models and simulations.
-   `data/`: Includes processed simulation data to generate plots
-   `figures/`: Plots summarizing the results of our simulations
-   `requirements.txt`: A list of Python dependencies required to run the code.

## Getting Started

### Prerequisites

-   Required Python packages (see `requirements.txt`)

### Installation

1.  Clone the repository:

    ```bash
    git clone <repository_url>
    ```

2.  Navigate to the repository directory:

    ```bash
    cd <repository_directory>
    ```

3.  Create a virtual environment (recommended):

    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

4.  Install the required Python packages:

    ```bash
    pip install -r requirements.txt
    ```

### Running the Simulations

Detailed instructions on how to run the simulations and reproduce the results are provided in the Jupyter notebooks located in the `src/` directory. Open the notebooks using Jupyter:

```bash
jupyter notebook
