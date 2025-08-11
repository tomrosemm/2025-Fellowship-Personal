##
# @file experiment_runner.py
# @author Tom Rose
#
# @brief
#   Provides routines to run and report on ZKP/blockchain experiments using the Experiment class
#   Supports running experiments with different ZoKrates circuits and configurations for automated testing
#
# @details
#   - Sets up and runs experiments with dummy.zok and auth.zok circuits
#   - Integrates with vehicle, RSU, ZoKrates, and blockchain modules
#   - Supports debug mode and cleanup of ZoKrates artifacts
#   - Logs experiment execution and results to files in the logs/ directory
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

# Classes and functions
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
    # SUMO_PORT_DATA_CONFIG,
    DEBUG_MODE as DEFAULT_DEBUG_MODE,
    ZOKRATES_DUMMY_CIRCUIT,
    ZOKRATES_AUTH_CIRCUIT,
    SUMO_TOOLS_PATH,
    SUMO_PORT_DYNAMIC_SPAWN,
    SUMO_PORT_RSUWITHDELAY,
    TEST_1_LEVEL_1_TOTAL_STEPS,
    TEST_1_LEVEL_1_SPAWN_STEP,
    TEST_1_LEVEL_2_STEP_LENGTH,
    TEST_1_LEVEL_2_TOTAL_STEPS,
    TEST_1_LEVEL_2_TIME_TO_WAIT,
    TEST_1_LEVEL_2_SPAWN_STEP,
    TEST_1_LEVEL_2_RSU_RANGE,
    TEST_1_LEVEL_1_SUMO_BINARY,
    TEST_1_LEVEL_2_SUMO_BINARY
)

## @var DEBUG_MODE
## @brief Global variable to control debug output
DEBUG_MODE = DEFAULT_DEBUG_MODE

## @var experiment_count
## @brief Counter for the number of experiments run
experiment_count = 0

## @var tested
## @brief Counter for the number of tests performed
tested = 0

## @var logger
## @brief Global logger for the experiment runner
logger = None


##
# @brief Enable or disable debug mode for detailed output
# @param enabled True to enable debug mode, False to disable
# @details
#   - Sets the global DEBUG_MODE variable
#   - Propagates debug mode to all relevant modules/classes
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
    
    # Update console handler log level based on debug mode
    if logger:
        for handler in logger.handlers:
            if isinstance(handler, logging.StreamHandler) and not isinstance(handler, logging.FileHandler):
                handler.setLevel(logging.INFO if enabled else logging.WARNING)
    
    # Log the debug mode change
    if logger:
        logger.debug(f"Debug mode set to: {enabled}")
        
        
##
# @brief Set up logging for the experiment runner
# @details
#   - Creates a logs directory if it doesn't exist
#   - Configures a logger with a timestamped filename
#   - Sets up logging level and format
##
def setup_logging():
    
    # Set up global logger variable
    global logger
    
    # logs_dir - create logs directory if it doesn't exist
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    # timestamp_str - format the current timestamp for log filename
    timestamp_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # log_filename - create a log filename with the timestamp
    log_filename = f"{timestamp_str}_experiment_runner.log"
    
    # log_filepath - full path to the log file
    log_filepath = logs_dir / log_filename
    
    # logger - create a logger instance and set its level to DEBUG
    logger = logging.getLogger("experiment_runner")
    logger.setLevel(logging.DEBUG)
    
    # Clear any existing handlers
    if logger.hasHandlers():
        logger.handlers.clear()
    
    # file_handler - create a file handler for logging to the log file
    file_handler = logging.FileHandler(log_filepath)
    file_handler.setLevel(logging.DEBUG)
    
    # console_handler - create a console handler for logging to the console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO if DEBUG_MODE else logging.WARNING)
    
    # formatter - create a formatter for log messages
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Add file and console handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    # Log initialization message
    logger.info("Experiment runner initialized")
    
    return logger


