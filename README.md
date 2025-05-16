# 2025-Fellowship-Personal

## Setup Instructions

1. **Install SUMO**:
   - Download and install SUMO from [SUMO Downloads](https://sumo.dlr.de/docs/Downloads.html).
   - Set the `SUMO_HOME` environment variable to the SUMO installation directory.

2. **Prepare the Files**:
   - Ensure the following files are in the project directory:
     - `run_sumo.py`: Python script to run the simulation.
     - `network.net.xml`: Defines the road network.
     - `routes.rou.xml`: Defines vehicle routes.
     - `simulation_config.sumocfg`: Configuration file for the simulation.

3. **Run the Simulation**:
   - Open a terminal or command prompt.
   - Navigate to the project directory.
   - Execute the following command:
     ```bash
     python run_sumo.py
     ```

4. **View Results**:
   - SUMO will open a GUI (if installed) to visualize the simulation.
   - Alternatively, you can use `sumo-gui` instead of `sumo` in the script for a graphical interface.

