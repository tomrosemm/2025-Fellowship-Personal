import secrets
import os
import time
import random

from experiment import Experiment

from vehicle import Vehicle
from rsu import RSU

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

# Uncomment if blockchain_interface is used
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
    Experiment.DEBUG_MODE = enabled

def clear_console():
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')

def run_single_experiment():
    """
    Example: Run a single experiment using the Experiment class with dummy.zok.
    """
    global experiment_count
    experiment_count += 1
    name = f"Experiment_{experiment_count}"
    vehicle_id = f"Vehicle_{experiment_count}"
    rsu_id = f"RSU_{experiment_count}"
    zokrates_circuit_path = "dummy.zok"  # Simple addition circuit
    exp = Experiment(name, vehicle_id, rsu_id, zokrates_circuit_path)
    exp.run()
    exp.report()

def run_auth_experiment():
    """
    Run an experiment using the auth.zok circuit which provides a cryptographically
    meaningful zero-knowledge proof for authentication.
    """
    global experiment_count
    experiment_count += 1
    name = f"Auth_Experiment_{experiment_count}"
    vehicle_id = f"Auth_Vehicle_{experiment_count}"
    rsu_id = f"Auth_RSU_{experiment_count}"
    zokrates_circuit_path = "auth.zok"  # Cryptographically meaningful circuit
    exp = Experiment(name, vehicle_id, rsu_id, zokrates_circuit_path)
    exp.run()
    exp.report()


if __name__ == "__main__":
    # Run both experiments
    print("\n=== Running Basic Dummy Circuit Experiment ===")
    run_single_experiment()
    
    print("\n=== Running Cryptographically Meaningful Auth Circuit Experiment ===")
    run_auth_experiment()