##
# @file experiment_runner.py
# @author Tom Rose
#
# @brief
#   Provides routines to run and report on ZKP/blockchain experiments using the Experiment class.
#   Supports running experiments with different ZoKrates circuits and configurations for automated testing.
#
# @details
#   - Sets up and runs experiments with dummy.zok and auth.zok circuits.
#   - Integrates with vehicle, RSU, ZoKrates, and blockchain modules.
#   - Supports debug mode and cleanup of ZoKrates artifacts.
#   - Logs experiment execution and results to files in the logs/ directory.
##

## Imports
# Libraries
# import secrets
# import time
# import random
import os
import logging
from pathlib import Path
import datetime
import shutil

# from utilities import clear_console
from experiment import Experiment
from vehicle import Vehicle
from rsu import RSU
from timer import Timer
from timer import Timer
from utilities import check_file_exists

from blockchain import (
    # simulate_blockchain_verification,
    set_debug_mode as set_blockchain_debug_mode
)

from sumo_interface import (
    # test_sumo_connection_wrapper,
    set_debug_mode as set_sumo_debug_mode,
    start_sumo_simulation,
    cleanup_sumo_and_traci
)

from zokrates_interface import (
    # hex_to_field_array,
    # run_zokrates_compile,
    # run_zokrates_setup,
    # run_zokrates_compute_witness,
    # run_zokrates_generate_proof,
    # run_zokrates_verify,
    cleanup_zokrates_files,
    set_debug_mode as set_zokrates_debug_mode
)

from settings import (
    DEBUG_MODE as DEFAULT_DEBUG_MODE,
    ZOKRATES_DUMMY_CIRCUIT,
    ZOKRATES_AUTH_CIRCUIT,
    SUMO_PORT_DATA_CONFIG,
    SUMO_TOOLS_PATH,
    SUMO_PORT_DYNAMIC_SPAWN,
    SUMO_PORT_RSUWITHDELAY
)

# Uncomment if blockchain_interface is used
# from blockchain_interface import set_debug_mode as set_blockchain_interface_debug_mode

## @var DEBUG_MODE
## @brief Global variable to control debug output.
DEBUG_MODE = DEFAULT_DEBUG_MODE

## @var experiment_count
## @brief Counter for the number of experiments run.
experiment_count = 0

## @var tested
## @brief Counter for the number of tests performed.
tested = 0

## @var logger
## @brief Global logger for the experiment runner.
logger = None

##
# @brief Set up logging for the experiment runner.
# @details
#   - Creates a logs directory if it doesn't exist.
#   - Configures a logger with a timestamped filename.
#   - Sets up logging level and format.
##
def setup_logging():
    global logger
    
    # Create logs directory if it doesn't exist
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    # Create timestamped filename for the runner's log
    timestamp_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = f"{timestamp_str}_experiment_runner.log"
    log_filepath = logs_dir / log_filename
    
    # Configure logger
    logger = logging.getLogger("experiment_runner")
    logger.setLevel(logging.DEBUG)
    
    # Clear any existing handlers
    if logger.hasHandlers():
        logger.handlers.clear()
    
    # Add file handler
    file_handler = logging.FileHandler(log_filepath)
    file_handler.setLevel(logging.DEBUG)
    
    # Add console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO if DEBUG_MODE else logging.WARNING)
    
    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Add handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    logger.info("Experiment runner initialized")
    return logger

##
# @brief Enable or disable debug mode for detailed output.
# @param enabled True to enable debug mode, False to disable.
# @details
#   - Sets the global DEBUG_MODE variable.
#   - Propagates debug mode to all relevant modules/classes.
##
def set_debug_mode(enabled):
    
    # Set the global DEBUG_MODE variable
    global DEBUG_MODE
    DEBUG_MODE = enabled
    
    # Set debug mode for all relevant modules
    Experiment.DEBUG_MODE = enabled
    set_zokrates_debug_mode(enabled)
    set_blockchain_debug_mode(enabled)
    set_sumo_debug_mode(enabled)
    
    # Update console handler log level
    if logger:
        for handler in logger.handlers:
            if isinstance(handler, logging.StreamHandler) and not isinstance(handler, logging.FileHandler):
                handler.setLevel(logging.INFO if enabled else logging.WARNING)
    
    if logger:
        logger.debug(f"Debug mode set to: {enabled}")
    
    # set_blockchain_interface_debug_mode(enabled)


