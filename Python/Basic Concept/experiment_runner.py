import secrets 
import os
import time
import random

from vehicle import Vehicle
from rsu import RSU

from zokrates_interface import (
    run_zokrates_compile,
    run_zokrates_setup,
    run_zokrates_compute_witness,
    run_zokrates_generate_proof,
    run_zokrates_verify,
    cleanup_zokrates_files,
    set_debug_mode as set_zokrates_debug_mode
)

from blockchain import simulate_blockchain_verification, set_debug_mode as set_blockchain_debug_mode
from sumo_interface import test_sumo_connection_wrapper, set_debug_mode as set_sumo_debug_mode
# from blockchain_interface import set_debug_mode as set_blockchain_interface_debug_mode

DEBUG_MODE = False

experiment_count = 0
tested = 0

def set_debug_mode(enabled):
    """Enable or disable debug mode for detailed output."""
    global DEBUG_MODE
    DEBUG_MODE = enabled
    set_zokrates_debug_mode(enabled)
    set_blockchain_debug_mode(enabled)
    set_sumo_debug_mode(enabled)
    # set_blockchain_interface_debug_mode(enabled)

"""Clears the console screen based on the operating system."""
def clear_console():
    if os.name == 'nt':         # For Windows
        os.system('cls')
    else:                       # For macOS/Linux
        os.system('clear')


"""
Template for a new experiment.
This function should be customized for each specific experiment.
"""
def templateExperiment():
    global experiment_count
    experiment_count += 1
    print(f"Running Experiment {experiment_count}...")

    # Example: Initialize a Vehicle and RSU
    vehicle = Vehicle("Vehicle_" + str(experiment_count), "dummy_zok_path.zok")
    rsu = RSU("RSU_" + str(experiment_count))

    # Example: Run ZoKrates compilation
    if not run_zokrates_compile(vehicle.zokrates_circuit_path):
        print("ZoKrates compilation failed.")
        return

    # Example: Run ZoKrates setup
    if not run_zokrates_setup():
        print("ZoKrates setup failed.")
        return

    # Example: Compute witness
    if not run_zokrates_compute_witness(vehicle.zokrates_circuit_path, vehicle.get_witness_input()):
        print("Witness computation failed.")
        return

    # Example: Generate proof
    if not run_zokrates_generate_proof():
        print("Proof generation failed.")
        return

    # Example: Verify proof
    if not run_zokrates_verify():
        print("Proof verification failed.")
        return

    # Simulate blockchain verification
    vehicle_id = vehicle.id
    zkp_proof = "dummy_zkp_proof"
    timestamp = int(time.time())
    verification_result = True  # Simulated result

    if simulate_blockchain_verification(vehicle_id, zkp_proof, timestamp, verification_result):
        print(f"Experiment {experiment_count} completed successfully.")
    else:
        print(f"Experiment {experiment_count} failed during blockchain verification.")