# **When do natural and artificial light matter to sleep and circadian metrics? A mathematical modeling approach**

Franco Tavella, Michael Gradisar, Renske Lok, Olivia Walch

## About

This repository provides the implementation of the mathematical models used to simulate the effects of light on the human circadian clock and sleep patterns. The code allows you to reproduce the results presented in the paper, explore different light schedules, and investigate the impact of various parameters on sleep and circadian metrics.

## Paper Abstract

Understanding the effects of light at different times on the body is a topic of enduring interest. In this paper, we use mathematical models from the literature to simulate what would be expected to the human circadian clock on different light schedules. We reproduce an experiment which showed eReaders capable of delaying sleep and melatonin onset. We find that we are able to match the delay in sleep timing but not the phase shift in melatonin, except in cases where the subjects are assumed to be highly light sensitive. Next, we show that daytime light exposure is predicted to reduce the amount of sleep onset latency and phase shift that would be expected from the eReader light. Finally, we explore how the timing of a bright light pulse during the day changes outcomes, such as sleep onset and circadian amplitude, and how these effects interact with light during the other hours of the 24 hour day.

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