##
# @file preliminary_tests.py
# @author Tom Rose
#
# @brief
#   Contains test routines to simulate and validate the ZKP-OTP authentication protocol
#   between Vehicle and RSU entities. Demonstrates authentication using both simulated
#   and real (ZoKrates-based) zero-knowledge proof workflows, as well as a blockchain verification simulation.
#   Includes tests for basic connection with related software/tools, such as ZoKrates and SUMO
#
# @details
#   - Simulates generation of one-time passwords (OTP) and timestamps by vehicles
#   - Demonstrates creation of zero-knowledge proofs (ZKP) for OTP and timestamp
#   - Shows verification of ZKPs by RSUs using both simulated (hash-based) and real ZoKrates CLI methods
#   - Includes a workflow for simulating blockchain-based verification and logging
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
    check_file_exists
)

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
    # SUMO_PORT_BASIC,
    # SUMO_PORT_CONFIG,
    DEBUG_MODE as DEFAULT_DEBUG_MODE,
    PRINT_DATA as DEFAULT_PRINT_DATA,
    SUMO_TOOLS_PATH, 
    SUMO_SIMPLE_NET_FILE,
    SUMO_INTERSECTION_CONFIG_FILE,
    SUMO_PORT_DATA,
    SUMO_PORT_DATA_CONFIG,
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
    SUMO_PORT_RSUWITHDELAY,
    PORTS_TO_CLEANUP
)


# Unused, Leftover Functions
# ##
# # @brief Set whether to print data in the SUMO interface
# # @param enabled True to enable printing data, False to disable
# # @details
# #     Sets the print_data attribute in the SUMO interface
# ##
# def set_print_data(enabled):
    
#     global PRINT_DATA
#     PRINT_DATA = enabled


## @var tested
# @brief Global variable to track the number of tests executed
tested = 0

## @var passed
# @brief Global variable to track the number of tests that passed
passed = 0

## @var DEBUG_MODE
# @brief Global variable to control debug output
DEBUG_MODE = DEFAULT_DEBUG_MODE

## @var PRINT_DATA
# @brief Global variable to control whether to print data in the SUMO interface
PRINT_DATA = DEFAULT_PRINT_DATA


# @brief Enable or disable debug mode for detailed output
# @param enabled True to enable debug mode, False to disable
# @details
#   Sets the global DEBUG_MODE variable and propagates debug mode to all relevant modules/classes
#
# Steps:
#   1. Set the global DEBUG_MODE variable
#   2. Set debug mode for ZoKrates, (Blockchain), and SUMO interfaces
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
# @brief Test the workflow using a simulated ZKP (hash-based)
# @details
#   Simulates authentication between a vehicle and RSU using a hash-based ZKP
#
# Steps:
#   1. Generate a random vehicle secret and create Vehicle entity
#   2. Vehicle generates an OTP and timestamp
#   3. Vehicle creates a simulated ZKP proof (hash-based) for the OTP and timestamp

#   4. Verify the ZKP proof by comparing with expected proof
#   5. Output the result of the verification and authentication status
##
def test_VehicleRsuBasicInteraction_SimulatedZkp():
    
    # Print test header
    print("\n=== Vehicle - Rsu Basic Interaction; Simulated Zkp ===")
    
    # Use global variables to track tests, increment tested count
    global tested, passed
    tested += 1
    
    # Start timer for the test
    timer = Timer("Vehicle - Rsu Basic Interaction; Simulated Zkp Test Timer")
    timer.start()
    
    # vehicle_id - identifier for the vehicle
    vehicle_id = "VEH123"
    
    # vehicle_secret - randomly generated secret for the vehicle
    vehicle_secret = secrets.token_hex(16)
    
    # vehicle - create Vehicle entity with ID and secret
    vehicle = Vehicle(vehicle_id, vehicle_secret)
    
    # unused_rsu = RSU({vehicle_id: vehicle_secret})

    # otp - one-time password generated by the vehicle
    # timestamp - timestamp of OTP generation
    otp, timestamp = vehicle.generate_otp()
    
    # Print debug information of otp and timestamp if DEBUG_MODE is enabled
    if DEBUG_MODE:
        print(f"\n[Simulated] OTP: {otp}\n\nTimestamp: {timestamp}\n")
        
    # zkp_proof - simulated ZKP proof generated by the vehicle
    zkp_proof = generate_zkp_proof_simulated(otp, timestamp)
    
    # Print ZKP proof if DEBUG_MODE is enabled
    if DEBUG_MODE:
        print(f"[Simulated] ZKP Proof: {zkp_proof}\n")
        
    # expected_zkp - expected ZKP proof for verification
    expected_zkp = generate_zkp_proof_simulated(otp, timestamp)
    
    # verification_result - result of ZKP verification
    verification_result = (zkp_proof == expected_zkp)
    
    # Print verification result if DEBUG_MODE is enabled
    if DEBUG_MODE:
        print(f"[Simulated] Verification result: {verification_result}\n")

    # Print authentication result, increment passed count if successful
    if verification_result:
        passed += 1
        print("[Simulated] Vehicle authenticated. Session started.\n")
        
    else:
        print("[Simulated] Authentication failed.\n")
    
    # Stop the timer for the test
    timer.stop()
    # Print elapsed time for the test
    print(timer)


##
# @brief Simulate the full workflow, using simulated ZKP and simulated blockchain verification and logging
# @details
#   Simulates authentication and blockchain verification using hash-based ZKP
#
# Steps:
#   1. Generate a random vehicle secret and create Vehicle entity
#   2. Vehicle generates an OTP and timestamp
#   3. Vehicle creates a simulated ZKP proof (hash-based) for the OTP and timestamp
#   4. Verify the ZKP proof by comparing with expected proof
#   5. Simulate blockchain verification and logging if DEBUG_MODE is enabled
#   6. Output the result of the infrastructure access decision
##
def test_VehicleRsuBasicInteraction_SimulatedZkpAndBlockchain():
    
    # Print test header
    print("\n=== Vehicle - Rsu Basic Interaction; Simulated Zkp And Blockchain ===")
    
    # Use global variables to track tests, increment tested count
    global tested, passed
    tested += 1
    
    # Start timer for the test
    timer = Timer("Vehicle - Rsu Basic Interaction; Simulated Zkp And Blockchain Test Timer")
    timer.start()
    
    # vehicle_id - identifier for the vehicle
    vehicle_id = "VEH123"
    
    # vehicle_secret - randomly generated secret for the vehicle
    vehicle_secret = secrets.token_hex(16)
    
    # vehicle - create Vehicle entity with ID and secret
    vehicle = Vehicle(vehicle_id, vehicle_secret)
    
    # unused_rsu = RSU({vehicle_id: vehicle_secret})

    # otp - one-time password generated by the vehicle
    # timestamp - timestamp of OTP generation
    otp, timestamp = vehicle.generate_otp()
    
    # Print debug information of otp and timestamp if DEBUG_MODE is enabled
    if DEBUG_MODE:
        print(f"\n[Simulated] OTP: {otp}\n\nTimestamp: {timestamp}\n")
        
    # zkp_proof - simulated ZKP proof generated by the vehicle
    zkp_proof = generate_zkp_proof_simulated(otp, timestamp)
    
    # Print ZKP proof if DEBUG_MODE is enabled
    if DEBUG_MODE:
        print(f"[Simulated] ZKP Proof: {zkp_proof}\n")
    
    # expected_zkp - expected ZKP proof for verification
    expected_zkp = generate_zkp_proof_simulated(otp, timestamp)
    
    # verification_result - result of ZKP verification
    verification_result = (zkp_proof == expected_zkp)
    
    # Print verification result if DEBUG_MODE is enabled
    if DEBUG_MODE:
        print(f"[Simulated] RSU Verification result: {verification_result}\n")

    # outcome - result of blockchain verification and access decision if DEBUG_MODE is enabled, else just verification_result
    outcome = simulate_blockchain_verification(vehicle_id, zkp_proof, timestamp, verification_result) if DEBUG_MODE else verification_result
    
    # Output the result of the infrastructure access decision, increment passed count if successful
    if outcome:
        passed += 1
        print("[Simulated] Access granted by infrastructure.\n")
        
    else:
        print("[Simulated] Access denied by infrastructure.\n")
    
    # Stop the timer for the test
    timer.stop()
    # Print elapsed time for the test
    print(timer)


##
# @brief End-to-end scenario: Vehicle authenticates successfully and is logged on blockchain
# @details
#   Simulates a successful authentication scenario for a vehicle
#
# Steps:
#   1. Create vehicle with random secret
#   2. Vehicle generates OTP and timestamp
#   3. Vehicle creates simulated ZKP proof
#   4. Verify ZKP proof by comparing with expected proof
#   5. Simulate blockchain verification if DEBUG_MODE is enabled
#   6. Output the result of the infrastructure access decision
##
def test_EndToEnd_SimulatedZkpAndBlockchain_Success():
    
    # Print test header
    print("\n=== End - To - End; Simulated Zkp And Blockchain; Success Test ===")
    
    # Use global variables to track tests, increment tested count
    global tested, passed
    tested += 1
    
    # Start timer for the test
    timer = Timer("End - To - End; Simulated Zkp And Blockchain; Success Test Timer")
    timer.start()
    
    # vehicle_id - identifier for the vehicle
    vehicle_id = "VEH001"
    
    # vehicle_secret - randomly generated secret for the vehicle
    vehicle_secret = secrets.token_hex(16)
    
    # vehicle - create Vehicle entity with ID and secret
    vehicle = Vehicle(vehicle_id, vehicle_secret)
    
    # unused_rsu = RSU({vehicle_id: vehicle_secret})

    # otp - one-time password generated by the vehicle
    # timestamp - timestamp of OTP generation
    otp, timestamp = vehicle.generate_otp()
    
    # Print debug information if DEBUG_MODE is enabled
    if DEBUG_MODE:
        print(f"\nVehicle {vehicle_id} generated OTP: {otp} at {timestamp}\n")
        
    # zkp_proof - simulated ZKP proof generated by the vehicle
    zkp_proof = generate_zkp_proof_simulated(otp, timestamp)
    
    # Print ZKP proof if DEBUG_MODE is enabled
    if DEBUG_MODE:
        print(f"Vehicle {vehicle_id} created ZKP proof: {zkp_proof}\n")
    
    # expected_zkp - expected ZKP proof for verification
    expected_zkp = generate_zkp_proof_simulated(otp, timestamp)
    
    # verification_result - result of ZKP verification
    verification_result = (zkp_proof == expected_zkp)
    
    # Print verification result if DEBUG_MODE is enabled
    if DEBUG_MODE:
        print(f"RSU verification result: {verification_result}\n")

    # outcome - result of blockchain verification and access decision if DEBUG_MODE is enabled, else just verification_result
    outcome = simulate_blockchain_verification(vehicle_id, zkp_proof, timestamp, verification_result) if DEBUG_MODE else verification_result
    
    # Output the result of the infrastructure access decision, increment passed count if successful
    if outcome:
        passed += 1
        print("Access granted by infrastructure.\n")
    
    else:
        print("Access denied by infrastructure.\n")
    
    # Stop the timer for the test
    timer.stop()
    # Print elapsed time for the test
    print(timer)


