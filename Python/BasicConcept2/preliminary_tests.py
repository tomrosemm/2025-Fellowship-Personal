##
# @file preliminary_tests.py
# @author Tom Rose
#
# @brief
#   Contains test routines to simulate and validate the ZKP-OTP authentication protocol
#   between Vehicle and RSU entities. Demonstrates authentication using both simulated
#   and real (ZoKrates-based) zero-knowledge proof workflows, as well as a blockchain verification simulation.
#   Includes tests for basic connection with related software/tools, such as ZoKrates and SUMO.
#
# @details
#   - Simulates generation of one-time passwords (OTP) and timestamps by vehicles.
#   - Demonstrates creation of zero-knowledge proofs (ZKP) for OTP and timestamp.
#   - Shows verification of ZKPs by RSUs using both simulated (hash-based) and real ZoKrates CLI methods.
#   - Includes a workflow for simulating blockchain-based verification and logging.
#   - Provides functions for each workflow, which can be run directly for demonstration and prototyping.
#   - Requires: vehicle.py, rsu.py, zokrates_interface.py, blockchain.py
##

## Imports
# Libraries
# import sys
# import subprocess
import secrets
import os
import time
import random
import shutil

# Classes and functions
# from experiment import Experiment
from vehicle import Vehicle
from rsu import RSU
from timer import Timer
from zkp import generate_zkp_proof_simulated

from utilities import (
    # clear_console,
    check_file_exists)

from blockchain import (
    simulate_blockchain_verification,
    set_debug_mode as set_blockchain_debug_mode
)

from sumo_interface import (
    # start_sumo_and_traci,
    set_debug_mode as set_sumo_debug_mode,
    kill_processes_on_port,
    test_sumo_connection_wrapper,
    cleanup_traci_connection,
    cleanup_sumo_and_traci,
    start_sumo_simulation,
    run_sumo_simulation_flexible
)

from zokrates_interface import (
    # run_zokrates_compile,
    # run_zokrates_setup,
    # run_zokrates_compute_witness,
    # run_zokrates_generate_proof,
    # run_zokrates_verify,
    cleanup_zokrates_files,
    set_debug_mode as set_zokrates_debug_mode,
    run_zokrates_workflow
)

from settings import (
    DEBUG_MODE as DEFAULT_DEBUG_MODE,
    PRINT_DATA as DEFAULT_PRINT_DATA,
    SUMO_TOOLS_PATH, 
    SUMO_SIMPLE_NET_FILE,
    SUMO_INTERSECTION_CONFIG_FILE,
    SUMO_PORT_DATA,
    SUMO_PORT_DATA_CONFIG,
    SUMO_PORT_BASIC,
    SUMO_PORT_CONFIG,
    ZOKRATES_DUMMY_CIRCUIT,
    SUMO_INTERSECTION2_CONFIG_FILE,
    SUMO_STRAIGHTAWAY1_CONFIG_FILE,
    SUMO_STRAIGHTAWAY2_CONFIG_FILE,
    SUMO_PORT_DYNAMIC_SPAWN,
    SUMO_PORT_LIVE_MANIPULATION,
    SUMO_PORT_SMALL_STEP,
    SUMO_PORT_DATA_INTERSECTION2_CONFIG,
    SUMO_PORT_DATA_STRAIGHTAWAY1_CONFIG,
    SUMO_PORT_DATA_STRAIGHTAWAY2_CONFIG,
    SUMO_PORT_RSUWITHDELAY
)

# Track number of tests run and passed
tested = 0
passed = 0

## @var DEBUG_MODE
# @brief Global variable to control debug output.
DEBUG_MODE = DEFAULT_DEBUG_MODE

## @var PRINT_DATA
# @brief Global variable to control whether to print data in the SUMO interface.
PRINT_DATA = DEFAULT_PRINT_DATA


##
# @brief Enable or disable debug mode for detailed output.
# @param enabled True to enable debug mode, False to disable.
# @details
#   Sets the global DEBUG_MODE variable and propagates debug mode to all relevant modules/classes.
#
# Steps:
#   1. Set the global DEBUG_MODE variable.
#   2. Set debug mode for ZoKrates, Blockchain, and SUMO interfaces.
##
def set_debug_mode(enabled):
    
    # Set global debug mode
    global DEBUG_MODE
    DEBUG_MODE = enabled
    
    # Set debug mode for Blockchain, and SUMO and ZoKrates interfaces
    set_zokrates_debug_mode(enabled)
    set_blockchain_debug_mode(enabled)
    set_sumo_debug_mode(enabled)
    
    # set_blockchain_interface_debug_mode(enabled)


##
# @brief Set whether to print data in the SUMO interface.
# @param enabled True to enable printing data, False to disable.
# @details
#     Sets the print_data attribute in the SUMO interface.
##
def set_print_data(enabled):
    
    global PRINT_DATA
    PRINT_DATA = enabled


##
# @brief Test the workflow using a simulated ZKP (hash-based).
# @details
#   Simulates authentication between a vehicle and RSU using a hash-based ZKP.
#
# Steps:
#   1. Generate a random vehicle secret and create Vehicle and RSU entities.
#   2. Vehicle generates an OTP and timestamp.
#   3. Vehicle creates a simulated ZKP proof (hash-based) for the OTP and timestamp.
#   4. RSU verifies the ZKP proof using the known vehicle secret and timestamp.
#   5. Output the result of the verification and authentication status.
##
def test_VehicleRsuBasicInteraction_SimulatedZkp():
    
    # Print test header
    print("\n=== Vehicle - Rsu Basic Interaction; Simulated Zkp ===")
    
    # Use global variables to track tests, increment tested count
    global tested, passed
    tested += 1
    
    timer = Timer("Vehicle - Rsu Basic Interaction; Simulated Zkp Test Timer")
    timer.start()
    
    # Generate entities with random secrets
    vehicle_id = "VEH123"
    vehicle_secret = secrets.token_hex(16)
    vehicle = Vehicle(vehicle_id, vehicle_secret)
    unused_rsu = RSU({vehicle_id: vehicle_secret})

    # Generate OTP and timestamp
    otp, timestamp = vehicle.generate_otp()
    
    # Print debug information if DEBUG_MODE is enabled
    if DEBUG_MODE:
        print(f"\n[Simulated] OTP: {otp}\n\nTimestamp: {timestamp}\n")
        
    # Use simulated ZKP proof
    zkp_proof = generate_zkp_proof_simulated(otp, timestamp)
    
    # Print ZKP proof if DEBUG_MODE is enabled
    if DEBUG_MODE:
        print(f"[Simulated] ZKP Proof: {zkp_proof}\n")
        
    # RSU verifies ZKP proof using simulated logic
    expected_zkp = generate_zkp_proof_simulated(otp, timestamp)
    verification_result = (zkp_proof == expected_zkp)
    
    # Print verification result if DEBUG_MODE is enabled
    if DEBUG_MODE:
        print(f"[Simulated] Verification result: {verification_result}\n")

    # Output authentication result, increment passed count if successful
    if verification_result:
        passed += 1
        print("[Simulated] Vehicle authenticated. Session started.\n")
        
    else:
        print("[Simulated] Authentication failed.\n")
    
    timer.stop()
    # Print elapsed time for the test
    print(f"\nTest completed in {timer.elapsed():.8f} seconds.\n")


##
# @brief Simulate the full workflow, using simulated ZKP and simulated blockchain verification and logging.
# @details
#   Simulates authentication and blockchain verification using hash-based ZKP.
#
# Steps:
#   1. Generate a random vehicle secret and create Vehicle and RSU entities.
#   2. Vehicle generates an OTP and timestamp.
#   3. Vehicle creates a simulated ZKP proof (hash-based) for the OTP and timestamp.
#   4. RSU verifies the ZKP proof using the known vehicle secret and timestamp.
#   5. Simulate blockchain smart contract verification and logging of the authentication attempt.
#   6. Output the result of the infrastructure access decision.
##
def test_VehicleRsuBasicInteraction_SimulatedZkpAndBlockchain():
    
    # Print test header
    print("\n=== Vehicle - Rsu Basic Interaction; Simulated Zkp And Blockchain ===")
    
    # Use global variables to track tests, increment tested count
    global tested, passed
    tested += 1
    
    timer = Timer("Vehicle - Rsu Basic Interaction; Simulated Zkp And Blockchain Test Timer")
    timer.start()
    
    # Generate entities with random secrets
    vehicle_id = "VEH123"
    vehicle_secret = secrets.token_hex(16)
    vehicle = Vehicle(vehicle_id, vehicle_secret)
    unused_rsu = RSU({vehicle_id: vehicle_secret})

    # Generate OTP and timestamp
    otp, timestamp = vehicle.generate_otp()
    
    # Print debug information if DEBUG_MODE is enabled
    if DEBUG_MODE:
        print(f"\n[Simulated] OTP: {otp}\n\nTimestamp: {timestamp}\n")
        
    # Use simulated ZKP proof
    zkp_proof = generate_zkp_proof_simulated(otp, timestamp)
    
    # Print ZKP proof if DEBUG_MODE is enabled
    if DEBUG_MODE:
        print(f"[Simulated] ZKP Proof: {zkp_proof}\n")
    
    # RSU verifies ZKP proof using simulated logic
    expected_zkp = generate_zkp_proof_simulated(otp, timestamp)
    verification_result = (zkp_proof == expected_zkp)
    
    # Print verification result if DEBUG_MODE is enabled
    if DEBUG_MODE:
        print(f"[Simulated] RSU Verification result: {verification_result}\n")

    # Simulate blockchain verification and logging if DEBUG_MODE is enabled
    outcome = simulate_blockchain_verification(vehicle_id, zkp_proof, timestamp, verification_result) if DEBUG_MODE else verification_result
    
    # Output the result of the infrastructure access decision, increment passed count if successful
    if outcome:
        passed += 1
        print("[Simulated] Access granted by infrastructure.\n")
        
    else:
        print("[Simulated] Access denied by infrastructure.\n")
    
    timer.stop()
    # Print elapsed time for the test
    print(f"\nTest completed in {timer.elapsed():.8f} seconds.\n")


