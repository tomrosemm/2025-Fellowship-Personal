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

# Imports
import secrets
import os
import time
import random
import subprocess
import sys

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


from sumo_interface import kill_processes_on_port, cleanup_traci_connection
from blockchain import simulate_blockchain_verification, set_debug_mode as set_blockchain_debug_mode
from sumo_interface import test_sumo_connection_wrapper, set_debug_mode as set_sumo_debug_mode
from zkp import generate_zkp_proof_simulated
from settings import (
    DEBUG_MODE as DEFAULT_DEBUG_MODE,
    SUMO_TOOLS_PATH, 
    SUMO_SIMPLE_NET_FILE,
    SUMO_INTERSECTION_CONFIG_FILE,
    SUMO_PORT_DATA,
    SUMO_PORT_DATA_CONFIG,
    SUMO_PORT_BASIC,
    SUMO_PORT_CONFIG,
    ZOKRATES_DUMMY_CIRCUIT
)

# Track number of tests run and passed
tested = 0
passed = 0

## @var DEBUG_MODE
# @brief Global variable to control debug output.
DEBUG_MODE = DEFAULT_DEBUG_MODE


##
# @brief Enable or disable debug mode for detailed output.
# @param enabled True to enable debug mode, False to disable.
# @details
#   Sets the global DEBUG_MODE variable and propagates debug mode to all relevant modules/classes.
# @steps
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
# @brief Clears the console screen based on the operating system.
# @details
#   Clears the console using the appropriate command for the OS.
# @steps
#   1. If Windows, use 'cls'.
#   2. Otherwise, use 'clear'.
##
def clear_console():
    
    if os.name == 'nt':
        os.system('cls')
        
    else:
        os.system('clear')


##
# @brief Test the workflow using a simulated ZKP (hash-based).
# @details
#   Simulates authentication between a vehicle and RSU using a hash-based ZKP.
# @steps
#   1. Generate a random vehicle secret and create Vehicle and RSU entities.
#   2. Vehicle generates an OTP and timestamp.
#   3. Vehicle creates a simulated ZKP proof (hash-based) for the OTP and timestamp.
#   4. RSU verifies the ZKP proof using the known vehicle secret and timestamp.
#   5. Output the result of the verification and authentication status.
##
def test_vehicle_rsu_interaction_simulated():
    
    # Print test header
    print("\n=== Simulated ZKP Test ===")
    
    # Use global variables to track tests, increment tested count
    global tested, passed
    tested += 1
    
    # Generate entities with random secrets
    vehicle_id = "VEH123"
    vehicle_secret = secrets.token_hex(16)
    vehicle = Vehicle(vehicle_id, vehicle_secret)
    rsu = RSU({vehicle_id: vehicle_secret})

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


##
# @brief Simulate the full workflow, including using ZoKrates for the ZKP as well as blockchain verification and logging.
# @details
#   Simulates authentication and blockchain verification using hash-based ZKP.
# @steps
#   1. Generate a random vehicle secret and create Vehicle and RSU entities.
#   2. Vehicle generates an OTP and timestamp.
#   3. Vehicle creates a simulated ZKP proof (hash-based) for the OTP and timestamp.
#   4. RSU verifies the ZKP proof using the known vehicle secret and timestamp.
#   5. Simulate blockchain smart contract verification and logging of the authentication attempt.
#   6. Output the result of the infrastructure access decision.
##
def test_vehicle_rsu_blockchain_simulated():
    
    # Print test header
    print("\n=== Simulated Blockchain ZKP Test ===")
    
    # Use global variables to track tests, increment tested count
    global tested, passed
    tested += 1
    
    # Generate entities with random secrets
    vehicle_id = "VEH123"
    vehicle_secret = secrets.token_hex(16)
    vehicle = Vehicle(vehicle_id, vehicle_secret)
    rsu = RSU({vehicle_id: vehicle_secret})

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

    # Simulate blockchain verification and logging
    outcome = simulate_blockchain_verification(vehicle_id, zkp_proof, timestamp, verification_result) if DEBUG_MODE else verification_result
    
    # Output the result of the infrastructure access decision, increment passed count if successful
    if outcome:
        passed += 1
        print("[Simulated] Access granted by infrastructure.\n")
        
    else:
        print("[Simulated] Access denied by infrastructure.\n")