##
# @brief End-to-end scenario: Vehicle fails authentication due to wrong secret
# @details
#   Simulates a failed authentication scenario for a vehicle with incorrect secret
#
# Steps:
#   1. Create vehicle with wrong secret and generate correct secret for comparison
#   2. Vehicle generates OTP and timestamp
#   3. Vehicle creates simulated ZKP proof
#   4. Generate expected ZKP proof using correct secret and compare
#   5. Simulate blockchain verification if DEBUG_MODE is enabled
#   6. Output expected denial of infrastructure access
##
def test_EndToEnd_SimulatedZkpAndBlockchain_Failure():
    
    # Print test header
    print("\n=== End - To - End; Simulated Zkp And Blockchain; Failure Test ===")
    
    # Use global variables to track tests, increment tested count
    global tested, passed
    tested += 1
    
    # Start timer for the test
    timer = Timer("End - To - End; Simulated Zkp And Blockchain; Failure Test Timer")
    timer.start()
    
    # vehicle_id - identifier for the vehicle
    vehicle_id = "VEH001"
    
    # correct_secret - randomly generated secret for the vehicle
    correct_secret = secrets.token_hex(16)
    
    # wrong_secret - randomly generated secret for the vehicle that will be used to simulate failure
    wrong_secret = secrets.token_hex(16)
    
    # vehicle - create Vehicle entity with ID and wrong secret
    vehicle = Vehicle(vehicle_id, wrong_secret)
    
    # unused_rsu = RSU({vehicle_id: correct_secret})

    # otp - one-time password generated by the vehicle
    # timestamp - timestamp of OTP generation
    otp, timestamp = vehicle.generate_otp()
    
    # Print debug information if DEBUG_MODE is enabled
    if DEBUG_MODE:
        print(f"\nVehicle {vehicle_id} generated OTP: {otp} at {timestamp}\n")
        
    # zkp_proof - simulated ZKP proof generated by the vehicle
    zkp_proof = generate_zkp_proof_simulated(otp, timestamp)
    
    # Print ZKP proof if DEBUG_MODE is enabled
    if DEBUG_MODE:
        print(f"Vehicle {vehicle_id} created ZKP proof: {zkp_proof}\n")
        
    # otp_expected - expected OTP generated using the correct secret
    otp_expected, _ = Vehicle(vehicle_id, correct_secret).generate_otp()
    
    # expected_zkp - expected ZKP proof for verification
    expected_zkp = generate_zkp_proof_simulated(otp_expected, timestamp)
    
    # verification_result - result of ZKP verification
    verification_result = (zkp_proof == expected_zkp)
    
    # Print verification result if DEBUG_MODE is enabled
    if DEBUG_MODE:
        print(f"RSU verification result: {verification_result}\n")

    # outcome - result of blockchain verification and access decision if DEBUG_MODE is enabled, else just verification_result
    outcome = simulate_blockchain_verification(vehicle_id, zkp_proof, timestamp, verification_result) if DEBUG_MODE else verification_result
    
    # Output the result of the infrastructure access decision, increment passed count if successful
    if outcome:
        print("Access granted by infrastructure (unexpected).\n")
        
    else:
        passed += 1
        print("Access denied by infrastructure (expected).\n")
    
    # Stop the timer for the test
    timer.stop()
    # Print elapsed time for the test
    print(timer)


##
# @brief Test the connection and workflow with ZoKrates CLI using zokrates/dummy.zok
# @details
#   Runs ZoKrates CLI workflow with fixed inputs
#
# Steps:
#   1. Set circuit path and fixed inputs (a=3, b=4)
#   2. Run ZoKrates workflow (compile, setup, compute witness, generate proof, verify)
#   3. Print verification result and output workflow result
##
def test_Zokrates_BasicConnectionTest_UsingDummyCircuit():
    
    # Print test header
    print("\n=== Zokrates Basic Connection (using dummy.zok) Test ===")
    
    # Use global variables to track tests, increment tested count
    global tested, passed
    tested += 1
    
    # Start timer for the test
    timer = Timer("Zokrates Basic Connection (using dummy.zok) Test Timer")
    timer.start()
    
    # circuit_path - Set the circuit path for ZoKrates from settings
    circuit_path = ZOKRATES_DUMMY_CIRCUIT
    
    # args - Fixed inputs to use for computing witness (a=3, b=4)
    args = ["3", "4"]
    
    # verification_result - Run ZoKrates workflow with the given circuit and args
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
    
    # Stop the timer for the test
    timer.stop()
    # Print elapsed time for the test
    print(timer)


##
# @brief Test the end-to-end ZoKrates workflow using zokrates/dummy.zok and random inputs
# @details
#   Simulates a real ZKP workflow using the ZoKrates CLI
#
# Steps:
#   1. Generate random field inputs for dummy.zok
#   2. Run ZoKrates workflow (compile, setup, compute witness, generate proof, verify)
#   3. Print verification result and output workflow result
##
def test_PartialWorkflow_RealZokrates_UsingDummyCircuit():
    
    # Print test header
    print("\n=== Partial Workflow - Real Zokrates (using dummy.zok) Test ===")
    
    # Use global variables to track tests, increment tested count
    global tested, passed
    tested += 1
    
    # Start timer for the test
    timer = Timer("Partial Workflow - Real Zokrates (using dummy.zok) Test Timer")
    timer.start()
    
    # circuit_path - Set the circuit path for ZoKrates from settings
    circuit_path = ZOKRATES_DUMMY_CIRCUIT
    
    # a, b - Generate random field inputs for dummy.zok (1 <= a,b <= 100)
    a = random.randint(1, 100)
    b = random.randint(1, 100)
    
    # If DEBUG_MODE is enabled, print the inputs
    if DEBUG_MODE:
        print(f"Inputs: a={a}, b={b}")
    
    # args - Prepare arguments as strings for ZoKrates CLI
    args = [str(a), str(b)]
    
    # verification_result - Run ZoKrates workflow with the given circuit and args
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
    
    # Stop the timer for the test
    timer.stop()
    # Print elapsed time for the test
    print(timer)


##
# @brief Simulated ZKP isolated test with multiple vehicles
# @details
#   Simulates authentication for multiple vehicles using hash-based ZKP
#
# Steps:
#   1. Create multiple vehicles, each with a unique secret
#   2. For each vehicle, generate OTP and timestamp, create simulated ZKP proof
#   3. Verify each ZKP proof by comparing with expected proof
#   4. Print whether all vehicles authenticated successfully
##
def test_PartialWorkflow_MultipleVehicles_Simulated():
    
    # Print test header
    print("\n=== Partial Workflow - Multiple Vehicles; Simulated Test ===")
    
    # Use global variables to track tests, increment tested count
    global tested, passed
    tested += 1
    
    # Start timer for the test
    timer = Timer("Partial Workflow - Multiple Vehicles; Simulated Test Timer")
    timer.start()
    
    # num_vehicles - Number of vehicles to simulate
    num_vehicles = 3
    
    # vehicles - Dictionary to hold Vehicle entities
    vehicles = {}
    
    # unused_rsu_secrets = {}
    
    # For each vehicle, create a unique ID and secret
    for i in range(num_vehicles):
        
        # vid - Generate vehicle ID formatted as VEH001, VEH002, etc
        vid = f"VEH{i+1:03d}"
        
        # secret - Generate a random secret for the vehicle and store it
        secret = secrets.token_hex(16)
        vehicles[vid] = Vehicle(vid, secret)
        
        # rsu_secrets[vid] = secret
    
    # # Create RSU with the secrets of all vehicles
    # # This simulates the RSU having access to all vehicle secrets
    
    # unused_rsu = RSU(rsu_secrets)
    
    # all_passed - Initialize a flag to track if all vehicles passed authentication
    all_passed = True
    
    # # Circuit path for the simulated ZKP proof
    # unused_circuit_path = "zokrates/dummy.zok"
    
    # For each vehicle, generate OTP, timestamp, and ZKP proof
    for vid, vehicle in vehicles.items():
        
        # otp - Generate OTP for the vehicle
        # timestamp - Generate timestamp for the vehicle
        otp, timestamp = vehicle.generate_otp()
        
        # zkp_proof - Generate a simulated ZKP and expected ZKP from the same OTP and timestamp
        zkp_proof = generate_zkp_proof_simulated(otp, timestamp)
        
        # expected_zkp - Generate expected ZKP proof for verification
        expected_zkp = generate_zkp_proof_simulated(otp, timestamp)
        
        # result - Verify that the ZKP proof is equal to the expected proof
        result = (zkp_proof == expected_zkp)
        
        # If DEBUG_MODE is enabled, print the verification result
        if DEBUG_MODE:
            print(f"Vehicle {vid}: Verification result: {result}")
        
        # all_passed - If any vehicle fails, set all_passed to False
        all_passed = all_passed and result
    
    # Output the result of the authentication for all vehicles, incrementing passed count if successful
    if all_passed:
        passed += 1
        print("[Simulated] All vehicles authenticated successfully.\n")
        
    else:
        print("[Simulated] Some vehicles failed authentication.\n")
    
    # Stop the timer for the test
    timer.stop()
    # Print elapsed time for the test
    print(timer)


