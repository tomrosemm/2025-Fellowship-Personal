"""
preliminary_tests.py

Purpose:
    This module contains test routines to simulate and validate the ZKP-OTP authentication protocol
    between Vehicle and RSU entities. It demonstrates the authentication process using both simulated
    and real (ZoKrates-based) zero-knowledge proof workflows, as well as a blockchain verification simulation.

Methodology:
    - Simulates the generation of one-time passwords (OTP) and timestamps by vehicles.
    - Demonstrates creation of zero-knowledge proofs (ZKP) for OTP and timestamp.
    - Shows verification of ZKPs by RSUs using both simulated (hash-based) and real ZoKrates CLI methods.
    - Includes a workflow for simulating blockchain-based verification and logging.
    - Provides functions for each workflow, which can be run directly for demonstration and prototyping.

Usage:
    Run this script directly to execute the included test scenarios.
    Requires: vehicle.py, rsu.py, zokrates_interface.py, blockchain.py
"""

import secrets                                              # For generating random secrets for vehicles

from vehicle import Vehicle                                 # Vehicle entity: generates OTPs and ZKPs
from rsu import RSU                                         # RSU entity: verifies ZKPs from vehicles
from zokrates_interface import (                        
    generate_zkp_proof,                                     # (Currently unused here) For generating ZKP proofs via ZoKrates
    run_zokrates_compile,                                   # Compile ZoKrates circuit
    run_zokrates_setup,                                     # Setup ZoKrates proving/verification keys
    run_zokrates_compute_witness,                           # Compute ZoKrates witness from inputs
    run_zokrates_generate_proof,                            # Generate ZKP proof using ZoKrates
    run_zokrates_verify,                                    # Verify ZKP proof using ZoKrates
)
from blockchain import simulate_blockchain_verification     # Simulate blockchain-based verification and logging

# Track number of tests run and passed
tested = 0
passed = 0

"""
Function: test_vehicle_rsu_interaction_simulated

Test the workflow using a simulated ZKP (hash-based).

Steps:
    1. Generate a random vehicle secret and create Vehicle and RSU entities.
    2. Vehicle generates an OTP and timestamp.
    3. Vehicle creates a simulated ZKP proof (hash-based) for the OTP and timestamp.
    4. RSU verifies the ZKP proof using the known vehicle secret and timestamp.
    5. Output the result of the verification and authentication status.
"""
def test_vehicle_rsu_interaction_simulated():
    global tested, passed
    tested += 1
    # Generate entities
    vehicle_id = "VEH123"
    vehicle_secret = secrets.token_hex(16)
    vehicle = Vehicle(vehicle_id, vehicle_secret)
    rsu = RSU({vehicle_id: vehicle_secret})

    # Generate OTP and timestamp
    otp, timestamp = vehicle.generate_otp()
    print(f"\n[Simulated] OTP: {otp}\n\nTimestamp: {timestamp}\n")

    # Create simulated ZKP proof
    zkp_proof = vehicle.create_zkp(otp, timestamp)
    print(f"[Simulated] ZKP Proof: {zkp_proof}\n")

    # RSU verifies ZKP proof
    verification_result = rsu.verify_zkp(vehicle_id, zkp_proof, timestamp)
    print(f"[Simulated] Verification result: {verification_result}\n")

    # Output authentication result
    if verification_result:
        passed += 1
        print("[Simulated] Vehicle authenticated. Session started.\n")
    else:
        print("[Simulated] Authentication failed.\n")