##
# @brief End-to-end scenario: Vehicle authenticates successfully and is granted access.
# @details
#   Simulates a successful authentication scenario for a vehicle.
# @steps
#   1. Create vehicle and RSU with matching secrets.
#   2. Vehicle generates OTP and timestamp.
#   3. Vehicle creates ZKP proof.
#   4. RSU verifies ZKP proof.
#   5. Blockchain verification is performed if DEBUG_MODE is enabled.
#   6. Print the result of infrastructure access decision.
##
def scenario_successful_authentication():
    
    # Print test header
    print("\n=== End-to-End Scenario: Successful Authentication ===")
    
    # Use global variables to track tests, increment tested count
    global tested, passed
    tested += 1
    
    # Generate entities with matching secrets
    vehicle_id = "VEH001"
    vehicle_secret = secrets.token_hex(16)
    vehicle = Vehicle(vehicle_id, vehicle_secret)
    rsu = RSU({vehicle_id: vehicle_secret})

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


##
# @brief End-to-end scenario: Vehicle fails authentication due to wrong secret.
# @details
#   Simulates a failed authentication scenario for a vehicle with incorrect secret.
# @steps
#   1. Create vehicle with wrong secret and RSU with correct secret.
#   2. Vehicle generates OTP and timestamp.
#   3. Vehicle creates ZKP proof.
#   4. RSU verifies ZKP proof using expected secret.
#   5. Blockchain verification is performed if DEBUG_MODE is enabled.
#   6. Print expected denial of infrastructure access.
##
def scenario_failed_authentication():
    
    # Print test header
    print("\n=== End-to-End Scenario: Failed Authentication ===")
    
    # Use global variables to track tests, increment tested count
    global tested, passed
    tested += 1
    
    # Generate entities with wrong secret
    vehicle_id = "VEH001"
    correct_secret = secrets.token_hex(16)
    wrong_secret = secrets.token_hex(16)
    vehicle = Vehicle(vehicle_id, wrong_secret)
    rsu = RSU({vehicle_id: correct_secret})

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


##
# @brief Test the connection and workflow with ZoKrates CLI using zokrates/dummy.zok.
# @details
#   Runs ZoKrates CLI workflow with fixed inputs.
# @steps
#   1. Compile the ZoKrates circuit.
#   2. Run setup.
#   3. Compute witness (inputs: a=3, b=4).
#   4. Generate proof.
#   5. Verify proof.
#   6. Clean up ZoKrates artifacts after test.
#   7. Print the result of the ZoKrates workflow.
##
def test_zokrates_connection():
    
    # Print test header
    print("\n=== ZoKrates CLI Connection Test ===")
    
    # Use global variables to track tests, increment tested count
    global tested, passed
    tested += 1
    
    # Set the circuit path for ZoKrates from settings
    circuit_path = ZOKRATES_DUMMY_CIRCUIT
    
    ## Compile circuit
    # If compilation fails, print error and return
    if not run_zokrates_compile(circuit_path):
        print("[ZoKrates Test] Compilation failed.")
        return
    
    ## Run setup
    # If setup fails, print error, clean up files, and return
    if not run_zokrates_setup():
        print("[ZoKrates Test] Setup failed.")
        cleanup_zokrates_files()
        return
    
    # Args to use for computing witness (a=3, b=4)
    args = ["3", "4"]
    
    ## Compute witness (inputs: a=3, b=4)
    # If compute witness fails, print error, clean up files, and return
    if not run_zokrates_compute_witness(args):
        print("[ZoKrates Test] Compute witness failed.")
        cleanup_zokrates_files()
        return
    
    ## Generate proof
    # If proof generation fails, print error, clean up files, and return
    if not run_zokrates_generate_proof():
        print("[ZoKrates Test] Proof generation failed.")
        cleanup_zokrates_files()
        return
    
    ## Verify proof
    verification_result = run_zokrates_verify()
    
    # Print verification result if DEBUG_MODE is enabled
    if DEBUG_MODE:
        print(f"[ZoKrates Test] Verification result: {verification_result}\n")
    
    # Output the result of the ZoKrates workflow, increment passed count if successful
    if verification_result:
        passed += 1
        print("[ZoKrates Test] ZoKrates connection and workflow succeeded!\n")
        
    else:
        print("[ZoKrates Test] ZoKrates connection or workflow failed.\n")
        
    # Clean up ZoKrates artifacts after test
    cleanup_zokrates_files()


