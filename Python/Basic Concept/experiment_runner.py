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

"""Clears the console screen based on the operating system."""
def clear_console():
    if os.name == 'nt':         # For Windows
        os.system('cls')
    else:                       # For macOS/Linux
        os.system('clear')