"""
Function: test_vehicle_rsu_interaction_real

Test the workflow using the real ZoKrates CLI (when available).
"""
def test_vehicle_rsu_interaction_real():
    global tested, passed
    tested += 1
    vehicle_id = "VEH123"
    vehicle_secret = secrets.token_hex(16)
    vehicle = Vehicle(vehicle_id, vehicle_secret)
    rsu = RSU({vehicle_id: vehicle_secret})

    otp, timestamp = vehicle.generate_otp()
    print(f"\n[Real ZKP] OTP: {otp}\nTimestamp: {timestamp}\n")

    # --- ZoKrates workflow ---
    # 1. Compile circuit
    # 2. Setup
    # 3. Compute witness (inputs must match your circuit)
    # 4. Generate proof
    # 5. Verify proof
    
    # Path to your ZoKrates circuit file
    circuit_path = "otp.zok"
    
    # Compile circuit
    if not run_zokrates_compile(circuit_path):
        print("[Real ZKP] Compilation failed.")
        return
    
    # Setup
    if not run_zokrates_setup():
        print("[Real ZKP] Setup failed.")
        return
    
    # Compute witness (inputs must match your circuit)
    # Example: args = [otp, timestamp] as strings
    args = [str(otp), str(timestamp)]
    if not run_zokrates_compute_witness(args):
        print("[Real ZKP] Compute witness failed.")
        return
    
    # Generate proof
    if not run_zokrates_generate_proof():
        print("[Real ZKP] Proof generation failed.")
        return
    
    # Verify proof
    verification_result = run_zokrates_verify()
    print(f"[Real ZKP] Verification result: {verification_result}\n")

    if verification_result:
        passed += 1
        print("[Real ZKP] Vehicle authenticated. Session started.\n")
    else:
        print("[Real ZKP] Authentication failed.\n")


"""
Function: test_vehicle_rsu_blockchain_simulated

Simulate the full workflow, including using ZoKrates for the ZKP as well as blockchain verification and logging.

Steps:
    1. Generate a random vehicle secret and create Vehicle and RSU entities.
    2. Vehicle generates an OTP and timestamp.
    3. Vehicle creates a simulated ZKP proof (hash-based) for the OTP and timestamp.
    4. RSU verifies the ZKP proof using the known vehicle secret and timestamp.
    5. Simulate blockchain smart contract verification and logging of the authentication attempt.
    6. Output the result of the infrastructure access decision.
"""
def test_vehicle_rsu_blockchain_simulated():
    global tested, passed
    tested += 1
    # Generate entities
    vehicle_id = "VEH123"
    vehicle_secret = secrets.token_hex(16)
    vehicle = Vehicle(vehicle_id, vehicle_secret)
    rsu = RSU({vehicle_id: vehicle_secret})

    # Generate OTP and timestamp
    otp, timestamp = vehicle.generate_otp()
    print(f"\n[Simulated] OTP: {otp}\n\nTimestamp: {timestamp}\n")

    # Create simulated ZKP proof
    zkp_proof = vehicle.create_zkp(otp, timestamp)
    print(f"[Simulated] ZKP Proof: {zkp_proof}\n")

    # RSU verifies ZKP proof
    verification_result = rsu.verify_zkp(vehicle_id, zkp_proof, timestamp)
    print(f"[Simulated] RSU Verification result: {verification_result}\n")

    # Simulate blockchain verification and logging
    outcome = simulate_blockchain_verification(vehicle_id, zkp_proof, timestamp, verification_result)
    # Output infrastructure access result
    if outcome:
        passed += 1
        print("[Simulated] Access granted by infrastructure.\n\n")
    else:
        print("[Simulated] Access denied by infrastructure.\n\n")

if __name__ == "__main__":
    print("=== Simulated ZKP Test ===")
    test_vehicle_rsu_interaction_simulated()
    print("=== Simulated Blockchain ZKP Test ===")
    test_vehicle_rsu_blockchain_simulated()
    
    # Uncomment the next line to run the real ZoKrates workflow (requires ZoKrates and a valid circuit)
    # print("=== Real ZKP Test ===")
    # test_vehicle_rsu_interaction_real()

    print("----------------------------------------------------------------------------------------------------------")
    print(f"Total tests run: {tested}")
    print(f"Total tests passed: {passed}")