##
# @brief Run a demo experiment using the Experiment class with zokrates/dummy.zok
# @details
#   Steps:
#     1. Increment experiment count and set up experiment parameters
#     2. Instantiate Experiment with zokrates/dummy.zok
#     3. Run and report the experiment
#     4. Clean up ZoKrates-generated files
##
def run_demo_experiment():
    
    # Increment experiment count and set up experiment parameters
    global experiment_count
    experiment_count += 1
    name = f"Experiment_{experiment_count}"
    
    # Log the start of the experiment
    if logger:
        logger.info(f"Running demo experiment: {name}")
    
    # vehicle_id - Generate a unique vehicle ID for this experiment
    vehicle_id = f"Vehicle_{experiment_count}"
    
    # rsu_id - Generate a unique RSU ID for this experiment
    rsu_id = f"RSU_{experiment_count}"
    
    # Log the vehicle and RSU IDs
    if logger:
        logger.debug(f"Vehicle ID: {vehicle_id}, RSU ID: {rsu_id}")
    
    # zokrates_circuit_path - Path to the ZoKrates circuit file from settings
    zokrates_circuit_path = ZOKRATES_DUMMY_CIRCUIT
    
    # exp - Create an Experiment instance with the specified parameters
    exp = Experiment(name, vehicle_id, rsu_id, zokrates_circuit_path, use_zokrates=True, use_blockchain=False)
    
    # Log the start of the experiment run
    if logger:
        logger.info(f"Running experiment {name}")
    
    # Run the experiment
    exp.run()
    
    # Log the reporting of the experiment
    if logger:
        logger.info(f"Reporting on experiment {name}")
    
    # Report the results of the experiment
    exp.report()
    
    # Log the cleanup of ZoKrates files
    if logger:
        logger.debug("Cleaning up ZoKrates files")
    
    # Clean up ZoKrates-generated files after the experiment
    cleanup_zokrates_files()


##
# @brief Run an experiment using the zokrates/auth.zok circuit which provides a simple field-based proof
# @details
#   Steps:
#     1. Increment experiment count and set up experiment parameters
#     2. Instantiate Experiment with zokrates/auth.zok
#     3. Run and report the experiment
#     4. Clean up ZoKrates-generated files
##
def run_auth_experiment():
    
    # Increment experiment count and set up experiment parameters
    global experiment_count
    experiment_count += 1
    name = f"Auth_Experiment_{experiment_count}"
    
    # Log the start of the experiment
    if logger:
        logger.info(f"Running auth experiment: {name}")
    
    # vehicle_id - Generate a unique vehicle ID for this experiment
    vehicle_id = f"Auth_Vehicle_{experiment_count}"
    
    # rsu_id - Generate a unique RSU ID for this experiment
    rsu_id = f"Auth_RSU_{experiment_count}"
    
    # Log the vehicle and RSU IDs
    if logger:
        logger.debug(f"Vehicle ID: {vehicle_id}, RSU ID: {rsu_id}")
    
    # zokrates_circuit_path - Path to the ZoKrates auth circuit file from settings
    zokrates_circuit_path = ZOKRATES_AUTH_CIRCUIT
    
    # exp - Create an Experiment instance with the specified parameters
    exp = Experiment(name, vehicle_id, rsu_id, zokrates_circuit_path, use_zokrates=True, use_blockchain=False)
    
    # Log the start of the experiment run
    if logger:
        logger.info(f"Running experiment {name}")
    
    # Run the experiment
    exp.run()
    
    # Log the reporting of the experiment
    if logger:
        logger.info(f"Reporting on experiment {name}")
    
    # Report the results of the experiment
    exp.report()
    
    # Log the cleanup of ZoKrates files
    if logger:
        logger.debug("Cleaning up ZoKrates files")
    
    # Clean up ZoKrates-generated files after the experiment
    cleanup_zokrates_files()