##
# @brief Simulated end-to-end test with multiple vehicles
# @details
#   Simulates authentication and blockchain verification for multiple vehicles
#
# Steps:
#   1. Create multiple vehicles, each with a unique secret
#   2. For each vehicle, generate OTP and timestamp, create simulated ZKP proof
#   3. Verify each ZKP proof by comparing with expected proof
#   4. Simulate blockchain verification if DEBUG_MODE is enabled
#   5. Print whether all vehicles were granted access by infrastructure
##
def test_EndToEnd_MultipleVehicles_Simulated():
    
    # Print test header
    print("\n=== End - To - End; Multiple Vehicles; Simulated Test ===")
    
    # Use global variables to track tests, increment tested count
    global tested, passed
    tested += 1
    
    # Start timer for the test
    timer = Timer("End - To - End; Multiple Vehicles; Simulated Test Timer")
    timer.start()
    
    # num_vehicles - Number of vehicles to simulate
    num_vehicles = 3
    
    # vehicles - Dictionary to hold Vehicle entities
    vehicles = {}
    
    # unused_rsu_secrets = {}
    
    # For each vehicle, create a unique ID and secret
    for i in range(num_vehicles):
        
        # vid - Generate vehicle ID formatted as VEH001, VEH002, etc
        vid = f"VEH{i+1:03d}"
        
        # secret - Generate a random secret for the vehicle and store it
        secret = secrets.token_hex(16)
        vehicles[vid] = Vehicle(vid, secret)
        
        # rsu_secrets[vid] = secret
    
    # # Create RSU with the secrets of all vehicles; this simulates the RSU having access to all vehicle secrets
    # unused_rsu = RSU(rsu_secrets)
    
    # all_passed - Initialize a flag to track if all vehicles passed authentication
    all_passed = True
    
    # unused_circuit_path = "zokrates/dummy.zok"
    
    # For each vehicle, generate OTP, timestamp, and ZKP proof
    for vid, vehicle in vehicles.items():
        
        # otp - Generate OTP for the vehicle
        # timestamp - Generate timestamp for the vehicle
        otp, timestamp = vehicle.generate_otp()
        
        # zkp_proof - Generate a simulated ZKP proof for the OTP and timestamp
        zkp_proof = generate_zkp_proof_simulated(otp, timestamp)
        
        # expected_zkp - Generate expected ZKP proof for verification
        expected_zkp = generate_zkp_proof_simulated(otp, timestamp)
        
        # verification_result - Verify that the ZKP proof is equal to the expected proof
        verification_result = (zkp_proof == expected_zkp)
        
        # outcome - Simulate blockchain verification and logging if DEBUG_MODE is enabled, else just use verification_result
        outcome = simulate_blockchain_verification(vid, zkp_proof, timestamp, verification_result) if DEBUG_MODE else verification_result
        
        if DEBUG_MODE:
            print(f"Vehicle {vid}: RSU result: {verification_result}, Blockchain outcome: {outcome}")
        
        # all_passed - If any vehicle fails, set all_passed to False
        all_passed = all_passed and outcome
    
    # Output the result of the ZoKrates workflow and blockchain verification for all vehicles, increment passed count if successful
    if all_passed:
        passed += 1
        print("[Simulated] All vehicles granted access by infrastructure.\n")
        
    else:
        print("[Simulated] Some vehicles denied access.\n")
    
    # Stop the timer for the test
    timer.stop()
    # Print elapsed time for the test
    print(timer)


##
# @brief Test the connection and workflow with ZoKrates CLI using zokrates/dummy.zok
# @details
#   Runs ZoKrates CLI workflow with fixed inputs
#
# Steps:
#   1. For each vehicle:
#      a. Generate inputs
#      b. Compile ZoKrates circuit
#      c. Run setup
#      d. Compute witness
#      e. Generate proof
#      f. Verify proof
#      g. Clean up ZoKrates artifacts
#   2. Print whether all vehicles' proofs were verified successfully
##
def test_PartialWorkflow_RealZokrates_MultipleVehicles_UsingDummyCircuit():
    
    # Print test header
    print("\n=== Partial Workflow - Real Zokrates; Multiple Vehicles (using dummy.zok) Test ===")
    
    # Use global variables to track tests, increment tested count
    global tested, passed
    tested += 1
    
    # Start timer for the test
    timer = Timer("Partial Workflow - Real Zokrates; Multiple Vehicles (using dummy.zok) Test Timer")
    timer.start()
    
    # circuit_path - Set the circuit path for ZoKrates from settings
    circuit_path = ZOKRATES_DUMMY_CIRCUIT
    
    # num_vehicles - Set the number of vehicles to test
    num_vehicles = 2
    
    # all_passed - Initialize a flag to track if all vehicles passed verification
    all_passed = True
    
    # For each vehicle, generate random inputs and run ZoKrates workflow
    for i in range(num_vehicles):
        
        # a, b - Generate random inputs for the vehicle, random integers between 1 and 100
        a = random.randint(1, 100)
        b = random.randint(1, 100)
        
        # If DEBUG_MODE is enabled, print the inputs
        if DEBUG_MODE:
            print(f"Vehicle {i+1}: Inputs a={a}, b={b}")
        
        # args - Prepare arguments as strings for ZoKrates CLI
        args = [str(a), str(b)]
        
        # verification_result - Run ZoKrates workflow with the given circuit and args
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
    
    # Stop the timer for the test
    timer.stop()
    # Print elapsed time for the test
    print(timer)


##
# @brief ZoKrates-integrated end-to-end test with multiple vehicles (zokrates/dummy.zok + simulated blockchain)
# @details
#   Runs ZoKrates workflow and blockchain verification for multiple vehicles
#
# Steps:
#   1. For each vehicle, generate random inputs
#   2. Run ZoKrates workflow (compile, setup, compute witness, generate proof, verify)
#   3. Simulate blockchain verification if DEBUG_MODE is enabled
#   4. Print verification and blockchain result for each vehicle and output overall result
##
def test_PartialWorkflow_RealZokratesSimulatedBlockchain_MultipleVehicles_UsingDummyCircuit():
    
    # Print test header
    print("\n=== Partial Workflow - Real Zokrates, Simulated Blockchain; Multiple Vehicles (using dummy.zok) Test ===")
    
    # Use global variables to track tests, increment tested count
    global tested, passed
    tested += 1
    
    # Start timer for the test
    timer = Timer("Partial Workflow - Real Zokrates, Simulated Blockchain; Multiple Vehicles (using dummy.zok) Test Timer")
    timer.start()
    
    # circuit_path - Set the circuit path for ZoKrates from settings
    circuit_path = ZOKRATES_DUMMY_CIRCUIT
    
    # num_vehicles - Set the number of vehicles to test
    num_vehicles = 2
    
    # all_passed - Initialize a flag to track if all vehicles passed verification
    all_passed = True
    
    # For each vehicle, generate random inputs and run ZoKrates workflow
    # and simulate blockchain verification
    for i in range(num_vehicles):
        
        # vid - Generate vehicle ID formatted as VEH001, VEH002, etc
        vid = f"ZOKR_VEH{i+1:03d}"
        
        # a, b - Generate random inputs for the vehicle, random integers between 1 and 100
        a = random.randint(1, 100)
        b = random.randint(1, 100)
        
        # If DEBUG_MODE is enabled, print the vehicle ID and the inputs
        if DEBUG_MODE:
            print(f"Vehicle {vid}: Inputs a={a}, b={b}")
        
        # args - Prepare arguments as strings for ZoKrates CLI
        args = [str(a), str(b)]
        
        # verification_result - Run ZoKrates workflow with the given circuit and args
        verification_result = run_zokrates_workflow(circuit_path, args)
        
        # If DEBUG_MODE is enabled, print the verification result
        if DEBUG_MODE:
            print(f"Vehicle {vid}: ZoKrates verification result: {verification_result}")
        
        # outcome - Simulate blockchain verification and logging if DEBUG_MODE is enabled, else just use verification_result
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
    
    # Stop the timer for the test
    timer.stop()
    # Print elapsed time for the test
    print(timer)


##
# @brief Test connecting to SUMO via TraCI, retrieving and storing simulation data
# @param print_data If True, print simulation data to screen
# @details
#   Tests SUMO connection and data retrieval using TraCI
#
# Steps:
#   1. Start SUMO with a simple network
#   2. Connect via TraCI
#   3. Retrieve simulation time, vehicle IDs, and positions
#   4. Print/store the data
#   5. Clean up
##
def test_DataTransfer_SumoAndTraCI_UsingSimpleNet(print_data=True):
    
    # Print test header
    print("\n=== Data Transfer (using simple.net.xml) Test ===")
    
    # Use global variables to track tests, increment tested count
    global tested, passed
    tested += 1
    
    # Start timer for the test
    timer = Timer("Data Transfer (using simple.net.xml) Test Timer")
    timer.start()

    # port - Define the port for SUMO TraCI connection
    port = SUMO_PORT_DATA
    
    # SUMO_NET_FILE - Path to the SUMO network file
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
    
    # If proc or traci is None, it means the SUMO process or TraCI connection failed, so return early
    if proc is None or traci is None:
        return
    
    # Try to run the SUMO simulation for 5 steps and retrieve data
    try:
        
        unused_sim_data = run_sumo_simulation_flexible(traci, 5, print_data)
        
        # passed_local - If no exceptions occurred, set passed_local to True
        passed_local = True
    
    # If any exception occurs during the TraCI data transfer, print the error and set passed_local to False
    except Exception as e:
        
        print(f"[SUMO TraCI Test] Error during TraCI data transfer: {e}")
        passed_local = False

    # Finally block to ensure cleanup regardless of success or failure
    finally:
        
        # Cleanup SUMO and TraCI processes
        cleanup_sumo_and_traci(proc, port, traci)
        
        # Clean up temp config/output if created
        if temp_config and os.path.exists(temp_config):
            
            # Attempt to remove the temporary config file with os.unlink
            try:
                os.unlink(temp_config)
            
            # If unlink fails do nothing, just pass
            except: 
                pass
        
        # Clean up temp output directory if created
        if temp_output_dir and os.path.exists(temp_output_dir):
            
            # Attempt to remove the temporary output directory with shutil.rmtree
            try: 
                shutil.rmtree(temp_output_dir)
            
            # If rmtree fails do nothing, just pass
            except: 
                pass

    # If passed_local is True, increment passed count and print success message
    if passed_local:
        passed += 1
        print("[SUMO TraCI Test] Data transfer test succeeded!\n")
        
    else:
        print("[SUMO TraCI Test] Data transfer test failed.\n")
    
    # Stop the timer for the test
    timer.stop()
    
    # Kill any processes still running on the specified port
    kill_processes_on_port(port)
    
    # Print elapsed time for the test
    print(timer)