##
# @brief Run a demo experiment using the Experiment class with zokrates/dummy.zok.
# @details
#   Steps:
#     1. Increment experiment count and set up experiment parameters.
#     2. Instantiate Experiment with zokrates/dummy.zok.
#     3. Run and report the experiment.
#     4. Clean up ZoKrates-generated files.
##
def run_demo_experiment():
    
    # Increment experiment count and set up experiment parameters
    global experiment_count
    experiment_count += 1
    name = f"Experiment_{experiment_count}"
    
    if logger:
        logger.info(f"Running demo experiment: {name}")
    
    # Generate a vehicle ID and RSU ID for this experiment
    vehicle_id = f"Vehicle_{experiment_count}"
    rsu_id = f"RSU_{experiment_count}"
    
    if logger:
        logger.debug(f"Vehicle ID: {vehicle_id}, RSU ID: {rsu_id}")
    
    # Path to the ZoKrates circuit file from settings
    zokrates_circuit_path = ZOKRATES_DUMMY_CIRCUIT
    
    # Create an Experiment instance with the specified parameters
    exp = Experiment(name, vehicle_id, rsu_id, zokrates_circuit_path, use_zokrates=True, use_blockchain=False)
    
    # Run the experiment and report results
    if logger:
        logger.info(f"Running experiment {name}")
    
    exp.run()
    
    if logger:
        logger.info(f"Reporting on experiment {name}")
    
    exp.report()
    
    # Clean up ZoKrates-generated files after the experiment
    if logger:
        logger.debug("Cleaning up ZoKrates files")
    
    cleanup_zokrates_files()


##
# @brief Run an experiment using the zokrates/auth.zok circuit which provides a simple field-based proof.
# @details
#   Steps:
#     1. Increment experiment count and set up experiment parameters.
#     2. Instantiate Experiment with zokrates/auth.zok.
#     3. Run and report the experiment.
#     4. Clean up ZoKrates-generated files.
##
def run_auth_experiment():
    
    # Increment experiment count and set up experiment parameters
    global experiment_count
    experiment_count += 1
    name = f"Auth_Experiment_{experiment_count}"
    
    if logger:
        logger.info(f"Running auth experiment: {name}")
    
    # Generate a vehicle ID and RSU ID for this experiment
    vehicle_id = f"Auth_Vehicle_{experiment_count}"
    rsu_id = f"Auth_RSU_{experiment_count}"
    
    if logger:
        logger.debug(f"Vehicle ID: {vehicle_id}, RSU ID: {rsu_id}")
    
    # Path to the ZoKrates circuit file from settings
    zokrates_circuit_path = ZOKRATES_AUTH_CIRCUIT
    
    # Create an Experiment instance with the specified parameters
    exp = Experiment(name, vehicle_id, rsu_id, zokrates_circuit_path, use_zokrates=True, use_blockchain=False)
    
    # Run the experiment and report results
    if logger:
        logger.info(f"Running experiment {name}")
    
    exp.run()
    
    if logger:
        logger.info(f"Reporting on experiment {name}")
    
    exp.report()
    
    # Clean up ZoKrates-generated files after the experiment
    if logger:
        logger.debug("Cleaning up ZoKrates files")
    
    cleanup_zokrates_files()