##
# @brief Run Test_1_Level_1 experiment: dynamic car spawning throughput in SUMO
# @param print_data If True, print simulation data to screen
# @details
#   Spawns cars dynamically in SUMO (straightaway5.sumocfg), tracks throughput (number of cars completing their routes)
#   Reports and logs throughput at the end
#
# Steps:
#   1. Set up experiment parameters and logger
#   2. Start SUMO simulation and connect via TraCI
#   3. Spawn cars after 10 seconds (to let RSU arrive at parking spot) one on the road at a time, once one finishes its route spawn another
#   4. Track and count cars that finish their routes (throughput)
#   5. Print and log throughput results
#   6. Clean up SUMO and temporary files
##
def run_test_1_level_1_experiment(print_data=True):

    # Increment experiment count and set up experiment parameters
    global experiment_count
    experiment_count += 1
    name = f"Test_1_Level_1_{experiment_count}"
    
    # exp - Create an Experiment instance without ZoKrates or blockchain
    exp = Experiment(name, f"Vehicle_{experiment_count}", f"RSU_{experiment_count}", None, use_zokrates=False, use_blockchain=False)
    
    # Log the start of the experiment
    exp.logger.info(f"Running experiment: {name}")

    # Start timer for the experiment
    timer = Timer(f"{name} Timer")
    timer.start()

    # # Use the correct config file path and port
    # sumo_cfg = os.path.join(
    #     os.path.dirname(__file__),
    #     "..", "..", "SUMO", "Built Sims", "StraightAway5", "straightaway5.sumocfg"
    # )
    
    # sumo_cfg - the path to the SUMO configuration file
    sumo_cfg = os.path.join(
        os.path.dirname(__file__),
        "..", "..", "SUMO", "Built Sims", "StraightAway6", "straightaway6.sumocfg"
    )
    
    # Make sure the path is absolute
    sumo_cfg = os.path.abspath(sumo_cfg)
    
    # port - the port to connect to SUMO
    port = SUMO_PORT_DYNAMIC_SPAWN

    # # Check config file exists
    # if not check_file_exists(sumo_cfg, "SUMO straightaway5 configuration file"):
    #     if logger:
    #         logger.error(f"Config file not found: {sumo_cfg}")
    #     return

    # Check config file exists
    if not check_file_exists(sumo_cfg, "SUMO straightaway6 configuration file"):
        
        # If the config file does not exist, log an error and return
        if logger:
            logger.error(f"Config file not found: {sumo_cfg}")
            
        return
    
    # Start SUMO and connect via TraCI
    proc, traci, _, temp_config, temp_output_dir = start_sumo_simulation(
        file_path=sumo_cfg,
        is_config=True,
        port=port,
        sumo_binary=TEST_1_LEVEL_1_SUMO_BINARY,
        connect_traci=True,
        sumo_tools_path=SUMO_TOOLS_PATH
    )

    # If SUMO or TraCI failed to start, exit early
    if proc is None or traci is None:
        
        # Log an error if SUMO or TraCI could not be started
        if logger:
            logger.error("Failed to start SUMO or connect to TraCI.")
            
        return

    # throughput - Initialize throughput counter
    throughput = 0
    
    # Try to run the simulation
    try:
        total_steps = TEST_1_LEVEL_1_TOTAL_STEPS
        car_counter = 0
        active_cars = {}
        car_type = "car"
        car_route = "route1"

        # Main simulation loop
        for step in range(total_steps):
            
            # Exit if we've reached total_steps
            if step >= total_steps - 1:
                print(f"\nReached max steps ({total_steps}). Ending simulation.")
                break
            
            # Run a simulation step
            traci.simulationStep()
            
            # sim_time - Get the current simulation time
            sim_time = traci.simulation.getTime()

            # Check each active car to see if it has finished its route
            for car_id in list(active_cars.keys()):
                
                # If the car is no longer in the simulation, count it as finished
                if car_id not in traci.vehicle.getIDList():
                    
                    # Increment throughput
                    throughput += 1
                    
                    # If print_data is True, print the car ID and step it finished at
                    if print_data:
                        print(f"{car_id} finished at step {step}")
                    
                    # Remove the car from active_cars
                    del active_cars[car_id]

            # Spawn a new car if no active cars are present and we're past spawn step
            if not active_cars and step >= TEST_1_LEVEL_1_SPAWN_STEP:
                
                # car_counter - Increment the car counter whenever a new car is spawned
                car_counter += 1
                
                # new_car_id - Generate a new car ID
                new_car_id = f"car{car_counter}"
                
                # Add the new car to the simulation
                traci.vehicle.add(
                    vehID=new_car_id,
                    routeID=car_route,
                    typeID=car_type,
                    depart=sim_time
                )
                
                # Add the new car to active_cars
                active_cars[new_car_id] = step
                
                # If print_data is True, print the new car ID and step it was spawned at
                if print_data:
                    print(f"Spawned {new_car_id} at step {step}")

            # Every 100 steps, if print_data is True, print the current step and active cars
            if print_data and step % 100 == 0:
                print(f"Step {step}: Active cars: {list(active_cars.keys())}, Throughput: {throughput}")
                exp.logger.info(f"Step {step}: Active cars: {list(active_cars.keys())}, Throughput: {throughput}")

        # Log and print final throughput
        exp.logger.info(f"Experiment {name} throughput: {throughput} cars finished in {total_steps} steps.")
        print(f"\nExperiment {name} throughput: {throughput} cars finished in {total_steps} steps.")

    # If an exception occurs during the simulation, log and print the error
    except Exception as e:
        exp.logger.error(f"[{name}] Error: {e}")
        print(f"[{name}] Error: {e}")

    # Ensure we always clean up SUMO and TraCI connections, even if an error occurs
    finally:
        
        # Clean up SUMO and TraCI connections and temporary files
        cleanup_sumo_and_traci(proc, port, traci)
        
        # If temp_config and temp_output_dir were created, clean them up
        if temp_config and os.path.exists(temp_config):
            
            try:
                # Attempt to remove the temporary config file with unlink
                os.unlink(temp_config)
                
            except:
                # If unlink fails, log the error but do not raise an exception
                pass
        
        # If temp_output_dir exists, attempt to remove it
        if temp_output_dir and os.path.exists(temp_output_dir):
            
            try:
                # Attempt to remove the temporary output directory
                shutil.rmtree(temp_output_dir)
                
            except:
                # If rmtree fails, log the error but do not raise an exception
                pass

    # Stop timer and log/print experiment duration
    timer.stop()
    exp.logger.info(f"{name} completed in {timer.elapsed():.8f} seconds.")
    print(f"\n{name} completed in {timer.elapsed():.8f} seconds.\n")


