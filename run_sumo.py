import os
import subprocess

def run_sumo():
    # Ensure SUMO_HOME is set
    sumo_home = os.environ.get("SUMO_HOME")
    if not sumo_home:
        raise EnvironmentError("Please set the SUMO_HOME environment variable.")

    # Path to SUMO binary
    sumo_binary = os.path.join(sumo_home, "bin", "sumo")

    # Path to the configuration file
    config_file = "simulation_config.sumocfg"

    # Run SUMO
    subprocess.run([sumo_binary, "-c", config_file])

if __name__ == "__main__":
    run_sumo()