def run_test_1_level_1_experiment(print_data=True):
    """
    Experiment: Test_1_Level_1
    Spawns cars dynamically in SUMO (straightaway5.sumocfg), tracks throughput (number of cars completing their routes).
    Reports and logs throughput at the end.
    """
    global experiment_count
    experiment_count += 1
    name = f"Test_1_Level_1_{experiment_count}"
    
    # Create experiment instance without ZoKrates or blockchain
    exp = Experiment(name, f"Vehicle_{experiment_count}", f"RSU_{experiment_count}", None, use_zokrates=False, use_blockchain=False)
    exp.logger.info(f"Running experiment: {name}")

    timer = Timer(f"{name} Timer")
    timer.start()

    # Use the correct config file path and port
    sumo_cfg = os.path.join(
        os.path.dirname(__file__),
        "..", "..", "SUMO", "Built Sims", "StraightAway5", "straightaway5.sumocfg"
    )
    sumo_cfg = os.path.abspath(sumo_cfg)
    port = SUMO_PORT_DYNAMIC_SPAWN  # Avoid port conflicts

    # Check config file exists
    if not check_file_exists(sumo_cfg, "SUMO straightaway5 configuration file"):
        if logger:
            logger.error(f"Config file not found: {sumo_cfg}")
        return

    proc, traci, _, temp_config, temp_output_dir = start_sumo_simulation(
        file_path=sumo_cfg,
        is_config=True,
        port=port,
        sumo_binary="sumo",
        connect_traci=True,
        sumo_tools_path=SUMO_TOOLS_PATH
    )

    if proc is None or traci is None:
        if logger:
            logger.error("Failed to start SUMO or connect to TraCI.")
        return

    throughput = 0
    try:
        total_steps = 1010
        car_counter = 0
        active_cars = {}  # Track active cars and their spawn times
        car_type = "car"
        car_route = "route1"

        for step in range(total_steps):
            # Exit if we've reached total_steps
            if step >= total_steps - 1:
                print(f"\nReached max steps ({total_steps}). Ending simulation.")
                break
            traci.simulationStep()
            sim_time = traci.simulation.getTime()

            # Check for cars that have finished their routes
            for car_id in list(active_cars.keys()):
                if car_id not in traci.vehicle.getIDList():
                    throughput += 1
                    if print_data:
                        print(f"{car_id} finished at step {step}")
                    del active_cars[car_id]

            # Spawn a new car if no active cars are present and we're past step 10
            if not active_cars and step >= 10:
                car_counter += 1
                new_car_id = f"car{car_counter}"
                traci.vehicle.add(
                    vehID=new_car_id,
                    routeID=car_route,
                    typeID=car_type,
                    depart=sim_time
                )
                active_cars[new_car_id] = step
                if print_data:
                    print(f"Spawned {new_car_id} at step {step}")

            if print_data and step % 100 == 0:
                print(f"Step {step}: Active cars: {list(active_cars.keys())}, Throughput: {throughput}")
                exp.logger.info(f"Step {step}: Active cars: {list(active_cars.keys())}, Throughput: {throughput}")

        exp.logger.info(f"Experiment {name} throughput: {throughput} cars finished in {total_steps} steps.")
        print(f"\nExperiment {name} throughput: {throughput} cars finished in {total_steps} steps.")

    except Exception as e:
        exp.logger.error(f"[{name}] Error: {e}")
        print(f"[{name}] Error: {e}")

    finally:
        cleanup_sumo_and_traci(proc, port, traci)
        if temp_config and os.path.exists(temp_config):
            try: os.unlink(temp_config)
            except: pass
        if temp_output_dir and os.path.exists(temp_output_dir):
            try: shutil.rmtree(temp_output_dir)
            except: pass

    timer.stop()
    exp.logger.info(f"{name} completed in {timer.elapsed():.8f} seconds.")
    print(f"\n{name} completed in {timer.elapsed():.8f} seconds.\n")