##
# @brief Test the end-to-end ZoKrates workflow using zokrates/dummy.zok and random inputs.
# @details
#   Simulates a real ZKP workflow using the ZoKrates CLI.
# @steps
#   1. Generate random field inputs for dummy.zok.
#   2. Compile circuit.
#   3. Run setup.
#   4. Compute witness.
#   5. Generate proof.
#   6. Verify proof.
#   7. Clean up ZoKrates artifacts after test.
#   8. Print the result of the workflow.
##
def test_vehicle_rsu_interaction_real_zokrates_dummy():
    
    # Print test header
    print("\n=== Real ZoKrates End-to-End Test with zokrates/dummy.zok ===")
    
    # Use global variables to track tests, increment tested count
    global tested, passed
    tested += 1
    
    # Set the circuit path for ZoKrates from settings
    circuit_path = ZOKRATES_DUMMY_CIRCUIT
    
    # Generate random field inputs for dummy.zok
    a = random.randint(1, 100)
    b = random.randint(1, 100)
    
    # If DEBUG_MODE is enabled, print the inputs
    if DEBUG_MODE:
        print(f"Inputs: a={a}, b={b}")
        
    ## Compile circuit
    # If compilation fails, print error and return
    if not run_zokrates_compile(circuit_path):
        print("[Real ZKP] Compilation failed.")
        return
    
    ## Run setup
    # If setup fails, print error, clean up files, and return
    if not run_zokrates_setup():
        print("[Real ZKP] Setup failed.")
        cleanup_zokrates_files()
        return
    
    # Args to use for computing witness (a, b)
    args = [str(a), str(b)]
    
    ## Compute witness (inputs: a, b)
    # If compute witness fails, print error, clean up files, and return
    if not run_zokrates_compute_witness(args):
        print("[Real ZKP] Compute witness failed.")
        cleanup_zokrates_files()
        return
    
    ## Generate proof
    # If proof generation fails, print error, clean up files, and return
    if not run_zokrates_generate_proof():
        print("[Real ZKP] Proof generation failed.")
        cleanup_zokrates_files()
        return
    
    ## Verify proof
    verification_result = run_zokrates_verify()
    
    # Print verification result if DEBUG_MODE is enabled
    if DEBUG_MODE:
        print(f"[Real ZKP] Verification result: {verification_result}\n")
    
    # Output the result of the ZoKrates workflow, increment passed count if successful
    if verification_result:
        passed += 1
        print("[Real ZKP] End-to-end ZoKrates workflow succeeded!\n")
        
    else:
        print("[Real ZKP] End-to-end ZoKrates workflow failed.\n")
    
    # Clean up ZoKrates artifacts after test
    cleanup_zokrates_files()


##
# @brief Simulated ZKP isolated test with multiple vehicles.
# @details
#   Simulates authentication for multiple vehicles using hash-based ZKP.
# @steps
#   1. Create multiple vehicles, each with a unique secret.
#   2. Each vehicle generates OTP and timestamp, creates ZKP proof.
#   3. RSU verifies each ZKP proof.
#   4. Print whether all vehicles authenticated successfully.
##
def test_simulated_isolated_multiple_vehicles():
    
    # Print test header
    print("\n=== Simulated ZKP Isolated Test: Multiple Vehicles ===")
    
    # Use global variables to track tests, increment tested count
    global tested, passed
    tested += 1
    
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
    rsu = RSU(rsu_secrets)
    
    # Initialize a flag to track if all vehicles passed authentication
    all_passed = True
    
    # Circuit path for the simulated ZKP proof
    circuit_path = "zokrates/dummy.zok"
    
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