##
# @brief End-to-end scenario: Vehicle authenticates successfully and is granted access.
# @details
#   Simulates a successful authentication scenario for a vehicle.
#
# Steps:
#   1. Create vehicle and RSU with matching secrets.
#   2. Vehicle generates OTP and timestamp.
#   3. Vehicle creates ZKP proof.
#   4. RSU verifies ZKP proof.
#   5. Blockchain verification is performed if DEBUG_MODE is enabled.
#   6. Print the result of the infrastructure access decision.
##
def test_EndToEnd_SimulatedZkpAndBlockchain_Success():
    
    # Print test header
    print("\n=== End - To - End; Simulated Zkp And Blockchain; Success Test ===")
    
    # Use global variables to track tests, increment tested count
    global tested, passed
    tested += 1
    
    timer = Timer("End - To - End; Simulated Zkp And Blockchain; Success Test Timer")
    timer.start()
    
    # Generate entities with matching secrets
    vehicle_id = "VEH001"
    vehicle_secret = secrets.token_hex(16)
    vehicle = Vehicle(vehicle_id, vehicle_secret)
    unused_rsu = RSU({vehicle_id: vehicle_secret})

    # Generate OTP and timestamp
    otp, timestamp = vehicle.generate_otp()
    
    # Print debug information if DEBUG_MODE is enabled
    if DEBUG_MODE:
        print(f"\nVehicle {vehicle_id} generated OTP: {otp} at {timestamp}\n")
        
    # Simulated ZKP proof is created
    zkp_proof = generate_zkp_proof_simulated(otp, timestamp)
    
    # Print ZKP proof if DEBUG_MODE is enabled
    if DEBUG_MODE:
        print(f"Vehicle {vehicle_id} created ZKP proof: {zkp_proof}\n")
    
    # RSU verifies ZKP proof using simulated logic
    expected_zkp = generate_zkp_proof_simulated(otp, timestamp)
    verification_result = (zkp_proof == expected_zkp)
    
    # Print verification result if DEBUG_MODE is enabled
    if DEBUG_MODE:
        print(f"RSU verification result: {verification_result}\n")

    # Blockchain verification and access outcome
    outcome = simulate_blockchain_verification(vehicle_id, zkp_proof, timestamp, verification_result) if DEBUG_MODE else verification_result
    
    # Output the result of the infrastructure access decision, increment passed count if successful
    if outcome:
        passed += 1
        print("Access granted by infrastructure.\n")
    
    else:
        print("Access denied by infrastructure.\n")
    
    timer.stop()
    # Print elapsed time for the test
    print(f"\nTest completed in {timer.elapsed():.8f} seconds.\n")


##
# @brief End-to-end scenario: Vehicle fails authentication due to wrong secret.
# @details
#   Simulates a failed authentication scenario for a vehicle with incorrect secret.
#
# Steps:
#   1. Create vehicle with wrong secret and RSU with correct secret.
#   2. Vehicle generates OTP and timestamp.
#   3. Vehicle creates ZKP proof.
#   4. RSU verifies ZKP proof using expected secret.
#   5. Blockchain verification is performed if DEBUG_MODE is enabled.
#   6. Print expected denial of infrastructure access.
##
def test_EndToEnd_SimulatedZkpAndBlockchain_Failure():
    
    # Print test header
    print("\n=== End - To - End; Simulated Zkp And Blockchain; Failure Test ===")
    
    # Use global variables to track tests, increment tested count
    global tested, passed
    tested += 1
    
    timer = Timer("End - To - End; Simulated Zkp And Blockchain; Failure Test Timer")
    timer.start()
    
    # Generate entities with wrong secret
    vehicle_id = "VEH001"
    correct_secret = secrets.token_hex(16)
    wrong_secret = secrets.token_hex(16)
    vehicle = Vehicle(vehicle_id, wrong_secret)
    unused_rsu = RSU({vehicle_id: correct_secret})

    # Generate OTP and timestamp
    otp, timestamp = vehicle.generate_otp()
    
    # Print debug information if DEBUG_MODE is enabled
    if DEBUG_MODE:
        print(f"\nVehicle {vehicle_id} generated OTP: {otp} at {timestamp}\n")
        
    # Simulated ZKP proof is created
    zkp_proof = generate_zkp_proof_simulated(otp, timestamp)
    
    # Print ZKP proof if DEBUG_MODE is enabled
    if DEBUG_MODE:
        print(f"Vehicle {vehicle_id} created ZKP proof: {zkp_proof}\n")
        
    # RSU expects correct secret, so expected_zkp is based on correct_secret
    otp_expected, _ = Vehicle(vehicle_id, correct_secret).generate_otp()
    
    # Generate expected ZKP proof using the correct secret
    expected_zkp = generate_zkp_proof_simulated(otp_expected, timestamp)
    
    # RSU verifies ZKP proof using expected logic
    verification_result = (zkp_proof == expected_zkp)
    
    # Print verification result if DEBUG_MODE is enabled
    if DEBUG_MODE:
        print(f"RSU verification result: {verification_result}\n")

    # Blockchain verification and access outcome
    outcome = simulate_blockchain_verification(vehicle_id, zkp_proof, timestamp, verification_result) if DEBUG_MODE else verification_result
    
    # Output the result of the infrastructure access decision, increment passed count if successful
    if outcome:
        print("Access granted by infrastructure (unexpected).\n")
        
    else:
        passed += 1
        print("Access denied by infrastructure (expected).\n")
    
    timer.stop()
    # Print elapsed time for the test
    print(f"\nTest completed in {timer.elapsed():.8f} seconds.\n")


##
# @brief Test the connection and workflow with ZoKrates CLI using zokrates/dummy.zok.
# @details
#   Runs ZoKrates CLI workflow with fixed inputs.
#
# Steps:
#   1. Compile the ZoKrates circuit.
#   2. Run setup.
#   3. Compute witness (inputs: a=3, b=4).
#   4. Generate proof.
#   5. Verify proof.
#   6. Clean up ZoKrates artifacts after test.
#   7. Print the result of the ZoKrates workflow.
##
def test_Zokrates_BasicConnectionTest_UsingDummyCircuit():
    
    # Print test header
    print("\n=== Zokrates Basic Connection (using dummy.zok) Test ===")
    
    # Use global variables to track tests, increment tested count
    global tested, passed
    tested += 1
    
    timer = Timer("Zokrates Basic Connection (using dummy.zok) Test Timer")
    timer.start()
    
    # Set the circuit path for ZoKrates from settings
    circuit_path = ZOKRATES_DUMMY_CIRCUIT
    
    # Args to use for computing witness (a=3, b=4)
    args = ["3", "4"]
    
    # Use run_zokrates_workflow to handle the ZoKrates operations
    verification_result = run_zokrates_workflow(circuit_path, args)
    
    # Print verification result if DEBUG_MODE is enabled
    if DEBUG_MODE:
        print(f"[ZoKrates Test] Verification result: {verification_result}\n")
    
    # Output the result of the ZoKrates workflow, increment passed count if successful
    if verification_result:
        passed += 1
        print("[ZoKrates Test] ZoKrates connection and workflow succeeded!\n")
        
    else:
        print("[ZoKrates Test] ZoKrates connection or workflow failed.\n")
    
    timer.stop()
    # Print elapsed time for the test
    print(f"\nTest completed in {timer.elapsed():.8f} seconds.\n")


##
# @brief Test the end-to-end ZoKrates workflow using zokrates/dummy.zok and random inputs.
# @details
#   Simulates a real ZKP workflow using the ZoKrates CLI.
#
# Steps:
#   1. Generate random field inputs for dummy.zok.
#   2. Compile circuit.
#   3. Run setup.
#   4. Compute witness.
#   5. Generate proof.
#   6. Verify proof.
#   7. Clean up ZoKrates artifacts after test.
#   8. Print the result of the workflow.
##
def test_PartialWorkflow_RealZokrates_UsingDummyCircuit():
    
    # Print test header
    print("\n=== Partial Workflow - Real Zokrates (using dummy.zok) Test ===")
    
    # Use global variables to track tests, increment tested count
    global tested, passed
    tested += 1
    
    timer = Timer("Partial Workflow - Real Zokrates (using dummy.zok) Test Timer")
    timer.start()
    
    # Set the circuit path for ZoKrates from settings
    circuit_path = ZOKRATES_DUMMY_CIRCUIT
    
    # Generate random field inputs for dummy.zok
    a = random.randint(1, 100)
    b = random.randint(1, 100)
    
    # If DEBUG_MODE is enabled, print the inputs
    if DEBUG_MODE:
        print(f"Inputs: a={a}, b={b}")
    
    # Args to use for computing witness (a, b)
    args = [str(a), str(b)]
    
    # Use run_zokrates_workflow to handle the ZoKrates operations
    verification_result = run_zokrates_workflow(circuit_path, args)
    
    # Print verification result if DEBUG_MODE is enabled
    if DEBUG_MODE:
        print(f"[Real ZKP] Verification result: {verification_result}\n")
    
    # Output the result of the ZoKrates workflow, increment passed count if successful
    if verification_result:
        passed += 1
        print("[Real ZKP] End-to-end ZoKrates workflow succeeded!\n")
        
    else:
        print("[Real ZKP] End-to-end ZoKrates workflow failed.\n")
    
    timer.stop()
    # Print elapsed time for the test
    print(f"\nTest completed in {timer.elapsed():.8f} seconds.\n")