##
# @brief Run Test_1_Level_2 experiment: RSU-car proximity logic and throughput in SUMO
# @param print_data If True, print simulation data to screen
# @details
#   Connects to straightaway6.sumocfg, spawns a car at step 1000, and whenever a car completes its route,
#   immediately spawns another identical car, for 51000 steps.
#   Implements RSU-car proximity logic: stops car for 2 seconds when within a specified range of RSU, then resumes.
#
# Steps:
#   1. Set up experiment parameters and logger
#   2. Start SUMO simulation and connect via TraCI
#   3. Spawn cars dynamically after a certain step
#   4. Stop cars for 2 seconds when near RSU, then resume
#   5. Track and count cars that finish their routes (throughput)
#   6. Print and log throughput results
#   7. Clean up SUMO and temporary files
##
def run_test_1_level_2_experiment(print_data=True):

    # Increment experiment count and set up experiment parameters
    global experiment_count
    experiment_count += 1
    name = f"Test_1_Level_2_{experiment_count}"

    # exp - Create an Experiment instance without ZoKrates or blockchain
    exp = Experiment(name, f"Vehicle_{experiment_count}", f"RSU_{experiment_count}", None, use_zokrates=False, use_blockchain=False)
    
    # Log the start of the experiment
    exp.logger.info(f"Running experiment: {name}")

    # Start timer for the experiment
    timer = Timer(f"{name} Timer")
    timer.start()

    # sumo_cfg - the path to the SUMO configuration file
    sumo_cfg = os.path.join(
        os.path.dirname(__file__),
        "..", "..", "SUMO", "Built Sims", "StraightAway6", "straightaway6.sumocfg"
    )
    sumo_cfg = os.path.abspath(sumo_cfg)
    
    # port - the port to connect to SUMO
    port = SUMO_PORT_RSUWITHDELAY

    # Check config file exists, return if not
    if not check_file_exists(sumo_cfg, "SUMO straightaway6 configuration file"):
        
        # Log an error if the config file does not exist
        if logger:
            logger.error(f"Config file not found: {sumo_cfg}")
            
        return

    # Start SUMO and connect via TraCI using the unified function
    proc, traci, _, temp_config, temp_output_dir = start_sumo_simulation(
        file_path=sumo_cfg,
        is_config=True,
        port=port,
        sumo_binary=TEST_1_LEVEL_2_SUMO_BINARY,
        connect_traci=True,
        step_length=TEST_1_LEVEL_2_STEP_LENGTH,
        sumo_tools_path=SUMO_TOOLS_PATH
    )

    # If SUMO or TraCI failed to start, exit early
    if proc is None or traci is None:
        
        # Log an error if SUMO or TraCI could not be started
        if logger:
            logger.error("Failed to start SUMO or connect to TraCI.")
        return
    
    # flags_lowered = 0
    
    # flags_raised - Initialize flags raised counter
    flags_raised = 0
    
    # throughput - Initialize throughput counter
    throughput = 0
    
    # Try to run the simulation
    try:
        total_steps = TEST_1_LEVEL_2_TOTAL_STEPS
        car_counter = 0
        active_cars = {}
        car_type = "car"
        car_route = "route1"
        finished_cars = 0

        # cars_that_triggered_stop - Set to track cars that triggered a stop
        cars_that_triggered_stop = set()

        # stopped_cars - Dictionary to track cars that are currently stopped and when they should resume
        stopped_cars = {}

        # Main simulation loop
        for step in range(total_steps):
            
            # Check each stopped car to see if it should resume
            for car_id in list(stopped_cars.keys()):
                
                # If the car has reached its resume step
                if step >= stopped_cars[car_id]:
                    
                    # Attempt to resume the car's speed
                    try:
                        
                        # If the car is still in the simulation, resume its speed
                        if car_id in traci.vehicle.getIDList():
                            traci.vehicle.setSpeed(car_id, -1)
                            
                            # If print_data is True, print the resuming message
                            if print_data:
                                print(f"*** RESUMING: Car {car_id} is resuming normal speed at step {step} ***")
                                
                    # If an error occurs while resuming the car, log the error
                    except Exception as e:
                        print(f"Could not resume car {car_id}: {e}")
                        
                    # Remove the car from stopped_cars since it has resumed
                    del stopped_cars[car_id]

            # rsu_ids - List to hold RSU IDs
            rsu_ids = []
            
            # car_ids - List to hold car IDs
            car_ids = []
            
            # Try to compute RSU-car interactions
            try:
                
                # rsu_ids - Get all RSU IDs in the simulation
                rsu_ids = [vid for vid in traci.vehicle.getIDList() if traci.vehicle.getTypeID(vid) == "rsu"]
                
                # car_ids - Get all car IDs in the simulation that are not in stopped_cars
                car_ids = [vid for vid in traci.vehicle.getIDList() if traci.vehicle.getTypeID(vid) == "car" and vid not in cars_that_triggered_stop]
                
                # For each car ID, check if it is within range of any RSU
                for car_id in car_ids:
                    
                    # If the car is already stopped, skip it
                    if car_id in stopped_cars:
                        continue
                    
                    # If there are no RSUs, skip to the next car
                    if not rsu_ids:
                        continue
                    
                    # rsu_pos - Get the position of the first RSU
                    rsu_pos = traci.vehicle.getPosition(rsu_ids[0])
                    
                    # car_pos - Get the position of the current car
                    car_pos = traci.vehicle.getPosition(car_id)
                    
                    # dx - Calculate the difference in x-coordinates
                    dx = rsu_pos[0] - car_pos[0]
                    
                    # dy - Calculate the difference in y-coordinates
                    dy = rsu_pos[1] - car_pos[1]
                    
                    # dist - Calculate the distance between the RSU and the car
                    dist = (dx**2 + dy**2) ** 0.5
                    
                    # Check if car is within rsu range
                    if dist < TEST_1_LEVEL_2_RSU_RANGE:
                        
                        # Try to stop the car
                        try:
                            
                            # current_speed - Get the current speed of the car
                            current_speed = traci.vehicle.getSpeed(car_id)
                            
                            # Stop the car by setting its speed to 0
                            traci.vehicle.setSpeed(car_id, 0)
                            
                            # resume_step - Calculate the step at which the car should resume
                            resume_step = step + TEST_1_LEVEL_2_TIME_TO_WAIT
                            
                            # Setup the stopped_cars dictionary with the car ID and resume step
                            stopped_cars[car_id] = resume_step
                            
                            # Add the car ID to the cars_that_triggered_stop set
                            cars_that_triggered_stop.add(car_id)
                            
                            # Increment flags_raised counter
                            flags_raised += 1
                            
                            # Print debug information
                            print(f"*** STOPPING: Car {car_id} at step {step} (distance: {dist:.2f} m, speed: {current_speed:.2f} m/s) ***")
                            print(f"*** Will resume at step {resume_step} ***")
                        
                        # If an error occurs while stopping the car, log the error
                        except Exception as e:
                            print(f"Could not stop car {car_id}: {e}")
            
            # If an error occurs while computing RSU-car interactions, log the error every 1000 steps
            except Exception as e:
                if step % 1000 == 0:
                    print(f"Step {step}: Could not compute RSU-car interactions: {e}")

            # Exit if we've reached total_steps
            if step >= total_steps - 1:
                
                # Print final statistics and exit
                print(f"\nReached max steps ({total_steps}). Ending simulation.")
                print(f"Total cars finished: {finished_cars}")
                print(f"Flags raised (cars stopped): {flags_raised}")
                print(f"Cars that triggered stop: {len(cars_that_triggered_stop)}")
                break

            # Run a simulation step
            traci.simulationStep()
            
            # sim_time - Get the current simulation time
            sim_time = traci.simulation.getTime()

            # Iterate through active cars to check if they have finished their routes
            for car_id in list(active_cars.keys()):
                
                # If the car is no longer in the simulation, count it as finished
                if car_id not in traci.vehicle.getIDList():
                    
                    # Increment finished cars and throughput
                    finished_cars += 1
                    throughput += 1
                    
                    # If print_data is True, print the car ID and step it finished at
                    if print_data:
                        print(f"{car_id} finished at step {step}")
                        
                    # Remove the car from active_cars
                    del active_cars[car_id]

            # If no active cars are present and we're past spawn step
            if not active_cars and step >= TEST_1_LEVEL_2_SPAWN_STEP:
                
                # Increment the car counter and set its ID
                car_counter += 1
                new_car_id = f"car{car_counter}"
                
                # Add the new car to the simulation
                traci.vehicle.add(
                    vehID=new_car_id,
                    routeID=car_route,
                    typeID=car_type,
                    depart=sim_time
                )
                
                # Add the new car to active_cars with the current step
                active_cars[new_car_id] = step
                
                # If print_data is True, print the new car ID and step it was spawned at
                if print_data:
                    print(f"Spawned {new_car_id} at step {step}")

            # Print and log status every 1000 steps
            if step % 1000 == 0:
                print(f"Step {step}: Active cars: {list(active_cars.keys())}, Total finished cars: {finished_cars}")

            # If print_data and DEBUG_MODE are True, print vehicle IDs and positions every step
            if print_data and DEBUG_MODE:
                
                # Get the list of vehicle IDs in the simulation and print them
                veh_ids = traci.vehicle.getIDList()
                print(f"Step {step}: Vehicles in sim: {veh_ids}")
                
                # For each vehicle ID, get and print its position
                for car_id in veh_ids:
                    
                    # Attempt to get the position of the vehicle
                    try:
                        pos = traci.vehicle.getPosition(car_id)
                        print(f"Step {step}: {car_id} position: {pos}")
                        
                    # If an error occurs while getting the position, log the error
                    except Exception as e:
                        print(f"Step {step}: Could not get position for {car_id}: {e}")

        # Log and print final throughput
        exp.logger.info(f"Experiment {name} throughput: {throughput} cars finished in {total_steps} steps.")
        print(f"\nExperiment {name} throughput: {throughput} cars finished in {total_steps} steps.")

    # If an exception occurs during the simulation, log and print the error
    except Exception as e:
        exp.logger.error(f"[{name}] Error: {e}")
        print(f"[{name}] Error: {e}")

    # Ensure we always clean up SUMO and TraCI connections, even if an error occurs
    finally:
        
        # Clean up SUMO and TraCI connections
        cleanup_sumo_and_traci(proc, port, traci)
        
        # If temp_config and temp_output_dir were created, clean them up
        if temp_config and os.path.exists(temp_config):
            try: 
                os.unlink(temp_config)
            except: 
                pass
        
        # If temp_output_dir exists, attempt to remove it
        if temp_output_dir and os.path.exists(temp_output_dir):
            try: 
                shutil.rmtree(temp_output_dir)
            except: 
                pass

    # Stop timer and log/print experiment duration
    timer.stop()
    exp.logger.info(f"{name} completed in {timer.elapsed():.8f} seconds.")
    print(f"\n{name} completed in {timer.elapsed():.8f} seconds.\n")