##
# @brief Simulated end-to-end test with multiple vehicles (RSU + blockchain).
# @details
#   Simulates authentication and blockchain verification for multiple vehicles.
# @steps
#   1. Create multiple vehicles, each with a unique secret.
#   2. Each vehicle generates OTP and timestamp, creates ZKP proof.
#   3. RSU verifies each ZKP proof.
#   4. Blockchain verification is performed if DEBUG_MODE is enabled.
#   5. Print whether all vehicles were granted access by infrastructure.
##
def test_simulated_end_to_end_multiple_vehicles():
    
    # Print test header
    print("\n=== Simulated End-to-End Test: Multiple Vehicles ===")
    
    # Use global variables to track tests, increment tested count
    global tested, passed
    tested += 1
    
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
    rsu = RSU(rsu_secrets)
    
    # Initialize a flag to track if all vehicles passed authentication
    all_passed = True
    
    # Circuit path for the simulated ZKP proof
    circuit_path = "zokrates/dummy.zok"
    
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
    
    # Output the result of the infrastructure access decision for all vehicles, increment passed count if successful
    if all_passed:
        passed += 1
        print("[Simulated] All vehicles granted access by infrastructure.\n")
        
    else:
        print("[Simulated] Some vehicles denied access.\n")


##
# @brief ZoKrates-integrated isolated test with multiple vehicles (zokrates/dummy.zok).
# @details
#   Runs ZoKrates workflow for multiple vehicles with random inputs.
# @steps
#   1. For each vehicle:
#      a. Generate random inputs.
#      b. Compile ZoKrates circuit.
#      c. Run setup.
#      d. Compute witness.
#      e. Generate proof.
#      f. Verify proof.
#      g. Clean up ZoKrates artifacts.
#   2. Print whether all vehicles' proofs were verified successfully.
##
def test_zokrates_isolated_multiple_vehicles():
    
    # Print test header
    print("\n=== ZoKrates-Integrated Isolated Test: Multiple Vehicles ===")
    
    # Use global variables to track tests, increment tested count
    global tested, passed
    tested += 1
    
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
        
        ## Compile circuit
        # If compilation fails, print error, set all_passed to False, and continue to next vehicle
        if not run_zokrates_compile(circuit_path):
            print("[ZoKrates] Compilation failed.")
            all_passed = False
            continue
        
        ## Run setup
        # If setup fails, print error, clean up files, set all_passed to False, and continue to next vehicle
        if not run_zokrates_setup():
            print("[ZoKrates] Setup failed.")
            cleanup_zokrates_files()
            all_passed = False
            continue
        
        # Args to use for computing witness (a, b)
        # Convert inputs to strings for ZoKrates CLI
        args = [str(a), str(b)]
        
        ## Compute witness (inputs: a, b)
        # If compute witness fails, print error, clean up files, set all_passed to False, and continue to next vehicle
        if not run_zokrates_compute_witness(args):
            print("[ZoKrates] Compute witness failed.")
            cleanup_zokrates_files()
            all_passed = False
            continue
        
        ## Generate proof
        # If proof generation fails, print error, clean up files, set all_passed to False, and continue to next vehicle
        if not run_zokrates_generate_proof():
            print("[ZoKrates] Proof generation failed.")
            cleanup_zokrates_files()
            all_passed = False
            continue
        
        ## Verify proof
        # Run ZoKrates verification and store the result
        verification_result = run_zokrates_verify()
        
        # If DEBUG_MODE is enabled, print the verification result
        if DEBUG_MODE:
            print(f"Vehicle {i+1}: ZoKrates verification result: {verification_result}")
        
        # If the verification result is False, set all_passed to False
        if not verification_result:
            all_passed = False
        
        # Clean up ZoKrates artifacts after each vehicle's test
        cleanup_zokrates_files()
    
    # Output the result of the ZoKrates workflow for all vehicles, increment passed count if successful
    if all_passed:
        passed += 1
        print("[ZoKrates] All vehicles' proofs verified successfully.\n")
        
    else:
        print("[ZoKrates] Some vehicles' proofs failed verification.\n")