##
# @brief Test connecting to SUMO via TraCI using a .sumocfg file, retrieving and storing simulation data for 100 steps
# @param print_data If True, print simulation data to screen
# @details
#   Tests SUMO connection and data retrieval using TraCI with a .sumocfg file
#
# Steps:
#   1. Start SUMO with a configuration file
#   2. Connect via TraCI
#   3. Retrieve simulation time, vehicle IDs, and positions for 100 steps
#   4. Print/store the data
#   5. Clean up
##
def test_DataTransfer_SumoAndTraCI_UsingIntersection1Config(print_data=True):
    
    # Print test header
    print("\n=== Data Transfer (using intersection1.sumocfg) Test ===")
    
    # Use global variables to track tests, increment tested count
    global tested, passed
    tested += 1
    
    # Start timer for the test
    timer = Timer("Data Transfer (using intersection1.sumocfg) Test Timer")
    timer.start()

    # port - Define the port for SUMO TraCI connection from settings
    port = SUMO_PORT_DATA_CONFIG
    
    # SUMO_SUMOCFG_FILE - Path to the SUMO configuration file
    SUMO_SUMOCFG_FILE = SUMO_INTERSECTION_CONFIG_FILE

    # Check if the SUMO configuration file exists, if not, print error (from check_file_exists) and return
    if not check_file_exists(SUMO_SUMOCFG_FILE, "SUMO configuration file"):
        return

    # Start SUMO and connect via TraCI
    proc, traci, _, temp_config, temp_output_dir = start_sumo_simulation(
        file_path=SUMO_SUMOCFG_FILE,
        is_config=True,
        port=port,
        sumo_binary="sumo",
        connect_traci=True,
        sumo_tools_path=SUMO_TOOLS_PATH
    )

    # If proc or traci is None, it means the SUMO process or TraCI connection failed, so return early
    if proc is None or traci is None:
        return

    # Try to run the SUMO simulation for 100 steps and retrieve data
    try:
        unused_sim_data = run_sumo_simulation_flexible(traci, 100, print_data)
        
        # passed_local - If no exceptions occurred, set passed_local to True
        passed_local = True
    
    # If any exception occurs during the TraCI data transfer, print the error and set passed_local to False
    except Exception as e:
        print(f"[SUMO TraCI Test] Error during TraCI data transfer: {e}")
        passed_local = False
    
    # In the finally block, ensure cleanup regardless of success or failure
    finally:
        
        # Cleanup SUMO and TraCI processes
        cleanup_sumo_and_traci(proc, port, traci)
        
        # Clean up temp config/output if created
        if temp_config and os.path.exists(temp_config):
            
            # Attempt to remove the temporary config file with os.unlink
            try:
                os.unlink(temp_config)
                
            # If unlink fails do nothing, just pass
            except:
                pass
        
        # Clean up temp output directory if created
        if temp_output_dir and os.path.exists(temp_output_dir):
            
            # Attempt to remove the temporary output directory with shutil.rmtree
            try:
                shutil.rmtree(temp_output_dir)
            
            # If rmtree fails do nothing, just pass
            except:
                pass

    # Print the result of the test based on passed_local and increment passed count if successful
    if passed_local:
        passed += 1
        print("[SUMO TraCI Test] .sumocfg data transfer test succeeded!\n")
        
    else:
        print("[SUMO TraCI Test] .sumocfg data transfer test failed.\n")

    # Stop the timer for the test
    timer.stop()
    
    # Kill any processes still running on the specified port
    kill_processes_on_port(port)
    
    # Print elapsed time for the test
    print(timer)


##
# @brief Test connecting to SUMO via TraCI using intersection2.sumocfg with explicit vehicles
# @param print_data If True, print simulation data to screen
# @details
#   Tests SUMO connection and data retrieval using TraCI with intersection2.sumocfg
#
# Steps:
#   1. Start SUMO with intersection2.sumocfg
#   2. Connect via TraCI
#   3. Retrieve simulation time, vehicle IDs, and positions
#   4. Print/store the data
#   5. Clean up
##
def test_DataTransfer_SumoAndTraCI_UsingIntersection2Config(print_data=True):
    
    # Print test header
    print("\n=== Data Transfer (using intersection2.sumocfg) Test ===")
    
    # Use global variables to track tests, increment tested count
    global tested, passed
    tested += 1
    
    # Start timer for the test
    timer = Timer("Data Transfer (using intersection2.sumocfg) Test Timer")
    timer.start()

    # port - Define the port for SUMO TraCI connection from settings
    port = SUMO_PORT_DATA_INTERSECTION2_CONFIG
    
    # Check if the intersection2.sumocfg file exists, if not, print error (from check_file_exists) and return
    if not check_file_exists(SUMO_INTERSECTION2_CONFIG_FILE, "SUMO intersection2 configuration file"):
        return

    # Start SUMO and connect via TraCI
    proc, traci, _, temp_config, temp_output_dir = start_sumo_simulation(
        file_path=SUMO_INTERSECTION2_CONFIG_FILE,
        is_config=True,
        port=port,
        sumo_binary="sumo",
        connect_traci=True,
        sumo_tools_path=SUMO_TOOLS_PATH
    )

    # If proc or traci is None, it means the SUMO process or TraCI connection failed, so return early
    if proc is None or traci is None:
        return

    # Try to run the SUMO simulation for 100 steps and retrieve data
    try:
        unused_sim_data = run_sumo_simulation_flexible(traci, 100, print_data)
        passed_local = True
    
    # If any exception occurs during the TraCI data transfer, print the error and set passed_local to False
    except Exception as e:
        print(f"[SUMO TraCI Test] Error during TraCI data transfer: {e}")
        passed_local = False
    
    # In the finally block, ensure cleanup regardless of success or failure
    finally:
        
        # Cleanup SUMO and TraCI processes
        cleanup_sumo_and_traci(proc, port, traci)
        
        # Clean up temp config/output if created
        if temp_config and os.path.exists(temp_config):
            
            # Attempt to remove the temporary config file with os.unlink
            try:
                os.unlink(temp_config)
            
            # If unlink fails do nothing, just pass
            except:
                pass
            
        # Clean up temp output directory if created
        if temp_output_dir and os.path.exists(temp_output_dir):
            
            # Attempt to remove the temporary output directory with shutil.rmtree
            try:
                shutil.rmtree(temp_output_dir)
            
            # If rmtree fails do nothing, just pass
            except:
                pass

    # Print the result of the test based on passed_local and increment passed count if successful
    if passed_local:
        passed += 1
        print("[SUMO TraCI Test] intersection2.sumocfg data transfer test succeeded!\n")
        
    else:
        print("[SUMO TraCI Test] intersection2.sumocfg data transfer test failed.\n")
    
    # Stop the timer for the test
    timer.stop()
    
    # Kill any processes still running on the specified port
    kill_processes_on_port(port)
    
    # Print elapsed time for the test
    print(timer)


##
# @brief Test connecting to SUMO via TraCI using straightaway1.sumocfg
# @param print_data If True, print simulation data to screen
# @details
#   Tests SUMO connection and data retrieval using TraCI with straightaway1.sumocfg
#
# Steps:
#   1. Start SUMO with straightaway1.sumocfg
#   2. Connect via TraCI
#   3. Retrieve simulation time, vehicle IDs, and positions
#   4. Print/store the data
#   5. Clean up
##
def test_DataTransfer_SumoAndTraCI_UsingStraightaway1Config(print_data=True):
    
    # Print test header
    print("\n=== Data Transfer (using straightaway1.sumocfg) Test ===")
    
    # Use global variables to track tests, increment tested count
    global tested, passed
    tested += 1
    
    # Start timer for the test
    timer = Timer("Data Transfer (using straightaway1.sumocfg) Test Timer")
    timer.start()

    # port - Define the port for SUMO TraCI connection from settings
    port = SUMO_PORT_DATA_STRAIGHTAWAY1_CONFIG
    
    # Check if the straightaway1.sumocfg file exists, if not, print error (from check_file_exists) and return
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

    # If proc or traci is None, it means the SUMO process or TraCI connection failed, so return early
    if proc is None or traci is None:
        return

    # Try to run the SUMO simulation for 100 steps and retrieve data
    try:
        
        # Use the centralized run_sumo_simulation function
        unused_sim_data = run_sumo_simulation_flexible(traci, 100, print_data)
        
        # passed_local - If no exceptions occurred, set passed_local to True
        passed_local = True
    
    # If any exception occurs during the TraCI data transfer, print the error and set passed_local to False
    except Exception as e:
        print(f"[SUMO TraCI Test] Error during TraCI data transfer: {e}")
        passed_local = False
    
    # In the finally block, ensure cleanup regardless of success or failure
    finally:
        
        # Cleanup SUMO and TraCI processes
        cleanup_sumo_and_traci(proc, port, traci)
        
        # Clean up temp config/output if created
        if temp_config and os.path.exists(temp_config):
            
            # Attempt to remove the temporary config file with os.unlink
            try:
                os.unlink(temp_config)
            
            # If unlink fails do nothing, just pass
            except:
                pass
        
        # Clean up temp output directory if created
        if temp_output_dir and os.path.exists(temp_output_dir):
            
            # Attempt to remove the temporary output directory with shutil.rmtree
            try:
                shutil.rmtree(temp_output_dir)
            
            # If rmtree fails do nothing, just pass
            except:
                pass

    # Print the result of the test based on passed_local and increment passed count if successful
    if passed_local:
        passed += 1
        print("[SUMO TraCI Test] straightaway1.sumocfg data transfer test succeeded!\n")
    else:
        print("[SUMO TraCI Test] straightaway1.sumocfg data transfer test failed.\n")
    
    # Stop the timer for the test
    timer.stop()
    
    # Kill any processes still running on the specified port
    kill_processes_on_port(port)
    
    # Print elapsed time for the test
    print(timer)