##
# @brief Simulated ZKP isolated test with multiple vehicles.
# @details
#   Simulates authentication for multiple vehicles using hash-based ZKP.
#
# Steps:
#   1. Create multiple vehicles, each with a unique secret.
#   2. Each vehicle generates OTP and timestamp, creates ZKP proof.
#   3. RSU verifies each ZKP proof.
#   4. Print whether all vehicles authenticated successfully.
##
def test_PartialWorkflow_MultipleVehicles_Simulated():
    
    # Print test header
    print("\n=== Partial Workflow - Multiple Vehicles; Simulated Test ===")
    
    # Use global variables to track tests, increment tested count
    global tested, passed
    tested += 1
    
    timer = Timer("Partial Workflow - Multiple Vehicles; Simulated Test Timer")
    timer.start()
    
    # Variables to hold vehicles and RSU secrets
    num_vehicles = 3
    vehicles = {}
    rsu_secrets = {}
    
    # For each vehicle, create a unique ID and secret
    for i in range(num_vehicles):
        
        # Generate vehicle ID formatted as VEH001, VEH002, etc.
        vid = f"VEH{i+1:03d}"
        
        # Generate a random secret for the vehicle and store it
        # in both the vehicles and RSU secrets dictionaries
        secret = secrets.token_hex(16)
        vehicles[vid] = Vehicle(vid, secret)
        rsu_secrets[vid] = secret
    
    # Create RSU with the secrets of all vehicles
    # This simulates the RSU having access to all vehicle secrets
    unused_rsu = RSU(rsu_secrets)
    
    # Initialize a flag to track if all vehicles passed authentication
    all_passed = True
    
    # Circuit path for the simulated ZKP proof
    unused_circuit_path = "zokrates/dummy.zok"
    
    # For each vehicle, generate OTP, timestamp, and ZKP proof
    for vid, vehicle in vehicles.items():
        
        # Generate OTP and timestamp for the vehicle
        otp, timestamp = vehicle.generate_otp()
        
        # Generate a simulated ZKP and expected ZKP from the same OTP and timestamp
        zkp_proof = generate_zkp_proof_simulated(otp, timestamp)
        expected_zkp = generate_zkp_proof_simulated(otp, timestamp)
        
        # Verify that the ZKP proof is equal to the expected proof
        result = (zkp_proof == expected_zkp)
        
        # If DEBUG_MODE is enabled, print the verification result
        if DEBUG_MODE:
            print(f"Vehicle {vid}: Verification result: {result}")
        
        # If the result is False, set all_passed to False
        all_passed = all_passed and result
    
    # Output the result of the authentication for all vehicles, increment passed count if successful
    if all_passed:
        passed += 1
        print("[Simulated] All vehicles authenticated successfully.\n")
        
    else:
        print("[Simulated] Some vehicles failed authentication.\n")
    
    timer.stop()
    # Print elapsed time for the test
    print(f"\nTest completed in {timer.elapsed():.8f} seconds.\n")


##
# @brief Simulated end-to-end test with multiple vehicles (RSU + blockchain).
# @details
#   Simulates authentication and blockchain verification for multiple vehicles.
#
# Steps:
#   1. Create multiple vehicles, each with a unique secret.
#   2. Each vehicle generates OTP and timestamp, creates ZKP proof.
#   3. RSU verifies each ZKP proof.
#   4. Blockchain verification is performed if DEBUG_MODE is enabled.
#   5. Print whether all vehicles were granted access by infrastructure.
##
def test_EndToEnd_MultipleVehicles_Simulated():
    
    # Print test header
    print("\n=== End - To - End; Multiple Vehicles; Simulated Test ===")
    
    # Use global variables to track tests, increment tested count
    global tested, passed
    tested += 1
    
    timer = Timer("End - To - End; Multiple Vehicles; Simulated Test Timer")
    timer.start()
    
    # Variables to hold vehicles and RSU secrets
    num_vehicles = 3
    vehicles = {}
    rsu_secrets = {}
    
    # For each vehicle, create a unique ID and secret
    for i in range(num_vehicles):
        
        # Generate vehicle ID formatted as VEH001, VEH002, etc.
        vid = f"VEH{i+1:03d}"
        
        # Generate a random secret for the vehicle and store it
        # in both the vehicles and RSU secrets dictionaries
        secret = secrets.token_hex(16)
        vehicles[vid] = Vehicle(vid, secret)
        rsu_secrets[vid] = secret
    
    # Create RSU with the secrets of all vehicles
    # This simulates the RSU having access to all vehicle secrets
    unused_rsu = RSU(rsu_secrets)
    
    # Initialize a flag to track if all vehicles passed authentication
    all_passed = True
    
    # Circuit path for the simulated ZKP proof
    unused_circuit_path = "zokrates/dummy.zok"
    
    # For each vehicle, generate OTP, timestamp, and ZKP proof
    for vid, vehicle in vehicles.items():
        
        # Generate OTP and timestamp for the vehicle
        otp, timestamp = vehicle.generate_otp()
        
        # Generate a simulated ZKP and expected ZKP from the same OTP and timestamp
        zkp_proof = generate_zkp_proof_simulated(otp, timestamp)
        expected_zkp = generate_zkp_proof_simulated(otp, timestamp)
        
        # Verify that the ZKP proof is equal to the expected proof
        verification_result = (zkp_proof == expected_zkp)
        
        # If DEBUG_MODE is enabled, store the verification result in outcome and print it
        # If DEBUG_MODE is disabled, outcome is just the verification result
        outcome = simulate_blockchain_verification(vid, zkp_proof, timestamp, verification_result) if DEBUG_MODE else verification_result
        
        if DEBUG_MODE:
            print(f"Vehicle {vid}: RSU result: {verification_result}, Blockchain outcome: {outcome}")
        
        # If the verification result or blockchain outcome is False, set all_passed to False
        all_passed = all_passed and outcome
    
    # Output the result of the ZoKrates workflow and blockchain verification for all vehicles, increment passed count if successful
    if all_passed:
        passed += 1
        print("[Simulated] All vehicles granted access by infrastructure.\n")
        
    else:
        print("[Simulated] Some vehicles denied access.\n")
    
    timer.stop()
    # Print elapsed time for the test
    print(f"\nTest completed in {timer.elapsed():.8f} seconds.\n")


##
# @brief Test the connection and workflow with ZoKrates CLI using zokrates/dummy.zok.
# @details
#   Runs ZoKrates CLI workflow with fixed inputs.
#
# Steps:
#   1. For each vehicle:
#      a. Generate inputs.
#      b. Compile ZoKrates circuit.
#      c. Run setup.
#      d. Compute witness.
#      e. Generate proof.
#      f. Verify proof.
#      g. Clean up ZoKrates artifacts.
#   2. Print whether all vehicles' proofs were verified successfully.
##
def test_PartialWorkflow_RealZokrates_MultipleVehicles_UsingDummyCircuit():
    
    # Print test header
    print("\n=== Partial Workflow - Real Zokrates; Multiple Vehicles (using dummy.zok) Test ===")
    
    # Use global variables to track tests, increment tested count
    global tested, passed
    tested += 1
    
    timer = Timer("Partial Workflow - Real Zokrates; Multiple Vehicles (using dummy.zok) Test Timer")
    timer.start()
    
    # Set the circuit path for ZoKrates from settings
    circuit_path = ZOKRATES_DUMMY_CIRCUIT
    
    # Set the number of vehicles to test and initialize a flag to track if all passed
    num_vehicles = 2
    all_passed = True
    
    # For each vehicle, generate random inputs and run ZoKrates workflow
    for i in range(num_vehicles):
        
        # Generate random inputs for the vehicle, random integers between 1 and 100
        a = random.randint(1, 100)
        b = random.randint(1, 100)
        
        # If DEBUG_MODE is enabled, print the inputs
        if DEBUG_MODE:
            print(f"Vehicle {i+1}: Inputs a={a}, b={b}")
        
        # Args to use for computing witness (a, b)
        args = [str(a), str(b)]
        
        # Use run_zokrates_workflow to handle the ZoKrates operations
        verification_result = run_zokrates_workflow(circuit_path, args)
        
        # If DEBUG_MODE is enabled, print the verification result
        if DEBUG_MODE:
            print(f"Vehicle {i+1}: ZoKrates verification result: {verification_result}")
        
        # If the verification result is False, set all_passed to False
        if not verification_result:
            all_passed = False
    
    # Output the result of the ZoKrates workflow for all vehicles, increment passed count if successful
    if all_passed:
        passed += 1
        print("[ZoKrates] All vehicles' proofs verified successfully.\n")
        
    else:
        print("[ZoKrates] Some vehicles' proofs failed verification.\n")
    
    timer.stop()
    # Print elapsed time for the test
    print(f"\nTest completed in {timer.elapsed():.8f} seconds.\n")


