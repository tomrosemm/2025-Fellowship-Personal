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
##

# Imports
import secrets
import os
import time
import random

from experiment import Experiment
from vehicle import Vehicle
from rsu import RSU
from timer import Timer
from utilities import clear_console

from zokrates_interface import (
    run_zokrates_compile,
    run_zokrates_setup,
    run_zokrates_compute_witness,
    run_zokrates_generate_proof,
    run_zokrates_verify,
    cleanup_zokrates_files,
    hex_to_field_array,
    set_debug_mode as set_zokrates_debug_mode
)

from blockchain import simulate_blockchain_verification, set_debug_mode as set_blockchain_debug_mode
from sumo_interface import test_sumo_connection_wrapper, set_debug_mode as set_sumo_debug_mode
from settings import (
    DEBUG_MODE as DEFAULT_DEBUG_MODE,
    ZOKRATES_DUMMY_CIRCUIT,
    ZOKRATES_AUTH_CIRCUIT
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
    
    # Generate a vehicle ID and RSU ID for this experiment
    vehicle_id = f"Vehicle_{experiment_count}"
    rsu_id = f"RSU_{experiment_count}"
    
    # Path to the ZoKrates circuit file from settings
    zokrates_circuit_path = ZOKRATES_DUMMY_CIRCUIT
    
    # Create an Experiment instance with the specified parameters
    exp = Experiment(name, vehicle_id, rsu_id, zokrates_circuit_path)
    
    # Run the experiment and report results
    exp.run()
    exp.report()
    
    # Clean up ZoKrates-generated files after the experiment
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
    
    # Generate a vehicle ID and RSU ID for this experiment
    vehicle_id = f"Auth_Vehicle_{experiment_count}"
    rsu_id = f"Auth_RSU_{experiment_count}"
    
    # Path to the ZoKrates circuit file from settings
    zokrates_circuit_path = ZOKRATES_AUTH_CIRCUIT
    
    # Create an Experiment instance with the specified parameters
    exp = Experiment(name, vehicle_id, rsu_id, zokrates_circuit_path)
    
    # Run the experiment and report results
    exp.run()
    exp.report()
    
    # Clean up ZoKrates-generated files after the experiment
    cleanup_zokrates_files()


def base_experiments_test():
    
    # Ensure no old files interfere
    cleanup_zokrates_files()  
    
    # Run both experiments
    print("\n=== Running Basic Dummy Circuit Experiment ===")
    run_demo_experiment()
    
    print("\n=== Running Cryptographically Meaningful Auth Circuit Experiment ===")
    run_auth_experiment()
    
    
if __name__ == "__main__":
    
    ## @brief Main entry point for running experiments.
    base_experiments_test()
    
    