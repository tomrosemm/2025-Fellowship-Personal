##
# @file framework.py
# @author Tom Rose
#
# @brief
#   Framework module to hold the proper implementation of the framework, and then draw on it for testing/experiments
#   Currently, this is a placeholder file, as there are enough details about vehicle and rsu behavior that still need to be worked out that attempts to implement it properly would be premature.
#   The logic in the run_test_1_level_2_experiment() function is a starting point for the basic implementation,
#   though it doesn't use the vehicle or RSU classes yet, just direct execution of the behavior desired.
#   generate_otp() and create_zkp() can then be used to build out the OTP and ZKP portions of the framework, with the blockchain interactions available and very roughly in place to be integrated later
#
#   Breakdown of the workflow, based on the original paper's description:
#
#   Part One
#   1. Vehicle generates an OTP using unique secret and timestamp
#   2. OTP is embedded into a ZKP, proving the OTP valid without revealing the secret
#   3. ZKP is sent to the RSU, where it is verified
#   4. Upon successful verification, the RSU sends a signal to the vehicle authenticating it and proceeding with session
#
#   Part Two
#   1. ZKP-OTP proof is submitted to RSU
#   2. RSU invokes a smart contract on the blockchain, verifying the ZKP-OTP proof
#   3. The blockchain logs the event, including anonymized record of the vehicle’s identity and authentication status
#   4. The outcome is returned to the infrastructure, which grants or denies access.
##

## Imports
# Classes and functions
from vehicle import Vehicle
from rsu import RSU
from timer import Timer
from zkp import generate_zkp_proof_simulated

from settings import (
    SUMO_STRAIGHTAWAY6_CONFIG_FILE
)

from utilities import (
    # clear_console,
    check_file_exists
)

from sumo_interface import (
    set_debug_mode as set_sumo_debug_mode,
    start_sumo_simulation,
    cleanup_sumo_and_traci,
    kill_processes_on_port,
    test_sumo_connection_wrapper,
    cleanup_traci_connection,
    run_sumo_simulation_flexible
)

from zokrates_interface import (
    run_zokrates_workflow,
    run_zokrates_compile,
    run_zokrates_setup,
    run_zokrates_compute_witness,
    run_zokrates_generate_proof,
    run_zokrates_verify,
    cleanup_zokrates_files
)

from blockchain import (
    simulate_blockchain_verification,
    set_debug_mode as set_blockchain_debug_mode
)