##
# @brief Test connecting to SUMO via TraCI using straightaway2.sumocfg
# @param print_data If True, print simulation data to screen
# @details
#   Tests SUMO connection and data retrieval using TraCI with straightaway2.sumocfg
#
# Steps:
#   1. Start SUMO with straightaway2.sumocfg
#   2. Connect via TraCI
#   3. Retrieve simulation time, vehicle IDs, and positions
#   4. Print/store the data
#   5. Clean up
##
def test_DataTransfer_SumoAndTraCI_UsingStraightaway2Config(print_data=True):
    
    # Print test header
    print("\n=== Data Transfer (using straightaway2.sumocfg) Test ===")
    
    # Use global variables to track tests, increment tested count
    global tested, passed
    tested += 1
    
    # Start timer for the test
    timer = Timer("Data Transfer (using straightaway2.sumocfg) Test Timer")
    timer.start()

    # port - Define the port for SUMO TraCI connection from settings
    port = SUMO_PORT_DATA_STRAIGHTAWAY2_CONFIG

    # Check if the straightaway2.sumocfg file exists, if not, print error (from check_file_exists) and return
    if not check_file_exists(SUMO_STRAIGHTAWAY2_CONFIG_FILE, "SUMO straightaway2 configuration file"):
        return

    # Start SUMO and connect via TraCI
    proc, traci, _, temp_config, temp_output_dir = start_sumo_simulation(
        file_path=SUMO_STRAIGHTAWAY2_CONFIG_FILE,
        is_config=True,
        port=port,
        sumo_binary="sumo",
        connect_traci=True,
        sumo_tools_path=SUMO_TOOLS_PATH
    )

    # If proc or traci is None, it means the SUMO process or TraCI connection failed, so return early
    if proc is None or traci is None:
        return

    # Try to run the SUMO simulation for 100 steps and retrieve data
    try:
        
        unused_sim_data = run_sumo_simulation_flexible(traci, 100, print_data)
        
        # passed_local - If no exceptions occurred, set passed_local to True
        passed_local = True
    
    # If any exception occurs during the TraCI data transfer, print the error and set passed_local to False
    except Exception as e:
        print(f"[SUMO TraCI Test] Error during TraCI data transfer: {e}")
        passed_local = False
    
    # In the finally block, ensure cleanup regardless of success or failure
    finally:
        
        # Cleanup SUMO and TraCI processes
        cleanup_sumo_and_traci(proc, port, traci)
        
        # Clean up temp config/output if created
        if temp_config and os.path.exists(temp_config):
            
            # Attempt to remove the temporary config file with os.unlink
            try:
                os.unlink(temp_config)
            
            # If unlink fails do nothing, just pass
            except:
                pass
        
        # Clean up temp output directory if created
        if temp_output_dir and os.path.exists(temp_output_dir):
            
            # Attempt to remove the temporary output directory with shutil.rmtree
            try:
                shutil.rmtree(temp_output_dir)
            
            # If rmtree fails do nothing, just pass
            except:
                pass

    # Print the result of the test based on passed_local and increment passed count if successful
    if passed_local:
        passed += 1
        print("[SUMO TraCI Test] straightaway2.sumocfg data transfer test succeeded!\n")
    else:
        print("[SUMO TraCI Test] straightaway2.sumocfg data transfer test failed.\n")
    
    # Stop the timer for the test
    timer.stop()
    
    # Kill any processes still running on the specified port
    kill_processes_on_port(port)
    
    # Print elapsed time for the test
    print(timer)


##
# @brief Test manipulating SUMO vehicles in real-time using TraCI with straightaway1.sumocfg
# @param print_data If True, print simulation data to screen
# @details
#   Tests manipulating vehicle parameters (speed, color, position) during a SUMO simulation
#
#       ***Position movement is still buggy. It's not needed in the actual framework, so it's
#                   been left as is after a period of troubleshooting wasn't fruitful***
#
# Steps:
#   1. Start SUMO with straightaway1.sumocfg
#   2. Connect via TraCI
#   3. Run the simulation for several steps to let vehicles appear
#   4. Manipulate vehicle parameters (color, speed, position)
#   5. Continue simulation to observe effects
#   6. Clean up
##
def test_LiveManipulation_SumoAndTraCI_UsingStraightaway1Config(print_data=True):
    
    # Print test header
    print("\n=== Live Manipulation (using straightaway1.sumocfg) Test ===")
    
    # Use global variables to track tests, increment tested count
    global tested, passed
    tested += 1
    
    # Start timer for the test
    timer = Timer("Live Manipulation (using straightaway1.sumocfg) Test Timer")
    timer.start()

    # port - Define the port for SUMO TraCI connection from settings
    port = SUMO_PORT_LIVE_MANIPULATION
    
    # Check if the straightaway1.sumocfg file exists, if not, print error (from check_file_exists) and return
    if not check_file_exists(SUMO_STRAIGHTAWAY1_CONFIG_FILE, "SUMO straightaway1 configuration file"):
        return

    # Start SUMO and connect via TraCI
    proc, traci, _, temp_config, temp_output_dir = start_sumo_simulation(
        file_path=SUMO_STRAIGHTAWAY1_CONFIG_FILE,
        is_config=True,
        port=port,
        sumo_binary="sumo",
        connect_traci=True,
        sumo_tools_path=SUMO_TOOLS_PATH
    )

    # If proc or traci is None, it means the SUMO process or TraCI connection failed, so return early
    if proc is None or traci is None:
        return
    
    # Try to manipulate vehicles in the simulation
    try:
        
        # veh_ids - Initialize an empty list to store vehicle IDs
        veh_ids = []
        
        # Run the simulation for 15 steps to allow vehicles to appear
        for step in range(15):
            
            # Run a simulation step
            traci.simulationStep()
            
            # Get the list of vehicle IDs currently in the simulation
            current_veh_ids = traci.vehicle.getIDList()
            
            # If current_veh_ids is not empty and veh_ids is empty, set veh_ids to current_veh_ids, then break
            if current_veh_ids and not veh_ids:
                veh_ids = current_veh_ids
                
                # If print_data is True, print the detected vehicle IDs
                if print_data:
                    print(f"Vehicles detected in simulation at step {step}: {veh_ids}")
                break
                
        # If no vehicles are present, print a message and set passed_local to False
        if not veh_ids:
            
            print("[SUMO Manipulation Test] No vehicles found in simulation after 15 steps.")
            
            # passed_local - Set to False since no vehicles were found
            passed_local = False
            return
            
        # Select the first vehicle ID for manipulation
        vehicle_id = veh_ids[0]
        
        # initial_speed, initial_position, initial_color - Get the initial state of the vehicle
        initial_speed = traci.vehicle.getSpeed(vehicle_id)
        initial_position = traci.vehicle.getPosition(vehicle_id)
        initial_color = traci.vehicle.getColor(vehicle_id)
        
        # If print_data is True, print the initial state of the vehicle
        if print_data:
            print(f"\nInitial state of vehicle {vehicle_id}:")
            print(f"Speed: {initial_speed:.2f} m/s")
            print(f"Position: ({initial_position[0]:.2f}, {initial_position[1]:.2f})")
            print(f"Color: {initial_color}")

        # Try to change the color of the vehicle
        try:
            
            # Set the vehicle color to red (RGBA format)
            traci.vehicle.setColor(vehicle_id, (255, 0, 0, 255))
            
            # If print_data is True, print the color change
            if print_data:
                print(f"\nChanged color of vehicle {vehicle_id} to red")
        
        # If any exception occurs during color change, print the error
        except Exception as e:
            print(f"Failed to change color: {e}")
        
        # Run a step to apply changes
        traci.simulationStep()

        # Try to change the speed of the vehicle
        try:
            
            # new_speed - Set a new speed for the vehicle
            new_speed = 15.0
            
            # Set the speed of the vehicle
            traci.vehicle.setSpeed(vehicle_id, new_speed)
            
            # If print_data is True, print the speed change
            if print_data:
                print(f"Changed speed of vehicle {vehicle_id} to {new_speed} m/s")
                
        # If any exception occurs during speed change, print the error
        except Exception as e:
            print(f"Failed to change speed: {e}")
        
        # Run a step to apply changes
        traci.simulationStep()

        # post_speed_position - Initialize to None to store position after speed change
        post_speed_position = None
        
        # Try to move vehicle forward along lane - buggy, but included for completeness
        try:
            
            # post_speed_position - Get the position after speed change
            post_speed_position = traci.vehicle.getPosition(vehicle_id)
            
            # lane_id - Get the lane ID of the vehicle
            lane_id = traci.vehicle.getLaneID(vehicle_id)
            
            # current_lane_pos - Get the current lane position of the vehicle
            current_lane_pos = traci.vehicle.getLanePosition(vehicle_id)
            
            # new_lane_pos - Calculate the new lane position (10m forward)
            new_lane_pos = current_lane_pos + 10
            
            # Move the vehicle to the new lane position
            traci.vehicle.moveTo(vehicle_id, lane_id, new_lane_pos)
            
            # If print_data is True, print the movement
            if print_data:
                print(f"Moved vehicle {vehicle_id} 10m forward along lane {lane_id}")
        
        # If any exception occurs during lane movement, print the error
        except Exception as e:
            print(f"Failed to move vehicle along lane: {e}")
        
        # Run several steps to see the effects of all manipulations
        for step in range(15):
            
            # Run a simulation step
            traci.simulationStep()
            
            # Get final state after last step (?)
            if step == 14:
                
                # Try to get the final state of the vehicle
                try:
                    
                    # final_speed - Get the final speed of the vehicle
                    final_speed = traci.vehicle.getSpeed(vehicle_id)
                    
                    # final_position - Get the final position of the vehicle
                    final_position = traci.vehicle.getPosition(vehicle_id)
                    
                    # final_color - Get the final color of the vehicle
                    final_color = traci.vehicle.getColor(vehicle_id)
                    
                    # unused_speed_change - Calculate the change in speed
                    unused_speed_change = final_speed - initial_speed
                    
                    # position_change - Calculate the change in position
                    position_change = final_position[0] - initial_position[0]
                    
                    # speed_position_change - Calculate position change due to speed change
                    speed_position_change = 0
                    
                    # If post_speed_position is available, calculate the position change due to speed
                    if post_speed_position:
                        speed_position_change = post_speed_position[0] - initial_position[0]
                    
                    # unused_manual_and_subsequent - Calculate position change due to manual movement and subsequent steps
                    unused_manual_and_subsequent = position_change - speed_position_change
                    
                    # If print_data is True, print the final state and changes
                    if print_data:
                        print(f"\nFinal state of vehicle {vehicle_id} after manipulations:")
                        print(f"Speed: {final_speed:.2f} m/s (was {initial_speed:.2f} m/s)")
                        print(f"Position: ({final_position[0]:.2f}, {final_position[1]:.2f}) (was ({initial_position[0]:.2f}, {initial_position[1]:.2f}))")
                        print(f"Color: {final_color} (was {initial_color})")
                        
                        print("\n[SUMO Manipulation Test] Successfully manipulated vehicle properties:")
                        print(f"- Speed changed from {initial_speed:.2f} to {final_speed:.2f}")
                        print(f"- Position changed {position_change:.2f} meters (from {initial_position[0]:.2f} to {final_position[0]:.2f})")
                        print(f"- Color changed from {initial_color} to {final_color}")
                    
                    # speed_changed - Change in speed greater than 0.1 m/s
                    speed_changed = abs(final_speed - initial_speed) > 0.1
                    
                    # position_changed - Change in position greater than 5 meters
                    position_changed = abs(position_change) > 5.0
                    
                    # color_changed - Color has changed
                    color_changed = final_color != initial_color
                    
                    # passed_local - All three changes must be true to pass
                    passed_local = speed_changed and position_changed and color_changed
                
                # If any exception occurs during final state retrieval, print the error and set passed_local to False
                except Exception as e:
                    print(f"Error reading final vehicle state: {e}")
                    passed_local = False
    
    # If any exception occurs during the manipulation, print the error and set passed_local to False
    except Exception as e:
        print(f"[SUMO Manipulation Test] Error during vehicle manipulation: {e}")
        passed_local = False
    
    # In the finally block, ensure cleanup regardless of success or failure
    finally:
        
        # Cleanup SUMO and TraCI processes
        cleanup_sumo_and_traci(proc, port, traci)
        
        # Clean up temp config/output if created
        if temp_config and os.path.exists(temp_config):
            
            # Attempt to remove the temporary config file with os.unlink
            try:
                os.unlink(temp_config)
            
            # If unlink fails do nothing, just pass
            except:
                pass
        
        # Clean up temp output directory if created
        if temp_output_dir and os.path.exists(temp_output_dir):
            
            # Attempt to remove the temporary output directory with shutil.rmtree
            try:
                shutil.rmtree(temp_output_dir)
            
            # If rmtree fails do nothing, just pass
            except:
                pass

    # Print the result of the test based on passed_local and increment passed count if successful
    if passed_local:
        passed += 1
        print("[SUMO Manipulation Test] Vehicle manipulation test succeeded!")
    else:
        print("[SUMO Manipulation Test] Vehicle manipulation test failed.")
    
    # Stop the timer for the test
    timer.stop()
    
    # Kill any processes still running on the specified port
    kill_processes_on_port(port)
    
    # Print elapsed time for the test
    print(timer)