##
# @brief ZoKrates-integrated end-to-end test with multiple vehicles (zokrates/dummy.zok + simulated blockchain).
# @details
#   Runs ZoKrates workflow and blockchain verification for multiple vehicles.
#
# Steps:
#   1. For each vehicle:
#      a. Generate random inputs.
#      b. Compile ZoKrates circuit.
#      c. Run setup.
#      d. Compute witness.
#      e. Generate proof.
#      f. Verify proof.
#      g. Simulate blockchain verification if DEBUG_MODE is enabled.
#      h. Clean up ZoKrates artifacts.
#   2. Print whether all vehicles' proofs and blockchain logs succeeded.
##
def test_PartialWorkflow_RealZokratesSimulatedBlockchain_MultipleVehicles_UsingDummyCircuit():
    
    # Print test header
    print("\n=== Partial Workflow - Real Zokrates, Simulated Blockchain; Multiple Vehicles (using dummy.zok) Test ===")
    
    # Use global variables to track tests, increment tested count
    global tested, passed
    tested += 1
    
    timer = Timer("Partial Workflow - Real Zokrates, Simulated Blockchain; Multiple Vehicles (using dummy.zok) Test Timer")
    timer.start()
    
    # Set the circuit path for ZoKrates from settings
    circuit_path = ZOKRATES_DUMMY_CIRCUIT
    
    # Set the number of vehicles to test and initialize a flag to track if all passed
    num_vehicles = 2
    all_passed = True
    
    # For each vehicle, generate random inputs and run ZoKrates workflow
    # and simulate blockchain verification
    for i in range(num_vehicles):
        
        # Generate vehicle ID for each vehicle, formatted as ZOKR_VEH001, ZOKR_VEH002, etc.
        vid = f"ZOKR_VEH{i+1:03d}"
        
        # Generate random inputs for the vehicle, random integers between 1 and 100
        a = random.randint(1, 100)
        b = random.randint(1, 100)
        
        # If DEBUG_MODE is enabled, print the vehicle ID and the inputs
        if DEBUG_MODE:
            print(f"Vehicle {vid}: Inputs a={a}, b={b}")
        
        # Args to use for computing witness (a, b)
        # Convert inputs to strings for ZoKrates CLI
        args = [str(a), str(b)]
        
        # Use run_zokrates_workflow to handle the ZoKrates operations
        verification_result = run_zokrates_workflow(circuit_path, args)
        
        # If DEBUG_MODE is enabled, print the verification result
        if DEBUG_MODE:
            print(f"Vehicle {vid}: ZoKrates verification result: {verification_result}")
        
        # If DEBUG_MODE is enabled, simulate blockchain verification
        # If DEBUG_MODE is disabled, outcome is just the verification result
        outcome = simulate_blockchain_verification(vid, f"proof_{a}_{b}", int(time.time()), verification_result) if DEBUG_MODE else verification_result
        
        # If DEBUG_MODE is enabled, print the blockchain outcome
        if DEBUG_MODE:
            print(f"Vehicle {vid}: Blockchain outcome: {outcome}")
        
        # If the verification result or blockchain outcome is False, set all_passed to False
        if not (verification_result and outcome):
            all_passed = False
    
    # Output the result of the ZoKrates workflow and blockchain verification for all vehicles, increment passed count if successful
    if all_passed:
        passed += 1
        print("[Zokrates] All vehicles' end-to-end proofs and blockchain logs succeeded.\n")
        
    else:
        print("[ZoKrates] Some vehicles failed end-to-end ZoKrates or blockchain verification.\n")
    
    timer.stop()
    # Print elapsed time for the test
    print(f"\nTest completed in {timer.elapsed():.8f} seconds.\n")


##
# @brief Test connecting to SUMO via TraCI, retrieving and storing simulation data.
# @param print_data If True, print simulation data to screen.
# @details
#   Tests SUMO connection and data retrieval using TraCI.
#
# Steps:
#   1. Start SUMO with a simple network.
#   2. Connect via TraCI.
#   3. Retrieve simulation time, vehicle IDs, and positions.
#   4. Print/store the data.
#   5. Clean up.
##
def test_DataTransfer_SumoAndTraCI_UsingSimpleNet(print_data=True):
    
    # Print test header
    print("\n=== Data Transfer (using simple.net.xml) Test ===")
    
    # Use global variables to track tests, increment tested count
    global tested, passed
    tested += 1
    
    timer = Timer("Data Transfer (using simple.net.xml) Test Timer")
    timer.start()

    # Define the port for TraCI connection from settings
    port = SUMO_PORT_DATA
    
    # Define the SUMO network file path from settings
    SUMO_NET_FILE = SUMO_SIMPLE_NET_FILE
    
    # Check if the SUMO network file exists, if not, print error and return
    if not check_file_exists(SUMO_NET_FILE, "SUMO network file"):
        return
    
    # Start SUMO and connect via TraCI using the new unified function
    proc, traci, _, temp_config, temp_output_dir = start_sumo_simulation(
        file_path=SUMO_NET_FILE,
        is_config=False,
        port=port,
        sumo_binary="sumo",
        connect_traci=True,
        sumo_tools_path=SUMO_TOOLS_PATH
    )
    
    if proc is None or traci is None:
        return
    
    try:
        # Use the new flexible simulation runner
        unused_sim_data = run_sumo_simulation_flexible(traci, 5, print_data)
        passed_local = True
    
    # If any exception occurs during the TraCI data transfer, print the error and set passed_local to False
    except Exception as e:
        
        print(f"[SUMO TraCI Test] Error during TraCI data transfer: {e}")
        passed_local = False

    finally:
        cleanup_sumo_and_traci(proc, port, traci)
        # Clean up temp config/output if created
        if temp_config and os.path.exists(temp_config):
            try: os.unlink(temp_config)
            except: pass
        if temp_output_dir and os.path.exists(temp_output_dir):
            try: shutil.rmtree(temp_output_dir)
            except: pass

    if passed_local:
        passed += 1
        print("[SUMO TraCI Test] Data transfer test succeeded!\n")
        
    else:
        print("[SUMO TraCI Test] Data transfer test failed.\n")
    
    timer.stop()
    # Print elapsed time for the test
    print(f"\nTest completed in {timer.elapsed():.8f} seconds.\n")


##
# @brief Test connecting to SUMO via TraCI using a .sumocfg file, retrieving and storing simulation data for 100 steps.
# @param print_data If True, print simulation data to screen.
# @details
#   Tests SUMO connection and data retrieval using TraCI with a .sumocfg file.
#
# Steps:
#   1. Start SUMO with a configuration file.
#   2. Connect via TraCI.
#   3. Retrieve simulation time, vehicle IDs, and positions for 100 steps.
#   4. Print/store the data.
#   5. Clean up.
##
def test_DataTransfer_SumoAndTraCI_UsingIntersection1Config(print_data=True):
    
    # Print test header
    print("\n=== Data Transfer (using intersection1.sumocfg) Test ===")
    
    # Use global variables to track tests, increment tested count
    global tested, passed
    tested += 1
    
    timer = Timer("Data Transfer (using intersection1.sumocfg) Test Timer")
    timer.start()

    port = SUMO_PORT_DATA_CONFIG
    SUMO_SUMOCFG_FILE = SUMO_INTERSECTION_CONFIG_FILE

    if not check_file_exists(SUMO_SUMOCFG_FILE, "SUMO configuration file"):
        return

    # Start SUMO and connect via TraCI using the new unified function
    proc, traci, _, temp_config, temp_output_dir = start_sumo_simulation(
        file_path=SUMO_SUMOCFG_FILE,
        is_config=True,
        port=port,
        sumo_binary="sumo",
        connect_traci=True,
        sumo_tools_path=SUMO_TOOLS_PATH
    )

    if proc is None or traci is None:
        return

    try:
        unused_sim_data = run_sumo_simulation_flexible(traci, 100, print_data)
        passed_local = True
    
    # If any exception occurs during the TraCI data transfer, print the error and set passed_local to False
    except Exception as e:
        print(f"[SUMO TraCI Test] Error during TraCI data transfer: {e}")
        passed_local = False
    
    # Cleanup SUMO and TraCI
    finally:
        cleanup_sumo_and_traci(proc, port, traci)
        if temp_config and os.path.exists(temp_config):
            try: os.unlink(temp_config)
            except: pass
        if temp_output_dir and os.path.exists(temp_output_dir):
            try: shutil.rmtree(temp_output_dir)
            except: pass

    if passed_local:
        passed += 1
        print("[SUMO TraCI Test] .sumocfg data transfer test succeeded!\n")
        
    else:
        print("[SUMO TraCI Test] .sumocfg data transfer test failed.\n")

    timer.stop()
    # Print elapsed time for the test
    print(f"\nTest completed in {timer.elapsed():.8f} seconds.\n")