# Stub for future Test_1_Level_3 experiment; OTP integration
def run_test_1_level_3_experiment(print_data=True):
    return


# Stub for future Test_1_Level_4 experiment; ZKP integration
def run_test_1_level_4_experiment(print_data=True):
    return


##
# @brief Runs all base experiments for ZKP/blockchain and SUMO throughput/proximity logic
# @details
#   Sets up logging, cleans up ZoKrates files, and runs a sequence of experiments:
#   - Basic dummy circuit experiment
#   - Auth circuit experiment
#   - Test_1_Level_1 (dynamic car spawning throughput)
#   - Test_1_Level_2 (RSU-car proximity logic)
#   Logs and prints results for each experiment
#
# Steps:
#   1. Set up logging and clean up ZoKrates files
#   2. Run basic dummy circuit experiment
#   3. Run cryptographically meaningful auth circuit experiment
#   4. Run Test_1_Level_1 experiment (dynamic car spawning throughput)
#   5. Run Test_1_Level_2 experiment (RSU-car proximity logic)
#   6. Log completion of base experiments
##
def base_experiments_test():
    
    # Set up logging
    setup_logging()
    
    # Log the start of the base experiments test
    if logger:
        logger.info("Starting base experiments test")
    
    # Ensure no old files interfere
    cleanup_zokrates_files()  
    
    # Experiment header
    print("\n=== Running Basic Dummy Circuit Experiment ===")
    
    # Log the start of the basic dummy circuit experiment
    if logger:
        logger.info("Running Basic Dummy Circuit Experiment")
        
    # Run the demo experiment
    run_demo_experiment()
    
    # Experiment header
    print("\n=== Running Cryptographically Meaningful Auth Circuit Experiment ===")
    
    # Log the start of the cryptographically meaningful auth circuit experiment
    if logger:
        logger.info("Running Cryptographically Meaningful Auth Circuit Experiment")
        
    # Run the auth experiment
    run_auth_experiment()
    
    # Experiment header
    print("\n=== Running Test_1_Level_1 Experiment (Dynamic Car Spawning Throughput) ===")
    
    # Log the start of the Test_1_Level_1 experiment
    if logger:
        logger.info("Running Test_1_Level_1 Experiment (Dynamic Car Spawning Throughput)")
    
    # Run Test_1_Level_1 experiment
    run_test_1_level_1_experiment(print_data=True)

    # Experiment header
    print("\n=== Running Test_1_Level_2 Experiment (RSU-Car Proximity Logic) ===")
    
    # Log the start of the Test_1_Level_2 experiment
    if logger:
        logger.info("Running Test_1_Level_2 Experiment (RSU-Car Proximity Logic)")
        
    # Run Test_1_Level_2 experiment
    run_test_1_level_2_experiment(print_data=True)

    # Log the completion of the base experiments test
    if logger:
        logger.info("Base experiments test completed")
    
    
if __name__ == "__main__":
    
    base_experiments_test()