##
# @brief Test the zokrates/VtoI_test.zok circuit for vehicle-to-infrastructure authentication
# @details
#   Tests the vehicle-to-infrastructure authentication circuit which uses a commitment scheme
#
# Steps:
#   1. Prepare the VtoI_test.zok circuit
#   2. Generate random secret key and vehicle ID
#   3. Calculate the commitment
#   4. Run the ZoKrates workflow with the circuit and arguments
#   5. Check if the verification was successful
#   6. Clean up
##
def test_Zokrates_UsingVtoICircuit():
    
    # Print test header
    print("\n=== Zokrates (using VtoI_test.zok) Test ===")
    
    # Use global variables to track tests, increment tested count
    global tested, passed
    tested += 1
    
    # Start timer for the test
    timer = Timer("Zokrates (using VtoI_test.zok) Test Timer")
    timer.start()
    
    # circuit_path - Set the path to the ZoKrates circuit file
    circuit_path = "zokrates/VtoI_test.zok"
    
    # sk - Secret key for the vehicle
    sk = random.randint(1, 999)
    
    # vid - Vehicle ID, a random integer
    vid = random.randint(1, 999999999)
    
    # commitment - Calculate the commitment using: commitment = sk^2 + vid
    commitment = (sk * sk) + vid

    # args - Prepare the arguments for ZoKrates
    args = [str(sk), str(vid), str(commitment)]

    # Print debug info if DEBUG_MODE is enabled
    if DEBUG_MODE:
        print(f"[VtoI_test.zok] sk={sk}, vid={vid}, commitment={commitment}")
        print(f"[VtoI_test.zok] args={args}")

    # verification_result - Run the ZoKrates workflow with the circuit and arguments
    verification_result = run_zokrates_workflow(circuit_path, args)

    # Print verification result if DEBUG_MODE is enabled
    if DEBUG_MODE:
        print(f"[VtoI_test.zok] Verification result: {verification_result}")

    # Print the result of the test based on verification_result, increment passed count if successful
    if verification_result:
        print(f"[PASS] Vehicle-to-Infrastructure ZKP Test passed - sk: {sk}, vid: {vid}")
        passed += 1
    else:
        print(f"[FAIL] Vehicle-to-Infrastructure ZKP Test failed - sk: {sk}, vid: {vid}")

    # Clean up ZoKrates files after the test
    cleanup_zokrates_files()
    
    # Stop the timer for the test
    timer.stop()
    
    # Print elapsed time for the test
    print(timer)
    return verification_result


##
# @brief Test the authentication circuit (auth.zok) for field-based proof
# @details
#   Tests the authentication circuit which uses simple field arithmetic for authentication
#
# Steps:
#   1. Prepare the auth.zok circuit
#   2. Generate random secret and timestamp
#   3. Calculate the OTP
#   4. Run the ZoKrates workflow with the circuit and arguments
#   5. Check if the verification was successful
#   6. Clean up
##
def test_Zokrates_UsingAuthCircuit():
    
    # Print test header
    print("\n=== Zokrates (using auth.zok) Test ===")
    
    # Use global variables to track tests, increment tested count
    global tested, passed
    tested += 1
    
    # Start timer for the test
    timer = Timer("Zokrates (using auth.zok) Test Timer")
    timer.start()
    
    # circuit_path - Set the path to the ZoKrates circuit file
    circuit_path = "zokrates/auth.zok"
    
    # secret - Random secret for authentication
    secret = random.randint(1, 100000)
    
    # timestamp - Current timestamp
    timestamp = int(time.time())
    
    # otp - Calculate the OTP from secret + timestamp
    otp = secret + timestamp

    # args - Prepare the arguments for ZoKrates
    args = [str(secret), str(timestamp), str(otp)]

    # Print debug info if DEBUG_MODE is enabled
    if DEBUG_MODE:
        print(f"[auth.zok] secret={secret}, timestamp={timestamp}, otp={otp}")
        print(f"[auth.zok] args={args}")

    # verification_result - Run the ZoKrates workflow with the circuit and arguments
    verification_result = run_zokrates_workflow(circuit_path, args)

    # Print verification result if DEBUG_MODE is enabled
    if DEBUG_MODE:
        print(f"[auth.zok] Verification result: {verification_result}")

    # Print the result of the test based on verification_result, increment passed count if successful
    if verification_result:
        print(f"[PASS] Authentication Circuit Test passed - secret: {secret}, timestamp: {timestamp}")
        passed += 1
    else:
        print(f"[FAIL] Authentication Circuit Test failed - secret: {secret}, timestamp: {timestamp}")

    # Clean up ZoKrates files after the test
    cleanup_zokrates_files()
    
    # Stop the timer for the test
    timer.stop()
    
    # Print elapsed time for the test
    print(timer)
    return verification_result


##
# @brief Test SUMO with a 10ms step length using straightaway1.sumocfg
# @param print_data If True, print simulation data to screen
# @details
#   Tests SUMO running with a small step length of 10ms for more precise simulation
#
# Steps:
#   1. Start SUMO with straightaway1.sumocfg and --step-length 0.01
#   2. Connect via TraCI
#   3. Retrieve simulation time for several steps to verify the step length
#   4. Print/store the data
#   5. Clean up
##
def test_DataTransfer_SumoAndTraCI_SmallStepLength_UsingStraightaway1Config(print_data=True):
    
    # Print test header
    print("\n=== Data Transfer; Small Step (using straightaway1.sumocfg) Test ===")
    
    # Use global variables to track tests, increment tested count
    global tested, passed
    tested += 1
    
    # Start timer for the test
    timer = Timer("Data Transfer; Small Step (using straightaway1.sumocfg) Test Timer")
    timer.start()

    # port - Define the port for SUMO TraCI connection from settings
    port = SUMO_PORT_SMALL_STEP
    
    # Check if the straightaway1.sumocfg file exists, if not, print error (from check_file_exists) and return
    if not check_file_exists(SUMO_STRAIGHTAWAY1_CONFIG_FILE, "SUMO straightaway1 configuration file"):
        return

    # Start SUMO and connect via TraCI with a step length of 0.01
    proc, traci, _, temp_config, temp_output_dir = start_sumo_simulation(
        file_path=SUMO_STRAIGHTAWAY1_CONFIG_FILE,
        is_config=True,
        port=port,
        sumo_binary="sumo",
        connect_traci=True,
        step_length=0.01,
        sumo_tools_path=SUMO_TOOLS_PATH
    )

    # If proc or traci is None, it means the SUMO process or TraCI connection failed, so return early
    if proc is None or traci is None:
        return
    
    # Try to run the SUMO simulation for 50 steps and verify the step length
    try:
        
        # sim_data - Run the simulation for 50 steps and collect data
        sim_data = run_sumo_simulation_flexible(traci, 50, print_data)
        
        # time_values - Extract the time values from the simulation data
        time_values = [step["time"] for step in sim_data]
        
        # step_lengths - Calculate the step lengths between consecutive time values
        step_lengths = [time_values[i+1] - time_values[i] for i in range(len(time_values)-1)]
        
        # avg_step_length - Calculate the average step length (Probably unneeded but included for completeness in case of shifting step lengths)
        avg_step_length = sum(step_lengths) / len(step_lengths) if step_lengths else 0.0

        # Print the average step length if print_data is True
        if print_data:
            print(f"\nAverage step length: {avg_step_length:.5f} seconds")
        
        # step_length_correct - Check if the average step length is approximately 0.01 seconds (within a small tolerance)
        step_length_correct = abs(avg_step_length - 0.01) < 0.001
        
        # If the step length is correct, set passed_local to True, and print success message if print data is True
        if step_length_correct:
            if print_data:
                print("[SUMO Small Step Test] Step length verified as approximately 0.01 seconds")
            
            # passed_local - Set to True since step length is correct
            passed_local = True
        
        # If step length is incorrect, print failure message and set passed_local to False
        else:
            print(f"[SUMO Small Step Test] Step length verification failed. Expected: 0.01, Got: {avg_step_length:.5f}")
            passed_local = False
        
    # If any exception occurs during the TraCI data transfer, print the error and set passed_local to False
    except Exception as e:
        print(f"[SUMO Small Step Test] Error during test: {e}")
        passed_local = False
    
    # In the finally block, ensure cleanup regardless of success or failure
    finally:
        
        # Cleanup SUMO and TraCI processes
        cleanup_sumo_and_traci(proc, port, traci)
        
        # Clean up temp config/output if created
        if temp_config and os.path.exists(temp_config):
            
            # Attempt to remove the temporary config file with os.unlink
            try:
                os.unlink(temp_config)
            
            # If unlink fails do nothing, just pass
            except:
                pass
        
        # Clean up temp output directory if created
        if temp_output_dir and os.path.exists(temp_output_dir):
            
            # Attempt to remove the temporary output directory with shutil.rmtree
            try:
                shutil.rmtree(temp_output_dir)
            
            # If rmtree fails do nothing, just pass
            except:
                pass

    # Print the result of the test based on passed_local and increment passed count if successful
    if passed_local:
        passed += 1
        print("[SUMO Small Step Test] Small step length test succeeded!\n")
    else:
        print("[SUMO Small Step Test] Small step length test failed.\n")
    
    # Stop the timer for the test
    timer.stop()
    
    # Kill any processes still running on the specified port
    kill_processes_on_port(port)
    
    # Print elapsed time for the test
    print(timer)