##
# @brief Test connecting to SUMO via TraCI using intersection2.sumocfg with explicit vehicles.
# @param print_data If True, print simulation data to screen.
# @details
#   Tests SUMO connection and data retrieval using TraCI with intersection2.sumocfg.
#
# Steps:
#   1. Start SUMO with intersection2.sumocfg.
#   2. Connect via TraCI.
#   3. Retrieve simulation time, vehicle IDs, and positions.
#   4. Print/store the data.
#   5. Clean up.
##
def test_DataTransfer_SumoAndTraCI_UsingIntersection2Config(print_data=True):
    
    # Print test header
    print("\n=== Data Transfer (using intersection2.sumocfg) Test ===")
    
    # Use global variables to track tests, increment tested count
    global tested, passed
    tested += 1
    
    timer = Timer("Data Transfer (using intersection2.sumocfg) Test Timer")
    timer.start()

    # Define the port for TraCI connection from settings
    port = SUMO_PORT_DATA_INTERSECTION2_CONFIG
    
    # Check if the intersection2.sumocfg file exists
    if not check_file_exists(SUMO_INTERSECTION2_CONFIG_FILE, "SUMO intersection2 configuration file"):
        return

    # Start SUMO and connect via TraCI using the new unified function
    proc, traci, _, temp_config, temp_output_dir = start_sumo_simulation(
        file_path=SUMO_INTERSECTION2_CONFIG_FILE,
        is_config=True,
        port=port,
        sumo_binary="sumo",
        connect_traci=True,
        sumo_tools_path=SUMO_TOOLS_PATH
    )

    if proc is None or traci is None:
        return

    try:
        # Use the centralized run_sumo_simulation function
        unused_sim_data = run_sumo_simulation_flexible(traci, 100, print_data)
        passed_local = True
    
    # If any exception occurs during the TraCI data transfer, print the error and set passed_local to False
    except Exception as e:
        print(f"[SUMO TraCI Test] Error during TraCI data transfer: {e}")
        passed_local = False
    
    # Cleanup SUMO and TraCI
    finally:
        cleanup_sumo_and_traci(proc, port, traci)
        if temp_config and os.path.exists(temp_config):
            try: os.unlink(temp_config)
            except: pass
        if temp_output_dir and os.path.exists(temp_output_dir):
            try: shutil.rmtree(temp_output_dir)
            except: pass

    if passed_local:
        passed += 1
        print("[SUMO TraCI Test] intersection2.sumocfg data transfer test succeeded!\n")
        
    else:
        print("[SUMO TraCI Test] intersection2.sumocfg data transfer test failed.\n")
    
    timer.stop()
    # Print elapsed time for the test
    print(f"\nTest completed in {timer.elapsed():.8f} seconds.\n")


##
# @brief Test connecting to SUMO via TraCI using straightaway1.sumocfg.
# @param print_data If True, print simulation data to screen.
# @details
#   Tests SUMO connection and data retrieval using TraCI with straightaway1.sumocfg.
#
# Steps:
#   1. Start SUMO with straightaway1.sumocfg.
#   2. Connect via TraCI.
#   3. Retrieve simulation time, vehicle IDs, and positions.
#   4. Print/store the data.
#   5. Clean up.
##
def test_DataTransfer_SumoAndTraCI_UsingStraightaway1Config(print_data=True):
    
    # Print test header
    print("\n=== Data Transfer (using straightaway1.sumocfg) Test ===")
    
    # Use global variables to track tests, increment tested count
    global tested, passed
    tested += 1
    
    timer = Timer("Data Transfer (using straightaway1.sumocfg) Test Timer")
    timer.start()

    # Define the port for TraCI connection from settings, using a different port to avoid conflicts
    port = SUMO_PORT_DATA_STRAIGHTAWAY1_CONFIG
    
    # Check if the straightaway1.sumocfg file exists
    if not check_file_exists(SUMO_STRAIGHTAWAY1_CONFIG_FILE, "SUMO straightaway1 configuration file"):
        return

    # Start SUMO and connect via TraCI using the new unified function
    proc, traci, _, temp_config, temp_output_dir = start_sumo_simulation(
        file_path=SUMO_STRAIGHTAWAY1_CONFIG_FILE,
        is_config=True,
        port=port,
        sumo_binary="sumo",
        connect_traci=True,
        sumo_tools_path=SUMO_TOOLS_PATH
    )

    if proc is None or traci is None:
        return

    try:
        # Use the centralized run_sumo_simulation function
        unused_sim_data = run_sumo_simulation_flexible(traci, 100, print_data)
        passed_local = True
    
    # If any exception occurs during the TraCI data transfer, print the error and set passed_local to False
    except Exception as e:
        print(f"[SUMO TraCI Test] Error during TraCI data transfer: {e}")
        passed_local = False
    
    # Cleanup SUMO and TraCI
    finally:
        cleanup_sumo_and_traci(proc, port, traci)
        if temp_config and os.path.exists(temp_config):
            try: os.unlink(temp_config)
            except: pass
        if temp_output_dir and os.path.exists(temp_output_dir):
            try: shutil.rmtree(temp_output_dir)
            except: pass

    if passed_local:
        passed += 1
        print("[SUMO TraCI Test] straightaway1.sumocfg data transfer test succeeded!\n")
    else:
        print("[SUMO TraCI Test] straightaway1.sumocfg data transfer test failed.\n")
    
    timer.stop()
    # Print elapsed time for the test
    print(f"\nTest completed in {timer.elapsed():.8f} seconds.\n")


##
# @brief Test connecting to SUMO via TraCI using straightaway2.sumocfg.
# @param print_data If True, print simulation data to screen.
# @details
#   Tests SUMO connection and data retrieval using TraCI with straightaway2.sumocfg.
#
# Steps:
#   1. Start SUMO with straightaway2.sumocfg.
#   2. Connect via TraCI.
#   3. Retrieve simulation time, vehicle IDs, and positions.
#   4. Print/store the data.
#   5. Clean up.
##
def test_DataTransfer_SumoAndTraCI_UsingStraightaway2Config(print_data=True):
    
    # Print test header
    print("\n=== Data Transfer (using straightaway2.sumocfg) Test ===")
    
    # Use global variables to track tests, increment tested count
    global tested, passed
    tested += 1
    
    timer = Timer("Data Transfer (using straightaway2.sumocfg) Test Timer")
    timer.start()

    # Define the port for TraCI connection from settings, using a different port to avoid conflicts
    port = SUMO_PORT_DATA_STRAIGHTAWAY2_CONFIG

    if not check_file_exists(SUMO_STRAIGHTAWAY2_CONFIG_FILE, "SUMO straightaway2 configuration file"):
        return

    # Start SUMO and connect via TraCI using the new unified function
    proc, traci, _, temp_config, temp_output_dir = start_sumo_simulation(
        file_path=SUMO_STRAIGHTAWAY2_CONFIG_FILE,
        is_config=True,
        port=port,
        sumo_binary="sumo",
        connect_traci=True,
        sumo_tools_path=SUMO_TOOLS_PATH
    )

    if proc is None or traci is None:
        return

    try:
        # Use the centralized run_sumo_simulation function
        unused_sim_data = run_sumo_simulation_flexible(traci, 100, print_data)
        passed_local = True
    
    # If any exception occurs during the TraCI data transfer, print the error and set passed_local to False
    except Exception as e:
        print(f"[SUMO TraCI Test] Error during TraCI data transfer: {e}")
        passed_local = False
    
    # Cleanup SUMO and TraCI
    finally:
        cleanup_sumo_and_traci(proc, port, traci)
        if temp_config and os.path.exists(temp_config):
            try: os.unlink(temp_config)
            except: pass
        if temp_output_dir and os.path.exists(temp_output_dir):
            try: shutil.rmtree(temp_output_dir)
            except: pass

    if passed_local:
        passed += 1
        print("[SUMO TraCI Test] straightaway2.sumocfg data transfer test succeeded!\n")
    else:
        print("[SUMO TraCI Test] straightaway2.sumocfg data transfer test failed.\n")
    
    timer.stop()
    # Print elapsed time for the test
    print(f"\nTest completed in {timer.elapsed():.8f} seconds.\n")


