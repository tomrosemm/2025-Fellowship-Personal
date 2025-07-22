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
    Example: Run a single experiment using the Experiment class.
    """
    global experiment_count
    experiment_count += 1
    name = f"Experiment_{experiment_count}"
    vehicle_id = f"Vehicle_{experiment_count}"
    rsu_id = f"RSU_{experiment_count}"
    zokrates_circuit_path = "auth.zok"
    exp = Experiment(name, vehicle_id, rsu_id, zokrates_circuit_path)
    exp.run()
    exp.report()


if __name__ == "__main__":
    run_single_experiment()