##
# @brief Test dynamic car spawning in SUMO using straightaway5.sumocfg
# @param print_data If True, print simulation data to screen
# @details
#   Connects to SUMO with straightaway5.sumocfg, spawns a car at step 10, and whenever a car completes its route,
#   immediately spawns another identical car, for 1010 steps.
#
# Steps:
#   1. Start SUMO with straightaway5.sumocfg
#   2. Connect via TraCI
#   3. Spawn a car at step 10
#   4. When a car finishes its route, spawn another identical car
#   5. Print vehicle positions and simulation data if print_data is True
#   6. Clean up after simulation
##
def test_LiveManipulation_SumoAndTraCI_SpawnCarsDynamically_UsingStraightaway5(print_data=True):
    
    # Print test header
    print("\n=== SUMO Dynamic Car Spawning (straightaway5.sumocfg) Test ===")
    
    # Use global variables to track tests, increment tested count
    global tested, passed
    tested += 1

    # Start timer for the test
    timer = Timer("SUMO Dynamic Car Spawning (straightaway5.sumocfg) Test Timer")
    timer.start()

    # sumo_cfg - Path to the SUMO configuration file for straightaway5
    sumo_cfg = os.path.join(
        os.path.dirname(__file__),
        "..", "..", "SUMO", "Built Sims", "StraightAway5", "straightaway5.sumocfg"
    )
    sumo_cfg = os.path.abspath(sumo_cfg)
    
    # port - Define the port for SUMO TraCI connection from settings
    port = SUMO_PORT_DYNAMIC_SPAWN

    # Check config file exists, if not, print error (from check_file_exists) and return
    if not check_file_exists(sumo_cfg, "SUMO straightaway5 configuration file"):
        return

    # Start SUMO and connect via TraCI
    proc, traci, _, temp_config, temp_output_dir = start_sumo_simulation(
        file_path=sumo_cfg,
        is_config=True,
        port=port,
        sumo_binary="sumo",
        connect_traci=True,
        sumo_tools_path=SUMO_TOOLS_PATH
    )

    # If proc or traci is None, it means the SUMO process or TraCI connection failed, so return early
    if proc is None or traci is None:
        return

    # Try to run the SUMO simulation and spawn cars dynamically
    try:
        
        # total_steps - Total number of simulation steps to run
        total_steps = 1010
        
        # car_counter - Counter for spawned cars
        car_counter = 0
        
        # active_cars - Dictionary to track active cars and their spawn step
        active_cars = {}
        
        # car_type - Type of car to spawn
        car_type = "car"
        
        # car_route - Route ID for the cars
        car_route = "route1"
        
        # finished_cars - Counter for finished cars
        finished_cars = 0

        # Main simulation loop
        for step in range(total_steps):
            
            # Check if we have reached the maximum number of steps, if so, print summary and break
            if step >= total_steps - 1:
                print(f"\nReached max steps ({total_steps}). Ending simulation.")
                print(f"Total cars finished: {finished_cars}")
                break
            
            # Run a simulation step
            traci.simulationStep()
            
            # sim_time - Get the current simulation time
            sim_time = traci.simulation.getTime()

            # Iterate over active cars to check if they have finished
            for car_id in list(active_cars.keys()):
                
                # Check if the car is still in the simulation, if not, increment finished_cars
                if car_id not in traci.vehicle.getIDList():
                    finished_cars += 1
                    
                    # If print_data is True, print the finished car ID and step
                    if print_data:
                        print(f"{car_id} finished at step {step}")
                        
                    # Remove the car from active_cars
                    del active_cars[car_id]

            # If there are no active cars and we are past step 10, spawn a new car
            if not active_cars and step >= 10:
                
                # Increment car_counter
                car_counter += 1
                
                # new_car_id - Generate a new car ID based on the counter
                new_car_id = f"car{car_counter}"
                
                # Add a new car to the simulation
                traci.vehicle.add(
                    vehID=new_car_id,
                    routeID=car_route,
                    typeID=car_type,
                    depart=sim_time
                )
                
                # active_cars - Add the new car to active_cars with the current step
                active_cars[new_car_id] = step
                
                # If print_data is True, print the spawned car ID and step
                if print_data:
                    print(f"Spawned {new_car_id} at step {step}")

            # If print_data is True, print vehicle positions and IDs
            if print_data:
                
                # veh_ids - Get the list of vehicle IDs currently in the simulation
                veh_ids = traci.vehicle.getIDList()
                
                # Print the current step and vehicle IDs
                print(f"Step {step}: Vehicles in sim: {veh_ids}")
                
                # Iterate over the car IDs in veh_ids and print their positions
                for car_id in veh_ids:
                    
                    # Try to get the position of the car
                    try:
                        
                        # pos - Get the position of the car
                        pos = traci.vehicle.getPosition(car_id)
                        
                        # Print the position of the car
                        print(f"Step {step}: {car_id} position: {pos}")
                    
                    # If any exception occurs while getting the position, print the error
                    except Exception as e:
                        print(f"Step {step}: Could not get position for {car_id}: {e}")

            # If print_data is True, print the active and finished cars every 100 steps
            if print_data and step % 100 == 0:
                print(f"Step {step}: Active cars: {list(active_cars.keys())}, Finished cars: {finished_cars}")

        # passed_local - Set to True since the simulation ran successfully
        passed_local = True

    # If any exception occurs during the simulation, print the error and set passed_local to False
    except Exception as e:
        print(f"[SUMO Dynamic Car Spawning Test] Error: {e}")
        passed_local = False

    # In the finally block, ensure cleanup regardless of success or failure
    finally:
        
        # Clean up SUMO and TraCI connections and temporary files
        cleanup_sumo_and_traci(proc, port, traci)
        
        # Clean up temp config/output if created
        if temp_config and os.path.exists(temp_config):
            
            # Attempt to remove the temporary config file with os.unlink
            try:
                os.unlink(temp_config)
            
            # If unlink fails do nothing, just pass
            except:
                pass
            
        # Clean up temp output directory if created
        if temp_output_dir and os.path.exists(temp_output_dir):
            
            # Attempt to remove the temporary output directory with shutil.rmtree
            try:
                shutil.rmtree(temp_output_dir)
            
            # If rmtree fails do nothing, just pass
            except:
                pass

    # Print test result
    if passed_local:
        passed += 1
        print("[SUMO Dynamic Car Spawning Test] Test succeeded!\n")
    else:
        print("[SUMO Dynamic Car Spawning Test] Test failed.\n")

    # Stop the timer for the test
    timer.stop()
    
    # Kill any processes still running on the specified port
    kill_processes_on_port(port)
    
    # Print elapsed time for the test
    print(timer)