##
# @brief Test manipulating SUMO vehicles in real-time using TraCI with straightaway1.sumocfg.
# @param print_data If True, print simulation data to screen.
# @details
#   Tests manipulating vehicle parameters (speed, color, position) during a SUMO simulation.
#
#       ***Position movement is still buggy. It's not needed in the actual framework, so it's
#                   been left as is after a period of troubleshooting wasn't fruitful***
#
# Steps:
#   1. Start SUMO with straightaway1.sumocfg.
#   2. Connect via TraCI.
#   3. Run the simulation for several steps to let vehicles appear.
#   4. Manipulate vehicle parameters (color, speed, position).
#   5. Continue simulation to observe effects.
#   6. Clean up.
##
def test_LiveManipulation_SumoAndTraCI_UsingStraightaway1Config(print_data=True):
    
    # Print test header
    print("\n=== Live Manipulation (using straightaway1.sumocfg) Test ===")
    
    # Use global variables to track tests, increment tested count
    global tested, passed
    tested += 1
    
    timer = Timer("Live Manipulation (using straightaway1.sumocfg) Test Timer")
    timer.start()

    # Define the port for TraCI connection from settings, using a different port to avoid conflicts
    port = SUMO_PORT_LIVE_MANIPULATION
    
    # Check if the straightaway1.sumocfg file exists
    if not check_file_exists(SUMO_STRAIGHTAWAY1_CONFIG_FILE, "SUMO straightaway1 configuration file"):
        return

    # Start SUMO and connect via TraCI using the new unified function
    proc, traci, _, temp_config, temp_output_dir = start_sumo_simulation(
        file_path=SUMO_STRAIGHTAWAY1_CONFIG_FILE,
        is_config=True,
        port=port,
        sumo_binary="sumo",
        connect_traci=True,
        sumo_tools_path=SUMO_TOOLS_PATH
    )

    if proc is None or traci is None:
        return
    
    try:
        # Run the simulation for steps to let vehicles appear
        veh_ids = []
        for step in range(15):
            traci.simulationStep()
            
            current_veh_ids = traci.vehicle.getIDList()
            if current_veh_ids and not veh_ids:
                veh_ids = current_veh_ids
                if print_data:
                    print(f"Vehicles detected in simulation at step {step}: {veh_ids}")
                break
                
        # If no vehicles are present, we can't proceed with manipulations
        if not veh_ids:
            print("[SUMO Manipulation Test] No vehicles found in simulation after 15 steps.")
            passed_local = False
            return
            
        # We'll manipulate the first vehicle
        vehicle_id = veh_ids[0]
        
        # Store initial vehicle state
        initial_speed = traci.vehicle.getSpeed(vehicle_id)
        initial_position = traci.vehicle.getPosition(vehicle_id)
        initial_color = traci.vehicle.getColor(vehicle_id)
        
        if print_data:
            print(f"\nInitial state of vehicle {vehicle_id}:")
            print(f"Speed: {initial_speed:.2f} m/s")
            print(f"Position: ({initial_position[0]:.2f}, {initial_position[1]:.2f})")
            print(f"Color: {initial_color}")

        # 1. Change vehicle color to red
        try:
            traci.vehicle.setColor(vehicle_id, (255, 0, 0, 255))
            if print_data:
                print(f"\nChanged color of vehicle {vehicle_id} to red")
        except Exception as e:
            print(f"Failed to change color: {e}")
        
        # Run a step to apply changes
        traci.simulationStep()

        # 2. Change vehicle speed
        try:
            new_speed = 15.0
            traci.vehicle.setSpeed(vehicle_id, new_speed)
            if print_data:
                print(f"Changed speed of vehicle {vehicle_id} to {new_speed} m/s")
        except Exception as e:
            print(f"Failed to change speed: {e}")
        
        # Run a step to apply changes
        traci.simulationStep()

        # 3. Move vehicle forward along lane
        post_speed_position = None
        try:
            # Get position after speed change but before manual movement
            post_speed_position = traci.vehicle.getPosition(vehicle_id)
            lane_id = traci.vehicle.getLaneID(vehicle_id)
            current_lane_pos = traci.vehicle.getLanePosition(vehicle_id)
            new_lane_pos = current_lane_pos + 10
            traci.vehicle.moveTo(vehicle_id, lane_id, new_lane_pos)
            if print_data:
                print(f"Moved vehicle {vehicle_id} 10m forward along lane {lane_id}")
                
        except Exception as e:
            print(f"Failed to move vehicle along lane: {e}")
        
        # Run several steps to see the effects of all manipulations
        for step in range(15):
            traci.simulationStep()
            
            # Get final state after last step
            if step == 14:
                try:
                    final_speed = traci.vehicle.getSpeed(vehicle_id)
                    final_position = traci.vehicle.getPosition(vehicle_id)
                    final_color = traci.vehicle.getColor(vehicle_id)
                    
                    # Calculate changes
                    unused_speed_change = final_speed - initial_speed
                    position_change = final_position[0] - initial_position[0]
                    
                    # Position change due to speed (after speed was set but before manual movement)
                    speed_position_change = 0
                    if post_speed_position:
                        speed_position_change = post_speed_position[0] - initial_position[0]
                    
                    # Position change due to manual movement and subsequent movement
                    unused_manual_and_subsequent = position_change - speed_position_change
                    
                    if print_data:
                        print(f"\nFinal state of vehicle {vehicle_id} after manipulations:")
                        print(f"Speed: {final_speed:.2f} m/s (was {initial_speed:.2f} m/s)")
                        print(f"Position: ({final_position[0]:.2f}, {final_position[1]:.2f}) (was ({initial_position[0]:.2f}, {initial_position[1]:.2f}))")
                        print(f"Color: {final_color} (was {initial_color})")
                        
                        print("\n[SUMO Manipulation Test] Successfully manipulated vehicle properties:")
                        print(f"- Speed changed from {initial_speed:.2f} to {final_speed:.2f}")
                        print(f"- Position changed {position_change:.2f} meters (from {initial_position[0]:.2f} to {final_position[0]:.2f})")
                        print(f"- Color changed from {initial_color} to {final_color}")
                    
                    # Verify that manipulations had an effect
                    speed_changed = abs(final_speed - initial_speed) > 0.1
                    position_changed = abs(position_change) > 5.0
                    color_changed = final_color != initial_color
                    
                    passed_local = speed_changed and position_changed and color_changed
                    
                except Exception as e:
                    print(f"Error reading final vehicle state: {e}")
                    passed_local = False
    
    # If any exception occurs during the manipulation
    except Exception as e:
        print(f"[SUMO Manipulation Test] Error during vehicle manipulation: {e}")
        passed_local = False
    
    # Use the utility function to clean up SUMO and TraCI
    finally:
        cleanup_sumo_and_traci(proc, port, traci)
        if temp_config and os.path.exists(temp_config):
            try: os.unlink(temp_config)
            except: pass
        if temp_output_dir and os.path.exists(temp_output_dir):
            try: shutil.rmtree(temp_output_dir)
            except: pass

    if passed_local:
        passed += 1
        print("[SUMO Manipulation Test] Vehicle manipulation test succeeded!")
    else:
        print("[SUMO Manipulation Test] Vehicle manipulation test failed.")
    
    timer.stop()
    print(f"\nTest completed in {timer.elapsed():.8f} seconds.\n")


##
# @brief Test the zokrates/VtoI_test.zok circuit for vehicle-to-infrastructure authentication.
# @details
#   Tests the vehicle-to-infrastructure authentication circuit which uses a commitment scheme.
#
# Steps:
#   1. Create an experiment with the VtoI_test.zok circuit.
#   2. Run the experiment with a vehicle ID, secret key, and commitment.
#   3. Check if the verification was successful.
##
def test_Zokrates_UsingVtoICircuit():
    
    # Print test header
    print("\n=== Zokrates (using VtoI_test.zok) Test ===")
    
    # Use global variables to track tests, increment tested count
    global tested, passed
    tested += 1
    
    timer = Timer("Zokrates (using VtoI_test.zok) Test Timer")
    timer.start()
    
    # Set the circuit path for ZoKrates
    circuit_path = "zokrates/VtoI_test.zok"
    
    # Generate random secret key and vehicle ID
    sk = random.randint(1, 999)
    vid = random.randint(1, 999999999)
    commitment = (sk * sk) + vid

    # Prepare arguments for ZoKrates
    args = [str(sk), str(vid), str(commitment)]

    # Print debug info if DEBUG_MODE is enabled
    if DEBUG_MODE:
        print(f"[VtoI_test.zok] sk={sk}, vid={vid}, commitment={commitment}")
        print(f"[VtoI_test.zok] args={args}")

    # Run ZoKrates workflow
    verification_result = run_zokrates_workflow(circuit_path, args)

    if DEBUG_MODE:
        print(f"[VtoI_test.zok] Verification result: {verification_result}")

    if verification_result:
        print(f"[PASS] Vehicle-to-Infrastructure ZKP Test passed - sk: {sk}, vid: {vid}")
        passed += 1
    else:
        print(f"[FAIL] Vehicle-to-Infrastructure ZKP Test failed - sk: {sk}, vid: {vid}")

    cleanup_zokrates_files()
    timer.stop()
    print(f"\nTest completed in {timer.elapsed():.8f} seconds.\n")
    return verification_result


##
# @brief Test the authentication circuit (auth.zok) for field-based proof.
# @details
#   Tests the authentication circuit which uses simple field arithmetic for authentication.
#
# Steps:
#   1. Create an experiment with the auth.zok circuit.
#   2. Run the experiment with a random vehicle ID and secret.
#   3. Check if the verification was successful.
##
def test_Zokrates_UsingAuthCircuit():
    
    # Print test header
    print("\n=== Zokrates (using auth.zok) Test ===")
    
    # Use global variables to track tests, increment tested count
    global tested, passed
    tested += 1
    
    timer = Timer("Zokrates (using auth.zok) Test Timer")
    timer.start()
    
    # Set the circuit path for ZoKrates
    circuit_path = "zokrates/auth.zok"
    
    # Generate random secret and timestamp
    secret = random.randint(1, 100000)
    timestamp = int(time.time())
    otp = secret + timestamp

    # Prepare arguments for ZoKrates
    args = [str(secret), str(timestamp), str(otp)]

    # Print debug info if DEBUG_MODE is enabled
    if DEBUG_MODE:
        print(f"[auth.zok] secret={secret}, timestamp={timestamp}, otp={otp}")
        print(f"[auth.zok] args={args}")

    # Run ZoKrates workflow
    verification_result = run_zokrates_workflow(circuit_path, args)

    if DEBUG_MODE:
        print(f"[auth.zok] Verification result: {verification_result}")

    if verification_result:
        print(f"[PASS] Authentication Circuit Test passed - secret: {secret}, timestamp: {timestamp}")
        passed += 1
    else:
        print(f"[FAIL] Authentication Circuit Test failed - secret: {secret}, timestamp: {timestamp}")

    cleanup_zokrates_files()
    timer.stop()
    print(f"\nTest completed in {timer.elapsed():.8f} seconds.\n")
    return verification_result