def run_test_1_level_2_experiment(print_data=True):
    """
    Experiment: Test_1_Level_2
    Connects to straightaway6.sumocfg, spawns a car at step 1000, and whenever a car completes its route,
    immediately spawns another identical car, for 51000 steps.
    Implements RSU-car proximity logic: stops car for 2 seconds when within 125m of RSU, then resumes.
    """
    global experiment_count
    experiment_count += 1
    name = f"Test_1_Level_2_{experiment_count}"

    # Create experiment instance without ZoKrates or blockchain
    exp = Experiment(name, f"Vehicle_{experiment_count}", f"RSU_{experiment_count}", None, use_zokrates=False, use_blockchain=False)
    exp.logger.info(f"Running experiment: {name}")

    timer = Timer(f"{name} Timer")
    timer.start()

    # Use the correct config file path and port
    sumo_cfg = os.path.join(
        os.path.dirname(__file__),
        "..", "..", "SUMO", "Built Sims", "StraightAway6", "straightaway6.sumocfg"
    )
    sumo_cfg = os.path.abspath(sumo_cfg)
    port = SUMO_PORT_RSUWITHDELAY

    # Check config file exists
    if not check_file_exists(sumo_cfg, "SUMO straightaway6 configuration file"):
        if logger:
            logger.error(f"Config file not found: {sumo_cfg}")
        return

    proc, traci, _, temp_config, temp_output_dir = start_sumo_simulation(
        file_path=sumo_cfg,
        is_config=True,
        port=port,
        sumo_binary="sumo",
        connect_traci=True,
        step_length=0.01,
        sumo_tools_path=SUMO_TOOLS_PATH
    )

    if proc is None or traci is None:
        if logger:
            logger.error("Failed to start SUMO or connect to TraCI.")
        return

    flags_raised = 0
    flags_lowered = 0
    throughput = 0
    try:
        total_steps = 51000
        car_counter = 0
        active_cars = {}
        car_type = "car"
        car_route = "route1"
        finished_cars = 0

        cars_that_triggered_stop = set()
        stopped_cars = {}  # car_id -> step to resume at

        for step in range(total_steps):
            # --- Handle cars that need to resume after stop ---
            for car_id in list(stopped_cars.keys()):
                if step >= stopped_cars[car_id]:
                    try:
                        if car_id in traci.vehicle.getIDList():
                            traci.vehicle.setSpeed(car_id, -1)  # Resume normal speed
                            if print_data:
                                print(f"*** RESUMING: Car {car_id} is resuming normal speed at step {step} ***")
                    except Exception as e:
                        print(f"Could not resume car {car_id}: {e}")
                    del stopped_cars[car_id]

            # --- RSU-car interaction logic ---
            rsu_ids = []
            car_ids = []
            try:
                rsu_ids = [vid for vid in traci.vehicle.getIDList() if traci.vehicle.getTypeID(vid) == "rsu"]
                car_ids = [vid for vid in traci.vehicle.getIDList() if traci.vehicle.getTypeID(vid) == "car" and vid not in cars_that_triggered_stop]
                for car_id in car_ids:
                    if car_id in stopped_cars:
                        continue
                    if not rsu_ids:
                        continue
                    rsu_pos = traci.vehicle.getPosition(rsu_ids[0])
                    car_pos = traci.vehicle.getPosition(car_id)
                    dx = rsu_pos[0] - car_pos[0]
                    dy = rsu_pos[1] - car_pos[1]
                    dist = (dx**2 + dy**2) ** 0.5
                    if dist < 125:
                        try:
                            current_speed = traci.vehicle.getSpeed(car_id)
                            traci.vehicle.setSpeed(car_id, 0)
                            resume_step = step + 1000
                            stopped_cars[car_id] = resume_step
                            cars_that_triggered_stop.add(car_id)
                            flags_raised += 1
                            print(f"*** STOPPING: Car {car_id} at step {step} (distance: {dist:.2f} m, speed: {current_speed:.2f} m/s) ***")
                            print(f"*** Will resume at step {resume_step} ***")
                        except Exception as e:
                            print(f"Could not stop car {car_id}: {e}")
            except Exception as e:
                if step % 1000 == 0:
                    print(f"Step {step}: Could not compute RSU-car interactions: {e}")

            # Exit if we've reached total_steps
            if step >= total_steps - 1:
                print(f"\nReached max steps ({total_steps}). Ending simulation.")
                print(f"Total cars finished: {finished_cars}")
                print(f"Flags raised (cars stopped): {flags_raised}")
                print(f"Cars that triggered stop: {len(cars_that_triggered_stop)}")
                break

            traci.simulationStep()
            sim_time = traci.simulation.getTime()

            # Check for cars that have finished their routes
            for car_id in list(active_cars.keys()):
                if car_id not in traci.vehicle.getIDList():
                    finished_cars += 1
                    throughput += 1
                    if print_data:
                        print(f"{car_id} finished at step {step}")
                    del active_cars[car_id]

            # Spawn a new car if no active cars are present and we're past step 1000
            if not active_cars and step >= 100:
                car_counter += 1
                new_car_id = f"car{car_counter}"
                traci.vehicle.add(
                    vehID=new_car_id,
                    routeID=car_route,
                    typeID=car_type,
                    depart=sim_time
                )
                active_cars[new_car_id] = step
                if print_data:
                    print(f"Spawned {new_car_id} at step {step}")

            if step % 1000 == 0:
                print(f"Step {step}: Active cars: {list(active_cars.keys())}, Total finished cars: {finished_cars}")

            if print_data and DEBUG_MODE:
                veh_ids = traci.vehicle.getIDList()
                print(f"Step {step}: Vehicles in sim: {veh_ids}")
                for car_id in veh_ids:
                    try:
                        pos = traci.vehicle.getPosition(car_id)
                        print(f"Step {step}: {car_id} position: {pos}")
                    except Exception as e:
                        print(f"Step {step}: Could not get position for {car_id}: {e}")

        exp.logger.info(f"Experiment {name} throughput: {throughput} cars finished in {total_steps} steps.")
        print(f"\nExperiment {name} throughput: {throughput} cars finished in {total_steps} steps.")

    except Exception as e:
        exp.logger.error(f"[{name}] Error: {e}")
        print(f"[{name}] Error: {e}")

    finally:
        cleanup_sumo_and_traci(proc, port, traci)
        if temp_config and os.path.exists(temp_config):
            try: os.unlink(temp_config)
            except: pass
        if temp_output_dir and os.path.exists(temp_output_dir):
            try: shutil.rmtree(temp_output_dir)
            except: pass

    timer.stop()
    exp.logger.info(f"{name} completed in {timer.elapsed():.8f} seconds.")
    print(f"\n{name} completed in {timer.elapsed():.8f} seconds.\n")