##
# @brief Test RSU message delay and car stopping in SUMO using straightaway6.sumocfg
# @param print_data If True, print simulation data to screen
# @details
#   Connects to SUMO with straightaway6.sumocfg, spawns a car at step 1000, and whenever a car completes its route,
#   immediately spawns another identical car, for 51000 steps. Cars are stopped for 2 seconds when near RSU.
#
# Steps:
#   1. Start SUMO with straightaway6.sumocfg
#   2. Connect via TraCI
#   3. Spawn a car at step 1000
#   4. When a car approaches RSU, stop it for 2 seconds, then resume
#   5. Print vehicle positions and simulation data if print_data is True
#   6. Clean up after simulation
##
def test_LiveManipulation_SumoAndTraCI_RsuMessageWithDelay_UsingStraightaway6(print_data=True):
    
    # Print test header
    print("\n=== Live Manipulation - Rsu Message With Delay; (using straightaway6.sumocfg) Test ===")
    
    # Use global variables to track tests, increment tested count
    global tested, passed
    tested += 1
    
    ## @var flags_raised Number of times a car was stopped by RSU
    # @brief Used to track how many times cars were stopped by RSU
    flags_raised = 0
    
    # flags_lowered = 0

    # Start the timer for this test
    timer = Timer("Live Manipulation - Rsu Message With Delay; (using straightaway6.sumocfg) Test Timer")
    timer.start()

    # Build and use the correct config file path and port
    sumo_cfg = os.path.join(
        os.path.dirname(__file__),
        "..", "..", "SUMO", "Built Sims", "StraightAway6", "straightaway6.sumocfg"
    )
    sumo_cfg = os.path.abspath(sumo_cfg)
    port = SUMO_PORT_RSUWITHDELAY

    # Check config file exists, return if not
    if not check_file_exists(sumo_cfg, "SUMO straightaway5 configuration file"):
        return

    # Start SUMO and connect via TraCI using the unified function
    proc, traci, _, temp_config, temp_output_dir = start_sumo_simulation(
        file_path=sumo_cfg,
        is_config=True,
        port=port,
        sumo_binary="sumo",
        connect_traci=True,
        step_length=0.01,
        sumo_tools_path=SUMO_TOOLS_PATH
    )

    # If SUMO or TraCI failed to start, exit early
    if proc is None or traci is None:
        return

    # Initialize variables for the simulation
    try:
        total_steps = 51000
        car_counter = 0
        active_cars = {}
        car_type = "car"
        car_route = "route1"
        finished_cars = 0
        
        # Used to track which cars have triggered the stop flag
        cars_that_triggered_stop = set()
        
        # Used to track cars that are currently stopped and when they should resume
        # car_id -> step to resume at
        stopped_cars = {}

        # Main simulation loop
        for step in range(total_steps):
            
            ## Handle cars that need to resume after stop
            # Iterate through stopped cars and check if they can resume
            for car_id in list(stopped_cars.keys()):
                
                # Check if it's time to resume this car
                if step >= stopped_cars[car_id]:

                    # Try to resume the car
                    try:
                        
                        # Check if the car is still in the simulation
                        if car_id in traci.vehicle.getIDList():
                            
                            # Resume the car's speed
                            traci.vehicle.setSpeed(car_id, -1)
                            
                            # If print_data is True, print the resuming action
                            if print_data:
                                print(f"*** RESUMING: Car {car_id} is resuming normal speed at step {step} ***")
                    
                    # If any error occurs while resuming, print the error
                    except Exception as e:
                        print(f"Could not resume car {car_id}: {e}")
                    
                    # Remove from stopped cars dict
                    del stopped_cars[car_id]
            
            ## RSU-car interaction logic
            # Initialize lists to hold RSU and car IDs
            rsu_ids = []
            car_ids = []
            
            # Try to get RSU and car IDs from the simulation
            try:
                
                # Get RSU and car IDs from simulation
                rsu_ids = [vid for vid in traci.vehicle.getIDList() if traci.vehicle.getTypeID(vid) == "rsu"]
                car_ids = [vid for vid in traci.vehicle.getIDList() if traci.vehicle.getTypeID(vid) == "car" and vid not in cars_that_triggered_stop]
                
                # Iterate over each car and check distance to RSU
                for car_id in car_ids:
                    
                    # Skip cars that are currently stopped
                    if car_id in stopped_cars:
                        continue
                    
                    # Skip if no RSUs
                    if not rsu_ids:
                        continue
                    
                    # Get the position of the first RSU and the car
                    rsu_pos = traci.vehicle.getPosition(rsu_ids[0])
                    car_pos = traci.vehicle.getPosition(car_id)
                    
                    # Calculate distance between car and RSU with Euclidean distance formula (sqrt((x2 - x1)^2 + (y2 - y1)^2))
                    dx = rsu_pos[0] - car_pos[0]
                    dy = rsu_pos[1] - car_pos[1]
                    dist = (dx**2 + dy**2) ** 0.5
                    
                    # Check if car is within threshold distance
                    if dist < 125:
                        
                        # Try to stop the car for 2 seconds (200 steps at 0.01s per step)
                        try:
                            
                            # Get current speed for debug info
                            current_speed = traci.vehicle.getSpeed(car_id)
                            
                            # Stop the car
                            traci.vehicle.setSpeed(car_id, 0)
                            

                            # Calculate resume step (2 seconds later)
                            resume_step = step + 200
                            stopped_cars[car_id] = resume_step
                            
                            # Mark this car as having triggered a stop
                            cars_that_triggered_stop.add(car_id)
                            
                            # Increment flag count
                            flags_raised += 1
                            
                            # Debug output
                            print(f"*** STOPPING: Car {car_id} at step {step} (distance: {dist:.2f} m, speed: {current_speed:.2f} m/s) ***")
                            print(f"*** Will resume at step {resume_step} ***")
                        
                        # If any error occurs while stopping the car, print the error
                        except Exception as e:
                            print(f"Could not stop car {car_id}: {e}")
            
            # If any error occurs while getting RSU-car interactions, print the error on a step divisible by 1000
            except Exception as e:
                if step % 1000 == 0:
                    print(f"Step {step}: Could not compute RSU-car interactions: {e}")

            # Exit if total_steps is reached
            if step >= total_steps - 1:
                
                # Print final summary before exiting
                print(f"\nReached max steps ({total_steps}). Ending simulation.")
                print(f"Total cars finished: {finished_cars}")
                print(f"Flags raised (cars stopped): {flags_raised}")
                print(f"Cars that triggered stop: {len(cars_that_triggered_stop)}")
                break
            
            # Run the simulation step and get the current simulation time
            traci.simulationStep()
            sim_time = traci.simulation.getTime()

            # Check for cars that have finished their routes, remove them from active_cars, and increment finished_cars
            for car_id in list(active_cars.keys()):
                
                if car_id not in traci.vehicle.getIDList():
                    finished_cars += 1
                    
                    if print_data:
                        print(f"{car_id} finished at step {step}")
                        
                    del active_cars[car_id]

            # Spawn a new car if no active cars are present and we're at or past step 1000, increment car_counter, and set new car ID
            if not active_cars and step >= 1000:
                car_counter += 1
                new_car_id = f"car{car_counter}"
                
                # Add a new car to the simulation
                traci.vehicle.add(
                    vehID=new_car_id,
                    routeID=car_route,
                    typeID=car_type,
                    depart=sim_time
                )
                
                # Add the new car to active_cars
                active_cars[new_car_id] = step
                
                # If print_data is True, print the spawning action
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
                    
                    # Try to get the position of each car
                    try:
                        pos = traci.vehicle.getPosition(car_id)
                        print(f"Step {step}: {car_id} position: {pos}")
                        
                    # If any error occurs while getting position, print the error
                    except Exception as e:
                        print(f"Step {step}: Could not get position for {car_id}: {e}")
                        
        # If we reach here, the simulation completed without errors, so we passed_local to True
        passed_local = True

    # If any exception occurs during the simulation process print it and set passed_local to False
    except Exception as e:
        print(f"[Live Manipulation - Rsu Message With Delay] Error: {e}")
        passed_local = False

    # Use finally and the utility function to clean up SUMO and TraCI connections and temporary files regardless of success or failure
    finally:
        
        # Clean up SUMO and TraCI connections and temporary files
        cleanup_sumo_and_traci(proc, port, traci)
        
        # If temp_config and temp_output_dir were created, remove them
        if temp_config and os.path.exists(temp_config):
            
            # Attempt to remove the temporary config file
            try: 
                os.unlink(temp_config)
            except: pass
            
        if temp_output_dir and os.path.exists(temp_output_dir):
            
            # Attempt to remove the temporary output directory
            try: 
                shutil.rmtree(temp_output_dir)
            except: pass

    # Print test result and increment passed count if the test was successful
    if passed_local:
        passed += 1
        print("[Live Manipulation - Rsu Message With Delay] Test succeeded!\n")
    else:
        print("[Live Manipulation - Rsu Message With Delay] Test failed.\n")

    timer.stop()
    
    kill_processes_on_port(port)
    
    print(timer)


##
# @brief Runs all tests and scenarios for the ZKP-OTP authentication protocol and related modules
# @details
#   Executes all test routines in sequence, including simulated and real ZKP workflows,
#   blockchain verification, SUMO connection/data transfer, and vehicle manipulation scenarios.
#
# Steps:
#   1. Initialize test counters and timer
#   2. Run each test function in sequence, with brief pauses between tests
#   3. Perform SUMO cleanup after connection tests
#   4. Print summary of total tests run, passed, and failed
##
def testAndScenarioRunner():
    
    # Use global variables to track tests, initialize counts
    global tested, passed
    tested, passed = 0, 0
    
    # Start timer for the entire test suite
    timer = Timer("Test and Scenario Runner Timer")
    timer.start()

    # Define list of all test functions and their print_data parameter if needed
    test_functions = [
        (test_VehicleRsuBasicInteraction_SimulatedZkp, None),
        (test_VehicleRsuBasicInteraction_SimulatedZkpAndBlockchain, None),
        (test_EndToEnd_SimulatedZkpAndBlockchain_Success, None),
        (test_EndToEnd_SimulatedZkpAndBlockchain_Failure, None),
        (test_PartialWorkflow_RealZokrates_UsingDummyCircuit, None),
        (test_PartialWorkflow_MultipleVehicles_Simulated, None),
        (test_EndToEnd_MultipleVehicles_Simulated, None),
        (test_PartialWorkflow_RealZokrates_MultipleVehicles_UsingDummyCircuit, None),
        (test_PartialWorkflow_RealZokratesSimulatedBlockchain_MultipleVehicles_UsingDummyCircuit, None),
        (lambda: test_sumo_connection_wrapper(tested, passed), None),
        (test_Zokrates_BasicConnectionTest_UsingDummyCircuit, None),
        (test_DataTransfer_SumoAndTraCI_UsingSimpleNet, True),
        (test_DataTransfer_SumoAndTraCI_UsingIntersection1Config, True),
        (test_DataTransfer_SumoAndTraCI_UsingIntersection2Config, True),
        (test_DataTransfer_SumoAndTraCI_UsingStraightaway1Config, True),
        (test_DataTransfer_SumoAndTraCI_UsingStraightaway2Config, True),
        (test_LiveManipulation_SumoAndTraCI_UsingStraightaway1Config, True),
        (test_Zokrates_UsingVtoICircuit, None),
        (test_Zokrates_UsingAuthCircuit, None),
        (test_DataTransfer_SumoAndTraCI_SmallStepLength_UsingStraightaway1Config, True),
        (test_LiveManipulation_SumoAndTraCI_SpawnCarsDynamically_UsingStraightaway5, True),
        (test_LiveManipulation_SumoAndTraCI_RsuMessageWithDelay_UsingStraightaway6, True)
    ]

    # Run each test function in sequence with print_data if specified and pause between tests
    for test_func, print_data in test_functions:
        if print_data is not None:
            test_func(print_data)
        else:
            test_func()
        time.sleep(.5)
        # clear_console()   # Uncomment if you want to clear the console after each test
    
    # SUMO/TraCI cleanup after tests
    cleanup_traci_connection()

    # Clean up all ports
    for port in PORTS_TO_CLEANUP:
        kill_processes_on_port(port)
    
    time.sleep(2)

    # Stop timer and print elapsed time for the test suite
    timer.stop()
    print(f"\nAll tests completed in {timer.elapsed():.8f} seconds.\n")
    
    # Print summary of test results
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