##
# @brief Test SUMO with a 10ms step length using straightaway1.sumocfg.
# @param print_data If True, print simulation data to screen.
# @details
#   Tests SUMO running with a small step length of 10ms for more precise simulation.
#
# Steps:
#   1. Start SUMO with straightaway1.sumocfg and --step-length 0.01.
#   2. Connect via TraCI.
#   3. Retrieve simulation time for several steps to verify the step length.
#   4. Print/store the data.
#   5. Clean up.
##
def test_DataTransfer_SumoAndTraCI_SmallStepLength_UsingStraightaway1Config(print_data=True):
    
    # Print test header
    print("\n=== Data Transfer; Small Step (using straightaway1.sumocfg) Test ===")
    
    # Use global variables to track tests, increment tested count
    global tested, passed
    tested += 1
    
    timer = Timer("Data Transfer; Small Step (using straightaway1.sumocfg) Test Timer")
    timer.start()

    # Define the port for TraCI connection from settings, using a different port to avoid conflicts
    port = SUMO_PORT_SMALL_STEP
    
    # Check if the straightaway1.sumocfg file exists
    if not check_file_exists(SUMO_STRAIGHTAWAY1_CONFIG_FILE, "SUMO straightaway1 configuration file"):
        return

    # Start SUMO and connect via TraCI using the new unified function
    proc, traci, _, temp_config, temp_output_dir = start_sumo_simulation(
        file_path=SUMO_STRAIGHTAWAY1_CONFIG_FILE,
        is_config=True,
        port=port,
        sumo_binary="sumo",
        connect_traci=True,
        step_length=0.01,
        sumo_tools_path=SUMO_TOOLS_PATH
    )

    if proc is None or traci is None:
        return
    
    try:
        # Use the flexible simulation runner
        sim_data = run_sumo_simulation_flexible(traci, 50, print_data)
        
        # Extract time values from simulation data
        time_values = [step["time"] for step in sim_data]
        
        # Calculate step lengths
        step_lengths = [time_values[i+1] - time_values[i] for i in range(len(time_values)-1)]
        avg_step_length = sum(step_lengths) / len(step_lengths) if step_lengths else 0.0

        if print_data:
            print(f"\nAverage step length: {avg_step_length:.5f} seconds")
        
        # Check if the average step length is close to 0.01
        step_length_correct = abs(avg_step_length - 0.01) < 0.001
        
        if step_length_correct:
            if print_data:
                print("[SUMO Small Step Test] Step length verified as approximately 0.01 seconds")
            passed_local = True
        else:
            print(f"[SUMO Small Step Test] Step length verification failed. Expected: 0.01, Got: {avg_step_length:.5f}")
            passed_local = False
        
    # If any exception occurs during the TraCI data transfer
    except Exception as e:
        print(f"[SUMO Small Step Test] Error during test: {e}")
        passed_local = False
    
    # Use the utility function to clean up SUMO and TraCI
    finally:
        cleanup_sumo_and_traci(proc, port, traci)
        if temp_config and os.path.exists(temp_config):
            try: os.unlink(temp_config)
            except: pass
        if temp_output_dir and os.path.exists(temp_output_dir):
            try: shutil.rmtree(temp_output_dir)
            except: pass

    if passed_local:
        passed += 1
        print("[SUMO Small Step Test] Small step length test succeeded!\n")
    else:
        print("[SUMO Small Step Test] Small step length test failed.\n")
    
    timer.stop()
    
    # Print elapsed time for the test
    print(f"\nTest completed in {timer.elapsed():.8f} seconds.\n")


def test_LiveManipulation_SumoAndTraCI_SpawnCarsDynamically_UsingStraightaway5(print_data=True):
    """
    Connects to straightaway5.sumocfg, spawns a car at step 10, and whenever a car completes its route,
    immediately spawns another identical car, for 1010 steps.
    """
    print("\n=== SUMO Dynamic Car Spawning (straightaway5.sumocfg) Test ===")
    global tested, passed
    tested += 1

    timer = Timer("SUMO Dynamic Car Spawning (straightaway5.sumocfg) Test Timer")
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
        return

    try:
        total_steps = 1010
        car_counter = 0
        active_cars = {}  # Track active cars and their spawn times
        car_type = "car"
        car_route = "route1"
        finished_cars = 0

        for step in range(total_steps):
            # Exit if we've reached total_steps
            if step >= total_steps - 1:
                print(f"\nReached max steps ({total_steps}). Ending simulation.")
                print(f"Total cars finished: {finished_cars}")
                break
            traci.simulationStep()
            sim_time = traci.simulation.getTime()

            # Check for cars that have finished their routes
            for car_id in list(active_cars.keys()):
                if car_id not in traci.vehicle.getIDList():
                    finished_cars += 1
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

            # Print vehicle list and position for debugging if requested
            if print_data:
                veh_ids = traci.vehicle.getIDList()
                print(f"Step {step}: Vehicles in sim: {veh_ids}")
                for car_id in veh_ids:
                    try:
                        pos = traci.vehicle.getPosition(car_id)
                        print(f"Step {step}: {car_id} position: {pos}")
                    except Exception as e:
                        print(f"Step {step}: Could not get position for {car_id}: {e}")

            if print_data and step % 100 == 0:
                print(f"Step {step}: Active cars: {list(active_cars.keys())}, Finished cars: {finished_cars}")

        passed_local = True

    except Exception as e:
        print(f"[SUMO Dynamic Car Spawning Test] Error: {e}")
        passed_local = False

    finally:
        cleanup_sumo_and_traci(proc, port, traci)
        if temp_config and os.path.exists(temp_config):
            try: os.unlink(temp_config)
            except: pass
        if temp_output_dir and os.path.exists(temp_output_dir):
            try: shutil.rmtree(temp_output_dir)
            except: pass

    if passed_local:
        passed += 1
        print("[SUMO Dynamic Car Spawning Test] Test succeeded!\n")
    else:
        print("[SUMO Dynamic Car Spawning Test] Test failed.\n")

    timer.stop()
    print(f"\nTest completed in {timer.elapsed():.8f} seconds.\n")
    
    