def run_test_1_level_3_experiment(print_data=True):
    return


def run_test_1_level_4_experiment(print_data=True):
    return


def base_experiments_test():
    
    # Set up logging
    setup_logging()
    
    if logger:
        logger.info("Starting base experiments test")
    
    # Ensure no old files interfere
    cleanup_zokrates_files()  
    
    # Run both test experiments
    print("\n=== Running Basic Dummy Circuit Experiment ===")
    if logger:
        logger.info("Running Basic Dummy Circuit Experiment")
    
    run_demo_experiment()
    
    print("\n=== Running Cryptographically Meaningful Auth Circuit Experiment ===")
    if logger:
        logger.info("Running Cryptographically Meaningful Auth Circuit Experiment")
    
    run_auth_experiment()
    
    # Run Test_1_Level_1 experiment
    print("\n=== Running Test_1_Level_1 Experiment (Dynamic Car Spawning Throughput) ===")
    if logger:
        logger.info("Running Test_1_Level_1 Experiment (Dynamic Car Spawning Throughput)")
    run_test_1_level_1_experiment(print_data=True)

    # Run Test_1_Level_2 experiment
    print("\n=== Running Test_1_Level_2 Experiment (RSU-Car Proximity Logic) ===")
    if logger:
        logger.info("Running Test_1_Level_2 Experiment (RSU-Car Proximity Logic)")
    run_test_1_level_2_experiment(print_data=True)

    if logger:
        logger.info("Base experiments test completed")
    
    
if __name__ == "__main__":
    
    ## @brief Main entry point for running experiments.
    base_experiments_test()