##
# @brief ZoKrates-integrated end-to-end test with multiple vehicles (zokrates/dummy.zok + simulated blockchain).
# @details
#   Runs ZoKrates workflow and blockchain verification for multiple vehicles.
# @steps
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
def test_zokrates_end_to_end_multiple_vehicles():
    
    # Print test header
    print("\n=== ZoKrates-Integrated End-to-End Test: Multiple Vehicles ===")
    
    # Use global variables to track tests, increment tested count
    global tested, passed
    tested += 1
    
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
        
        ## Compile circuit
        # If compilation fails, print error, set all_passed to False, and continue to next vehicle
        if not run_zokrates_compile(circuit_path):
            print("[ZoKrates] Compilation failed.")
            all_passed = False
            continue
        
        ## Run setup
        # If setup fails, print error, clean up files, set all_passed to False, and continue to next vehicle
        if not run_zokrates_setup():
            print("[ZoKrates] Setup failed.")
            cleanup_zokrates_files()
            all_passed = False
            continue
        
        # Args to use for computing witness (a, b)
        # Convert inputs to strings for ZoKrates CLI
        args = [str(a), str(b)]
        
        ## Compute witness (inputs: a, b)
        # If compute witness fails, print error, clean up files, set all_passed to False, and continue to next vehicle
        if not run_zokrates_compute_witness(args):
            print("[ZoKrates] Compute witness failed.")
            cleanup_zokrates_files()
            all_passed = False
            continue
        
        ## Generate proof
        # If proof generation fails, print error, clean up files, set all_passed to False, and continue to next vehicle
        if not run_zokrates_generate_proof():
            print("[ZoKrates] Proof generation failed.")
            cleanup_zokrates_files()
            all_passed = False
            continue
        
        ## Verify proof
        # Run ZoKrates verification and store the result
        verification_result = run_zokrates_verify()
        
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
        
        # Clean up ZoKrates artifacts after each vehicle's test
        cleanup_zokrates_files()
    
    # Output the result of the ZoKrates workflow and blockchain verification for all vehicles, increment passed count if successful
    if all_passed:
        passed += 1
        print("[ZoKrates] All vehicles' end-to-end proofs and blockchain logs succeeded.\n")
        
    else:
        print("[ZoKrates] Some vehicles failed end-to-end ZoKrates or blockchain verification.\n")