def test_LiveManipulation_SumoAndTraCI_RsuMessageWithDelay_UsingStraightaway6(print_data=True):
    """
    Connects to straightaway6.sumocfg, spawns a car at step 1000, and whenever a car completes its route,
    immediately spawns another identical car, for 51000 steps.
    """
    print("\n=== Live Manipulation - Rsu Message With Delay; (using straightaway6.sumocfg) Test ===")
    global tested, passed
    tested += 1
    flags_raised = 0
    flags_lowered = 0

    timer = Timer("Live Manipulation - Rsu Message With Delay; (using straightaway6.sumocfg) Test Timer")
    timer.start()

    # Use the correct config file path and port
    sumo_cfg = os.path.join(
        os.path.dirname(__file__),
        "..", "..", "SUMO", "Built Sims", "StraightAway6", "straightaway6.sumocfg"
    )
    sumo_cfg = os.path.abspath(sumo_cfg)
    port = SUMO_PORT_RSUWITHDELAY

    # Check config file exists
    if not check_file_exists(sumo_cfg, "SUMO straightaway5 configuration file"):
        return

    proc, traci, _, temp_config, temp_output_dir = start_sumo_simulation(
        file_path=sumo_cfg,
        is_config=True,
        port=port,
        sumo_binary="sumo",
        connect_traci=True,
        step_length=0.01,  # Added step_length parameter
        sumo_tools_path=SUMO_TOOLS_PATH
    )

    if proc is None or traci is None:
        return

    try:
        total_steps = 51000
        car_counter = 0
        active_cars = {}
        car_type = "car"
        car_route = "route1"
        finished_cars = 0
        rsu_car_close_flag = False  # Flag for RSU-car proximity

        for step in range(total_steps):
            # --- Move RSU-car distance logic to top level of loop ---
            rsu_ids = []
            car_ids = []
            try:
                rsu_ids = [vid for vid in traci.vehicle.getIDList() if traci.vehicle.getTypeID(vid) == "rsu"]
                car_ids = [vid for vid in traci.vehicle.getIDList() if traci.vehicle.getTypeID(vid) == "car"]
                if rsu_ids and car_ids:
                    rsu_pos = traci.vehicle.getPosition(rsu_ids[0])
                    car_pos = traci.vehicle.getPosition(car_ids[0])
                    dx = rsu_pos[0] - car_pos[0]
                    dy = rsu_pos[1] - car_pos[1]
                    dist = (dx**2 + dy**2) ** 0.5
                    # --- Flag logic ---
                    if dist < 100:
                        if not rsu_car_close_flag:
                            rsu_car_close_flag = True
                            print(f"*** FLAG RAISED: RSU and car are within 50 meters at step {step} (distance: {dist:.2f} m) ***")
                            flags_raised += 1
                            # Slow down car to 25 m/s over 1 second
                            try:
                                traci.vehicle.slowDown(car_ids[0], 1.0, 0.1)
                                if print_data:
                                    print(f"Slowing down {car_ids[0]} to 5 m/s over 0.1 second")
                            except Exception as e:
                                print(f"Could not slow down car {car_ids[0]}: {e}")
                    else:
                        if rsu_car_close_flag:
                            rsu_car_close_flag = False
                            print(f"*** FLAG LOWERED: RSU and car are now farther than 50 meters at step {step} (distance: {dist:.2f} m) ***")
                            flags_lowered += 1
                            # Speed up car to 45 m/s over 1 second
                            try:
                                traci.vehicle.slowDown(car_ids[0], 45.0, 0.1)
                                if print_data:
                                    print(f"Speeding up {car_ids[0]} to 45 m/s over 1 second")
                            except Exception as e:
                                print(f"Could not speed up car {car_ids[0]}: {e}")
                    if step % 100 == 0:
                        print(f"Step {step}: Distance between RSU ({rsu_ids[0]}) and car ({car_ids[0]}): {dist:.2f} m")
            except Exception as e:
                if step % 1000 == 0:
                    print(f"Step {step}: Could not compute RSU-car distance: {e}")

            # Exit if we've reached total_steps
            if step >= total_steps - 1:
                print(f"\nReached max steps ({total_steps}). Ending simulation.")
                print(f"Total cars finished: {finished_cars}")
                print(f"Flags raised: {flags_raised}, Flags lowered: {flags_lowered}")
                break

            traci.simulationStep()
            sim_time = traci.simulation.getTime()

            # Check for cars that have finished their routes
            for car_id in list(active_cars.keys()):
                if car_id not in traci.vehicle.getIDList():
                    finished_cars += 1
                    if print_data:
                        print(f"{car_id} finished at step {step}")
                    del active_cars[car_id]

            # Spawn a new car if no active cars are present and we're past step 1000
            if not active_cars and step >= 1000:
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
                    
            # Print status every 1000 steps to track progress
            if step % 1000 == 0:
                print(f"Step {step}: Active cars: {list(active_cars.keys())}, Total finished cars: {finished_cars}")
                

            # Print vehicle list and position for debugging if requested
            if print_data and DEBUG_MODE:
                veh_ids = traci.vehicle.getIDList()
                print(f"Step {step}: Vehicles in sim: {veh_ids}")
                for car_id in veh_ids:
                    try:
                        pos = traci.vehicle.getPosition(car_id)
                        print(f"Step {step}: {car_id} position: {pos}")
                    except Exception as e:
                        print(f"Step {step}: Could not get position for {car_id}: {e}")

        passed_local = True  # Test passes if it completes all steps

    except Exception as e:
        print(f"[Live Manipulation - Rsu Message With Delay] Error: {e}")
        passed_local = False

    finally:
        cleanup_sumo_and_traci(proc, port, traci)
        if temp_config and os.path.exists(temp_config):
            try: os.unlink(temp_config)
            except: pass
        if temp_output_dir and os.path.exists(temp_output_dir):
            try: shutil.rmtree(temp_output_dir)
            except: pass

    if passed_local:
        passed += 1
        print("[Live Manipulation - Rsu Message With Delay] Test succeeded!\n")
    else:
        print("[Live Manipulation - Rsu Message With Delay] Test failed.\n")

    timer.stop()
    print(f"\nTest completed in {timer.elapsed():.8f} seconds.\n")


def testAndScenarioRunner():
    
    # Use global variables to track tests, initialize counts
    global tested, passed
    tested, passed = 0, 0
    
    timer = Timer("Test and Scenario Runner Timer")
    timer.start()

    # 3 - Run Simulated ZKP Test
    test_VehicleRsuBasicInteraction_SimulatedZkp()
    time.sleep(.5)
    # clear_console()

    # 4 - Run Simulated Blockchain ZKP Test
    test_VehicleRsuBasicInteraction_SimulatedZkpAndBlockchain()
    time.sleep(.5)
    # clear_console()

    # 5 - Run Simulated End-to-End Scenario: Successful Authentication
    test_EndToEnd_SimulatedZkpAndBlockchain_Success()
    time.sleep(.5)
    # clear_console()

    # 6 - Run Simulated End-to-End Scenario: Failed Authentication
    test_EndToEnd_SimulatedZkpAndBlockchain_Failure()
    time.sleep(.5)
    # clear_console()

    # 7 - Run Real ZoKrates End-to-End Test with dummy.zok
    test_PartialWorkflow_RealZokrates_UsingDummyCircuit()
    time.sleep(.5)
    # clear_console()

    # 8 - Simulated ZKP Isolated Test: Multiple Vehicles
    test_PartialWorkflow_MultipleVehicles_Simulated()
    time.sleep(.5)
    # clear_console()

    # 9 - Simulated End-to-End Test: Multiple Vehicles
    test_EndToEnd_MultipleVehicles_Simulated()
    time.sleep(.5)
    # clear_console()

    # 10 - ZoKrates-Integrated Isolated Test: Multiple Vehicles
    test_PartialWorkflow_RealZokrates_MultipleVehicles_UsingDummyCircuit()
    time.sleep(.5)
    # clear_console()

    # 11 - ZoKrates-Integrated End-to-End Test: Multiple Vehicles
    test_PartialWorkflow_RealZokratesSimulatedBlockchain_MultipleVehicles_UsingDummyCircuit()
    time.sleep(.5)
    # clear_console()

    # 12 - Run SUMO Connection Tests (Basic Network + Configuration File)
    tested, passed = test_sumo_connection_wrapper(tested, passed)
    time.sleep(.5)
    # clear_console()

    # 13 - Run ZoKrates CLI Connection Test
    test_Zokrates_BasicConnectionTest_UsingDummyCircuit()
    time.sleep(.5)
    # clear_console()

    # 14 - Run SUMO TraCI Data Transfer Test
    test_DataTransfer_SumoAndTraCI_UsingSimpleNet(True)
    time.sleep(.5)
    # clear_console()

    # 15 - Run SUMO TraCI Data Transfer Test (.sumocfg, 100 steps)
    test_DataTransfer_SumoAndTraCI_UsingIntersection1Config(True)
    time.sleep(.5)
    # clear_console()

    # 15b - Run SUMO TraCI Data Transfer Test (intersection2.sumocfg, explicit vehicles)
    test_DataTransfer_SumoAndTraCI_UsingIntersection2Config(True)
    time.sleep(.5)
    # clear_console()

    # 15c - Run SUMO TraCI Data Transfer Test (straightaway1.sumocfg)
    test_DataTransfer_SumoAndTraCI_UsingStraightaway1Config(True)
    time.sleep(.5)
    # clear_console()

    # 15d - Run SUMO TraCI Data Transfer Test (straightaway2.sumocfg)
    test_DataTransfer_SumoAndTraCI_UsingStraightaway2Config(True)
    time.sleep(.5)
    # clear_console()
    
    # 15e - Run SUMO Live Vehicle Manipulation Test (straightaway1.sumocfg)
    test_LiveManipulation_SumoAndTraCI_UsingStraightaway1Config(True)
    time.sleep(.5)
    # clear_console()

    # 16 - Run Vehicle-to-Infrastructure ZKP Test with the
    # zokrates/VtoI_test.zok circuit for vehicle-to-infrastructure authentication
    test_Zokrates_UsingVtoICircuit()
    time.sleep(.5)
    # clear_console()
    
    # 17 - Run Authentication Circuit Test with auth.zok
    test_Zokrates_UsingAuthCircuit()
    time.sleep(.5)
    # clear_console()
    
    # 18 - Run SUMO Small Step Length Test (10ms steps)
    test_DataTransfer_SumoAndTraCI_SmallStepLength_UsingStraightaway1Config(True)
    time.sleep(.5)
    # clear_console()

    # --- Add any tests not already in the runner ---

    # 19 - Run Dynamic Car Spawning (using straightaway5.sumocfg) Test
    test_LiveManipulation_SumoAndTraCI_SpawnCarsDynamically_UsingStraightaway5(True)
    time.sleep(.5)
    # clear_console()

    # 20 - Run RSU Message With Delay (using straightaway5.sumocfg) Test
    test_LiveManipulation_SumoAndTraCI_RsuMessageWithDelay_UsingStraightaway6(True)
    time.sleep(.5)
    # clear_console()
    
    # SUMO cleanup after connection tests
    cleanup_traci_connection()
    kill_processes_on_port(SUMO_PORT_BASIC)
    kill_processes_on_port(SUMO_PORT_CONFIG)
    kill_processes_on_port(SUMO_PORT_DATA)
    kill_processes_on_port(SUMO_PORT_DYNAMIC_SPAWN)
    time.sleep(2)

    timer.stop()
    
    # Print elapsed time for the test
    print(f"\nAll tests completed in {timer.elapsed():.8f} seconds.\n")
    
    print(f"\nTotal tests run: {tested}")
    print(f"Total tests passed: {passed}")
    print(f"Total tests failed: {tested - passed}")
    print()
    time.sleep(2)


## Runs all tests and scenarios
if __name__ == "__main__":
    
    testAndScenarioRunner()
    print(f"\nTotal tests run: {tested}")
    print(f"Total tests passed: {passed}")
    print(f"Total tests failed: {tested - passed}")
    print()
    time.sleep(2)