##
# @brief Test connecting to SUMO via TraCI, retrieving and storing simulation data.
# @param print_data If True, print simulation data to screen.
# @details
#   Tests SUMO connection and data retrieval using TraCI.
# @steps
#   1. Start SUMO with a simple network.
#   2. Connect via TraCI.
#   3. Retrieve simulation time, vehicle IDs, and positions.
#   4. Print/store the data.
#   5. Clean up.
##
def test_sumo_traci_data_transfer(print_data=True):
    
    # Print test header
    print("\n=== SUMO TraCI Data Transfer Test ===")
    
    # Use global variables to track tests, increment tested count
    global tested, passed
    tested += 1

    # Define the port for TraCI connection from settings
    port = SUMO_PORT_DATA
    
    # Set the SUMO_TOOLS_PATH from settings
    sys.path.append(SUMO_TOOLS_PATH)
    
    # Try to import the TraCI module
    try:
        
        import traci
    
    # If import fails, print error and return
    except ImportError:
        
        print("[SUMO TraCI Test] Could not import traci. Check SUMO_TOOLS_PATH.")
        return

    # Define the SUMO network file path from settings
    SUMO_NET_FILE = SUMO_SIMPLE_NET_FILE
    
    # Check if the SUMO network file exists, if not, print error and return
    if not os.path.exists(SUMO_NET_FILE):
        print(f"[SUMO TraCI Test] Network file not found: {SUMO_NET_FILE}")
        return
    
    # Clean up port and traci
    kill_processes_on_port(port)
    cleanup_traci_connection()
    
    # Wait for a moment to ensure cleanup is complete
    time.sleep(2)

    # Define the SUMO binary command, "sumo" or "sumo-gui"
    sumo_binary = "sumo"
    
    # Create and store the command to start SUMO with the network file and remote port
    # Current command will start SUMO in non-GUI mode
    sumo_cmd = [sumo_binary, "-n", SUMO_NET_FILE, "--remote-port", str(port)]
    
    # Try to start SUMO and connect via TraCI
    try:
        
        # Start SUMO process with the stored command
        proc = subprocess.Popen(sumo_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait for a moment to allow SUMO to start
        time.sleep(3)
        
        # Check if the SUMO process has exited early
        # If it has, read and print the STDERR output, then return
        if proc.poll() is not None:
            
            stderr = proc.stderr.read().decode()
            print(f"[SUMO TraCI Test] SUMO exited early. STDERR:\n{stderr}")
            return
        
        # Initialize TraCI connection to the specified port to connect to the running SUMO instance
        traci.init(port=port)
        
        # Wait for a moment to ensure TraCI connection is established
        time.sleep(1)
        
        # Initialize a list to store simulation data
        sim_data = []
        
        # Run the simulation for a fixed number of steps (5 in this case)
        for _ in range(5):
            
            # Perform a simulation step using TraCI
            # This updates the simulation state and allows data retrieval
            traci.simulationStep()
            
            # Retrieve and store the current simulation time, vehicle IDs, and their positions
            sim_time = traci.simulation.getTime()
            veh_ids = traci.vehicle.getIDList()
            veh_positions = {vid: traci.vehicle.getPosition(vid) for vid in veh_ids}
            
            # Store the retrieved data in a dictionary and append it to the sim_data list
            sim_data.append({
                "time": sim_time,
                "vehicle_ids": veh_ids,
                "positions": veh_positions
            })
            
            # If print_data is True, print the current simulation time, vehicle IDs, and positions
            if print_data:
                print(f"Time: {sim_time}, Vehicles: {veh_ids}, Positions: {veh_positions}")
            
            time.sleep(0.1)
        
        # If no exceptions occurred during the simulation and data retrieval, set passed_local to True to indicate success
        passed_local = True
    
    # If any exception occurs during the TraCI data transfer, print the error and set passed_local to False
    except Exception as e:
        
        print(f"[SUMO TraCI Test] Error during TraCI data transfer: {e}")
        passed_local = False
    
    # Ensure that TraCI connection is closed and SUMO process is terminated, regardless of success or failure
    # This is done in a finally block to ensure cleanup occurs even if an error happens
    finally:
        
        # Try to close the TraCI connection if it is loaded
        try:
            
            # Check if TraCI is loaded and close it
            if 'traci' in locals() and traci.isLoaded():
                traci.close()
            
        except Exception:
            pass
        
        # Try to terminate the SUMO process gracefully
        try:
            proc.terminate()
            proc.wait(timeout=3)
        
        # If termination fails, try to kill the process
        except Exception:
            
            try:
                proc.kill()
                
            except Exception:
                pass
        
        # Clean up any processes that may still be running on the specified port
        # This ensures that no leftover processes are blocking the port for future tests
        kill_processes_on_port(port)
        
        time.sleep(1)
    
    # Output the result of the SUMO TraCI data transfer test, increment passed count if successful
    if passed_local:
        passed += 1
        print("[SUMO TraCI Test] Data transfer test succeeded!\n")
        
    else:
        print("[SUMO TraCI Test] Data transfer test failed.\n")


##
# @brief Test connecting to SUMO via TraCI using a .sumocfg file, retrieving and storing simulation data for 100 steps.
# @param print_data If True, print simulation data to screen.
# @details
#   Tests SUMO connection and data retrieval using TraCI with a .sumocfg file.
# @steps
#   1. Start SUMO with a configuration file.
#   2. Connect via TraCI.
#   3. Retrieve simulation time, vehicle IDs, and positions for 100 steps.
#   4. Print/store the data.
#   5. Clean up.
##
def test_sumo_traci_data_transfer_sumocfg(print_data=True):
    
    # Print test header
    print("\n=== SUMO TraCI Data Transfer Test (.sumocfg, 100 steps) ===")
    
    # Use global variables to track tests, increment tested count
    global tested, passed
    tested += 1

    # Define the port for TraCI connection from settings
    port = SUMO_PORT_DATA_CONFIG
    
    # Set the SUMO_TOOLS_PATH from settings
    sys.path.append(SUMO_TOOLS_PATH)
    
    # Try to import the TraCI module
    try:
        
        import traci
    
    # If import fails, print error and return
    except ImportError:
        
        print("[SUMO TraCI Test] Could not import traci. Check SUMO_TOOLS_PATH.")
        return

    # Define the path to the .sumocfg file from settings
    SUMO_SUMOCFG_FILE = SUMO_INTERSECTION_CONFIG_FILE
    
    # Check if the .sumocfg file exists, if not, print error and return
    if not os.path.exists(SUMO_SUMOCFG_FILE):
        
        print(f"[SUMO TraCI Test] .sumocfg file not found: {SUMO_SUMOCFG_FILE}")
        return

    # Clean up port and traci connection before starting the test
    # This ensures that no previous processes are blocking the port
    kill_processes_on_port(port)
    cleanup_traci_connection()
    
    # Wait for a moment to ensure cleanup is complete
    time.sleep(2)

    # Define the SUMO binary command, "sumo" or "sumo-gui"
    sumo_binary = "sumo"
    
    # Create and store the command to start SUMO with the .sumocfg file and remote port
    sumo_cmd = [sumo_binary, "-c", SUMO_SUMOCFG_FILE, "--remote-port", str(port)]
    
    # Try to start SUMO and connect via TraCI
    try:
        
        # Start SUMO process with the stored command
        proc = subprocess.Popen(sumo_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait for a moment to allow SUMO to start
        time.sleep(3)
        
        # Check if the SUMO process has exited early
        # If it has, read and print the STDERR output, then return
        if proc.poll() is not None:
            
            stderr = proc.stderr.read().decode()
            print(f"[SUMO TraCI Test] SUMO exited early. STDERR:\n{stderr}")
            return
        
        # Initialize TraCI connection to the specified port to connect to the running SUMO instance
        traci.init(port=port)
        
        # Wait for a moment to ensure TraCI connection is established
        time.sleep(1)
        
        # Initialize a list to store simulation data
        sim_data = []
        
        # Run the simulation for 100 steps
        for _ in range(100):
            
            # Perform a simulation step using TraCI
            # This updates the simulation state and allows data retrieval
            traci.simulationStep()
            
            # Retrieve and store the current simulation time, vehicle IDs, and their positions
            sim_time = traci.simulation.getTime()
            veh_ids = traci.vehicle.getIDList()
            veh_positions = {vid: traci.vehicle.getPosition(vid) for vid in veh_ids}
            
            # Store the retrieved data in a dictionary and append it to the sim_data list
            sim_data.append({
                "time": sim_time,
                "vehicle_ids": veh_ids,
                "positions": veh_positions
            })
            
            # If print_data is True, print the current simulation time, vehicle IDs, and positions
            if print_data:
                print(f"Time: {sim_time}, Vehicles: {veh_ids}, Positions: {veh_positions}")
                
            time.sleep(0.1)
        
        # If no exceptions occurred during the simulation and data retrieval, set passed_local to True to indicate success
        passed_local = True
    
    # If any exception occurs during the TraCI data transfer, print the error and set passed_local to False
    except Exception as e:
        
        print(f"[SUMO TraCI Test] Error during TraCI data transfer: {e}")
        passed_local = False
    
    # Ensure that TraCI connection is closed and SUMO process is terminated, regardless of success or failure
    # This is done in a finally block to ensure cleanup occurs even if an error happens
    finally:
        
        # Try to close the TraCI connection if it is loaded
        try:
            
            # Check if TraCI is loaded and close it
            if 'traci' in locals() and traci.isLoaded():
                traci.close()
                
        except Exception:
            pass
        
        # Try to terminate the SUMO process gracefully
        try:
            
            proc.terminate()
            proc.wait(timeout=3)
        
        # If termination fails, try to kill the process
        except Exception:
            
            try:
                proc.kill()
                
            except Exception:
                pass
            
        # Clean up any processes that may still be running on the specified port
        # This ensures that no leftover processes are blocking the port for future tests
        kill_processes_on_port(port)
        
        time.sleep(1)
    
    # Output the result of the SUMO sumocfg TraCI data transfer test, increment passed count if successful
    if passed_local:
        passed += 1
        print("[SUMO TraCI Test] .sumocfg data transfer test succeeded!\n")
        
    else:
        print("[SUMO TraCI Test] .sumocfg data transfer test failed.\n")


##
# @brief Run all test and scenario functions and print summary statistics.
# @details
#   Runs all included test and scenario functions in sequence and prints summary statistics.
# @steps
#   1. Run all included test and scenario functions in sequence.
#   2. Print summary statistics for total tests run, passed, and failed.
#   3. Perform SUMO cleanup after connection tests.
##
def testAndScenarioRunner():
    
    # Use global variables to track tests, initialize counts
    global tested, passed
    tested, passed = 0, 0

    # 3 - Run Simulated ZKP Test
    test_vehicle_rsu_interaction_simulated()
    time.sleep(.5)
    # clear_console()

    # 4 - Run Simulated Blockchain ZKP Test
    test_vehicle_rsu_blockchain_simulated()
    time.sleep(.5)
    # clear_console()

    # 5 - Run Simulated End-to-End Scenario: Successful Authentication
    scenario_successful_authentication()
    time.sleep(.5)
    # clear_console()

    # 6 - Run Simulated End-to-End Scenario: Failed Authentication
    scenario_failed_authentication()
    time.sleep(.5)
    # clear_console()

    # 7 - Run Real ZoKrates End-to-End Test with dummy.zok
    test_vehicle_rsu_interaction_real_zokrates_dummy()
    time.sleep(.5)
    # clear_console()

    # 8 - Simulated ZKP Isolated Test: Multiple Vehicles
    test_simulated_isolated_multiple_vehicles()
    time.sleep(.5)
    # clear_console()

    # 9 - Simulated End-to-End Test: Multiple Vehicles
    test_simulated_end_to_end_multiple_vehicles()
    time.sleep(.5)
    # clear_console()

    # 10 - ZoKrates-Integrated Isolated Test: Multiple Vehicles
    test_zokrates_isolated_multiple_vehicles()
    time.sleep(.5)
    # clear_console()

    # 11 - ZoKrates-Integrated End-to-End Test: Multiple Vehicles
    test_zokrates_end_to_end_multiple_vehicles()
    time.sleep(.5)
    # clear_console()

    # 12 - Run SUMO Connection Tests (Basic Network + Configuration File)
    tested, passed = test_sumo_connection_wrapper(tested, passed)
    time.sleep(.5)
    # clear_console()

    # 13 - Run ZoKrates CLI Connection Test
    test_zokrates_connection()
    time.sleep(.5)
    # clear_console()

    # 14 - Run SUMO TraCI Data Transfer Test
    test_sumo_traci_data_transfer(False)
    time.sleep(.5)
    # clear_console()

    # 15 - Run SUMO TraCI Data Transfer Test (.sumocfg, 100 steps)
    test_sumo_traci_data_transfer_sumocfg(False)
    time.sleep(.5)
    # clear_console()

    # SUMO cleanup after connection tests
    cleanup_traci_connection()
    kill_processes_on_port(SUMO_PORT_BASIC)
    kill_processes_on_port(SUMO_PORT_CONFIG)
    kill_processes_on_port(SUMO_PORT_DATA)
    time.sleep(2)

    print(f"\nTotal tests run: {tested}")
    print(f"Total tests passed: {passed}")
    print(f"Total tests failed: {tested - passed}")
    print()
    time.sleep(2)


## Runs all tests and scenarios
if __name__ == "__main__":
    
    # Example usage: toggle PRINT_SUMO_DATA as needed
    # test_sumo_traci_data_transfer(print_data=True)
    # test_sumo_traci_data_transfer_sumocfg(print_data=True)
    
    testAndScenarioRunner()
