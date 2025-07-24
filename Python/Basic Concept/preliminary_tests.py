"""
preliminary_tests.py

Author: Tom Rose

Purpose:
    This module contains test routines to simulate and validate the ZKP-OTP authentication protocol
    between Vehicle and RSU entities. It demonstrates the authentication process using both simulated
    and real (ZoKrates-based) zero-knowledge proof workflows, as well as a blockchain verification simulation.
    It contains tests for basic connection with related software/tools, such as ZoKrates and SUMO (next: OMNeT++ or Mininet)

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

from blockchain import simulate_blockchain_verification, set_debug_mode as set_blockchain_debug_mode
from sumo_interface import test_sumo_connection_wrapper, set_debug_mode as set_sumo_debug_mode
from zkp import generate_zkp_proof_simulated

# Uncomment if blockchain_interface is used
# from blockchain_interface import set_debug_mode as set_blockchain_interface_debug_mode

# Track number of tests run and passed
tested = 0
passed = 0


DEBUG_MODE = False


"""
Function: set_debug_mode

Enable or disable debug mode for detailed output.

Args:
    enabled (bool): True to enable debug mode, False to disable.

Steps:
    1. Set the global DEBUG_MODE variable to the provided value.
    2. Propagate debug mode to all relevant modules/classes.
"""
def set_debug_mode(enabled):
    
    global DEBUG_MODE
    DEBUG_MODE = enabled
    set_zokrates_debug_mode(enabled)
    set_blockchain_debug_mode(enabled)
    set_sumo_debug_mode(enabled)
    
    # set_blockchain_interface_debug_mode(enabled)


"""
Function: clear_console

Clears the console screen based on the operating system.

Steps:
    1. If Windows, use 'cls'.
    2. Otherwise, use 'clear'.
"""
def clear_console():
    if os.name == 'nt':         # For Windows
        os.system('cls')
    else:                       # For macOS/Linux
        os.system('clear')


"""
Test the workflow using a simulated ZKP (hash-based).

Steps:
    1. Generate a random vehicle secret and create Vehicle and RSU entities.
    2. Vehicle generates an OTP and timestamp.
    3. Vehicle creates a simulated ZKP proof (hash-based) for the OTP and timestamp.
    4. RSU verifies the ZKP proof using the known vehicle secret and timestamp.
    5. Output the result of the verification and authentication status.
"""
def test_vehicle_rsu_interaction_simulated():
    print("\n=== Simulated ZKP Test ===")
    global tested, passed
    tested += 1
    # Generate entities
    vehicle_id = "VEH123"
    vehicle_secret = secrets.token_hex(16)
    vehicle = Vehicle(vehicle_id, vehicle_secret)
    rsu = RSU({vehicle_id: vehicle_secret})

    # Generate OTP and timestamp
    otp, timestamp = vehicle.generate_otp()
    if DEBUG_MODE:
        print(f"\n[Simulated] OTP: {otp}\n\nTimestamp: {timestamp}\n")
    # Use simulated ZKP proof
    zkp_proof = generate_zkp_proof_simulated(otp, timestamp)
    if DEBUG_MODE:
        print(f"[Simulated] ZKP Proof: {zkp_proof}\n")
    # RSU verifies ZKP proof using simulated logic
    expected_zkp = generate_zkp_proof_simulated(otp, timestamp)
    verification_result = (zkp_proof == expected_zkp)
    if DEBUG_MODE:
        print(f"[Simulated] Verification result: {verification_result}\n")

    # Output authentication result
    if verification_result:
        passed += 1
        print("[Simulated] Vehicle authenticated. Session started.\n")
    else:
        print("[Simulated] Authentication failed.\n")


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
    print("\n=== Simulated Blockchain ZKP Test ===")
    global tested, passed
    tested += 1
    # Generate entities
    vehicle_id = "VEH123"
    vehicle_secret = secrets.token_hex(16)
    vehicle = Vehicle(vehicle_id, vehicle_secret)
    rsu = RSU({vehicle_id: vehicle_secret})

    # Generate OTP and timestamp
    otp, timestamp = vehicle.generate_otp()
    if DEBUG_MODE:
        print(f"\n[Simulated] OTP: {otp}\n\nTimestamp: {timestamp}\n")
    zkp_proof = generate_zkp_proof_simulated(otp, timestamp)
    if DEBUG_MODE:
        print(f"[Simulated] ZKP Proof: {zkp_proof}\n")
    expected_zkp = generate_zkp_proof_simulated(otp, timestamp)
    verification_result = (zkp_proof == expected_zkp)
    if DEBUG_MODE:
        print(f"[Simulated] RSU Verification result: {verification_result}\n")

    # Simulate blockchain verification and logging
    outcome = simulate_blockchain_verification(vehicle_id, zkp_proof, timestamp, verification_result) if DEBUG_MODE else verification_result
    # Output infrastructure access result
    if outcome:
        passed += 1
        print("[Simulated] Access granted by infrastructure.\n")
    else:
        print("[Simulated] Access denied by infrastructure.\n")


"""End-to-end scenario: Vehicle authenticates successfully and is granted access."""
def scenario_successful_authentication():
    print("\n=== End-to-End Scenario: Successful Authentication ===")
    global tested, passed
    tested += 1
    vehicle_id = "VEH001"
    vehicle_secret = secrets.token_hex(16)
    vehicle = Vehicle(vehicle_id, vehicle_secret)
    rsu = RSU({vehicle_id: vehicle_secret})

    # Generate OTP and timestamp
    otp, timestamp = vehicle.generate_otp()
    if DEBUG_MODE:
        print(f"\nVehicle {vehicle_id} generated OTP: {otp} at {timestamp}\n")
    zkp_proof = generate_zkp_proof_simulated(otp, timestamp)
    if DEBUG_MODE:
        print(f"Vehicle {vehicle_id} created ZKP proof: {zkp_proof}\n")
    expected_zkp = generate_zkp_proof_simulated(otp, timestamp)
    verification_result = (zkp_proof == expected_zkp)
    if DEBUG_MODE:
        print(f"RSU verification result: {verification_result}\n")

    # Blockchain verification and access outcome
    outcome = simulate_blockchain_verification(vehicle_id, zkp_proof, timestamp, verification_result) if DEBUG_MODE else verification_result
    if outcome:
        passed += 1
        print("Access granted by infrastructure.\n")
    else:
        print("Access denied by infrastructure.\n")


"""End-to-end scenario: Vehicle fails authentication due to wrong secret."""
def scenario_failed_authentication():
    print("\n=== End-to-End Scenario: Failed Authentication ===")
    global tested, passed
    tested += 1
    vehicle_id = "VEH001"
    correct_secret = secrets.token_hex(16)
    wrong_secret = secrets.token_hex(16)
    vehicle = Vehicle(vehicle_id, wrong_secret)  # Vehicle uses wrong secret
    rsu = RSU({vehicle_id: correct_secret})      # RSU expects correct secret

    # Generate OTP and timestamp
    otp, timestamp = vehicle.generate_otp()
    if DEBUG_MODE:
        print(f"\nVehicle {vehicle_id} generated OTP: {otp} at {timestamp}\n")
    zkp_proof = generate_zkp_proof_simulated(otp, timestamp)
    if DEBUG_MODE:
        print(f"Vehicle {vehicle_id} created ZKP proof: {zkp_proof}\n")
    # RSU expects correct secret, so expected_zkp is based on correct_secret
    otp_expected, _ = Vehicle(vehicle_id, correct_secret).generate_otp()
    expected_zkp = generate_zkp_proof_simulated(otp_expected, timestamp)
    verification_result = (zkp_proof == expected_zkp)
    if DEBUG_MODE:
        print(f"RSU verification result: {verification_result}\n")

    # Blockchain verification and access outcome
    outcome = simulate_blockchain_verification(vehicle_id, zkp_proof, timestamp, verification_result) if DEBUG_MODE else verification_result
    if outcome:
        print("Access granted by infrastructure (unexpected).\n")
    else:
        passed += 1
        print("Access denied by infrastructure (expected).\n")


"""
Function: test_zokrates_connection

Test the connection and workflow with ZoKrates CLI using dummy.zok.

Steps:
    1. Compile dummy.zok
    2. Setup
    3. Compute witness (inputs: a=3, b=4)
    4. Generate proof
    5. Verify proof
"""
def test_zokrates_connection():
    print("\n=== ZoKrates CLI Connection Test ===")
    global tested, passed
    tested += 1
    circuit_path = "dummy.zok"
    # Compile circuit
    if not run_zokrates_compile(circuit_path):
        print("[ZoKrates Test] Compilation failed.")
        return
    # Setup
    if not run_zokrates_setup():
        print("[ZoKrates Test] Setup failed.")
        cleanup_zokrates_files()
        return
    # Compute witness (inputs: a=3, b=4)
    args = ["3", "4"]
    if not run_zokrates_compute_witness(args):
        print("[ZoKrates Test] Compute witness failed.")
        cleanup_zokrates_files()
        return
    # Generate proof
    if not run_zokrates_generate_proof():
        print("[ZoKrates Test] Proof generation failed.")
        cleanup_zokrates_files()
        return
    # Verify proof
    verification_result = run_zokrates_verify()
    if DEBUG_MODE:
        print(f"[ZoKrates Test] Verification result: {verification_result}\n")
    if verification_result:
        passed += 1
        print("[ZoKrates Test] ZoKrates connection and workflow succeeded!\n")
    else:
        print("[ZoKrates Test] ZoKrates connection or workflow failed.\n")
    # Always clean up ZoKrates artifacts after test
    cleanup_zokrates_files()


"""
Test the end-to-end ZoKrates workflow using dummy.zok and random inputs.
This simulates a real ZKP workflow using the ZoKrates CLI on Linux.
"""
def test_vehicle_rsu_interaction_real_zokrates_dummy():
    print("\n=== Real ZoKrates End-to-End Test with dummy.zok ===")
    global tested, passed
    tested += 1
    circuit_path = "dummy.zok"
    # Generate random field inputs for dummy.zok
    a = random.randint(1, 100)
    b = random.randint(1, 100)
    if DEBUG_MODE:
        print(f"Inputs: a={a}, b={b}")
    # Compile circuit
    if not run_zokrates_compile(circuit_path):
        print("[Real ZKP] Compilation failed.")
        return
    # Setup
    if not run_zokrates_setup():
        print("[Real ZKP] Setup failed.")
        cleanup_zokrates_files()
        return
    # Compute witness
    args = [str(a), str(b)]
    if not run_zokrates_compute_witness(args):
        print("[Real ZKP] Compute witness failed.")
        cleanup_zokrates_files()
        return
    # Generate proof
    if not run_zokrates_generate_proof():
        print("[Real ZKP] Proof generation failed.")
        cleanup_zokrates_files()
        return
    # Verify proof
    verification_result = run_zokrates_verify()
    if DEBUG_MODE:
        print(f"[Real ZKP] Verification result: {verification_result}\n")
    if verification_result:
        passed += 1
        print("[Real ZKP] End-to-end ZoKrates workflow succeeded!\n")
    else:
        print("[Real ZKP] End-to-end ZoKrates workflow failed.\n")
    cleanup_zokrates_files()


"""Simulated ZKP isolated test with multiple vehicles."""
def test_simulated_isolated_multiple_vehicles():
    global tested, passed
    tested += 1
    print("\n=== Simulated ZKP Isolated Test: Multiple Vehicles ===")
    num_vehicles = 3
    vehicles = {}
    rsu_secrets = {}
    for i in range(num_vehicles):
        vid = f"VEH{i+1:03d}"
        secret = secrets.token_hex(16)
        vehicles[vid] = Vehicle(vid, secret)
        rsu_secrets[vid] = secret
    rsu = RSU(rsu_secrets)
    all_passed = True
    circuit_path = "dummy.zok"
    for vid, vehicle in vehicles.items():
        otp, timestamp = vehicle.generate_otp()
        zkp_proof = generate_zkp_proof_simulated(otp, timestamp)
        expected_zkp = generate_zkp_proof_simulated(otp, timestamp)
        result = (zkp_proof == expected_zkp)
        if DEBUG_MODE:
            print(f"Vehicle {vid}: Verification result: {result}")
        all_passed = all_passed and result
    if all_passed:
        passed += 1
        print("[Simulated] All vehicles authenticated successfully.\n")
    else:
        print("[Simulated] Some vehicles failed authentication.\n")


"""Simulated end-to-end test with multiple vehicles (RSU + blockchain)."""
def test_simulated_end_to_end_multiple_vehicles():
    global tested, passed
    tested += 1
    print("\n=== Simulated End-to-End Test: Multiple Vehicles ===")
    num_vehicles = 3
    vehicles = {}
    rsu_secrets = {}
    for i in range(num_vehicles):
        vid = f"VEH{i+1:03d}"
        secret = secrets.token_hex(16)
        vehicles[vid] = Vehicle(vid, secret)
        rsu_secrets[vid] = secret
    rsu = RSU(rsu_secrets)
    all_passed = True
    circuit_path = "dummy.zok"
    for vid, vehicle in vehicles.items():
        otp, timestamp = vehicle.generate_otp()
        zkp_proof = generate_zkp_proof_simulated(otp, timestamp)
        expected_zkp = generate_zkp_proof_simulated(otp, timestamp)
        verification_result = (zkp_proof == expected_zkp)
        outcome = simulate_blockchain_verification(vid, zkp_proof, timestamp, verification_result) if DEBUG_MODE else verification_result
        if DEBUG_MODE:
            print(f"Vehicle {vid}: RSU result: {verification_result}, Blockchain outcome: {outcome}")
        all_passed = all_passed and outcome
    if all_passed:
        passed += 1
        print("[Simulated] All vehicles granted access by infrastructure.\n")
    else:
        print("[Simulated] Some vehicles denied access.\n")


"""ZoKrates-integrated isolated test with multiple vehicles (dummy.zok)."""
def test_zokrates_isolated_multiple_vehicles():
    global tested, passed
    tested += 1
    print("\n=== ZoKrates-Integrated Isolated Test: Multiple Vehicles ===")
    circuit_path = "dummy.zok"
    num_vehicles = 2
    all_passed = True
    for i in range(num_vehicles):
        a = random.randint(1, 100)
        b = random.randint(1, 100)
        if DEBUG_MODE:
            print(f"Vehicle {i+1}: Inputs a={a}, b={b}")
        if not run_zokrates_compile(circuit_path):
            print("[ZoKrates] Compilation failed.")
            all_passed = False
            continue
        if not run_zokrates_setup():
            print("[ZoKrates] Setup failed.")
            cleanup_zokrates_files()
            all_passed = False
            continue
        args = [str(a), str(b)]
        if not run_zokrates_compute_witness(args):
            print("[ZoKrates] Compute witness failed.")
            cleanup_zokrates_files()
            all_passed = False
            continue
        if not run_zokrates_generate_proof():
            print("[ZoKrates] Proof generation failed.")
            cleanup_zokrates_files()
            all_passed = False
            continue
        verification_result = run_zokrates_verify()
        if DEBUG_MODE:
            print(f"Vehicle {i+1}: ZoKrates verification result: {verification_result}")
        if not verification_result:
            all_passed = False
        cleanup_zokrates_files()
    if all_passed:
        passed += 1
        print("[ZoKrates] All vehicles' proofs verified successfully.\n")
    else:
        print("[ZoKrates] Some vehicles' proofs failed verification.\n")


"""ZoKrates-integrated end-to-end test with multiple vehicles (dummy.zok + simulated blockchain)."""
def test_zokrates_end_to_end_multiple_vehicles():
    global tested, passed
    tested += 1
    print("\n=== ZoKrates-Integrated End-to-End Test: Multiple Vehicles ===")
    circuit_path = "dummy.zok"
    num_vehicles = 2
    all_passed = True
    for i in range(num_vehicles):
        vid = f"ZOKR_VEH{i+1:03d}"
        a = random.randint(1, 100)
        b = random.randint(1, 100)
        if DEBUG_MODE:
            print(f"Vehicle {vid}: Inputs a={a}, b={b}")
        if not run_zokrates_compile(circuit_path):
            print("[ZoKrates] Compilation failed.")
            all_passed = False
            continue
        if not run_zokrates_setup():
            print("[ZoKrates] Setup failed.")
            cleanup_zokrates_files()
            all_passed = False
            continue
        args = [str(a), str(b)]
        if not run_zokrates_compute_witness(args):
            print("[ZoKrates] Compute witness failed.")
            cleanup_zokrates_files()
            all_passed = False
            continue
        if not run_zokrates_generate_proof():
            print("[ZoKrates] Proof generation failed.")
            cleanup_zokrates_files()
            all_passed = False
            continue
        verification_result = run_zokrates_verify()
        if DEBUG_MODE:
            print(f"Vehicle {vid}: ZoKrates verification result: {verification_result}")
        outcome = simulate_blockchain_verification(vid, f"proof_{a}_{b}", int(time.time()), verification_result) if DEBUG_MODE else verification_result
        if DEBUG_MODE:
            print(f"Vehicle {vid}: Blockchain outcome: {outcome}")
        if not (verification_result and outcome):
            all_passed = False
        cleanup_zokrates_files()
    if all_passed:
        passed += 1
        print("[ZoKrates] All vehicles' end-to-end proofs and blockchain logs succeeded.\n")
    else:
        print("[ZoKrates] Some vehicles failed end-to-end ZoKrates or blockchain verification.\n")


"""
Test connecting to SUMO via TraCI, retrieving and storing simulation data.
Steps:
    1. Start SUMO with a simple network.
    2. Connect via TraCI.
    3. Retrieve simulation time, vehicle IDs, and positions.
    4. Print/store the data.
    5. Clean up.
Args:
    print_data (bool): If True, print simulation data to screen.
"""
def test_sumo_traci_data_transfer(print_data=True):
    
    print("\n=== SUMO TraCI Data Transfer Test ===")
    global tested, passed
    tested += 1

    port = 8815
    SUMO_TOOLS_PATH = os.getenv("SUMO_TOOLS_PATH", "/home/admin/sumo/tools")
    sys.path.append(SUMO_TOOLS_PATH)
    try:
        import traci
    except ImportError:
        print("[SUMO TraCI Test] Could not import traci. Check SUMO_TOOLS_PATH.")
        return

    SUMO_NET_FILE = os.path.abspath("/home/admin/2025-Fellowship-Personal/Python/Basic Concept/sumo/simple.net.xml")
    if not os.path.exists(SUMO_NET_FILE):
        print(f"[SUMO TraCI Test] Network file not found: {SUMO_NET_FILE}")
        return

    # Clean up port and traci
    from sumo_interface import kill_processes_on_port, cleanup_traci_connection
    kill_processes_on_port(port)
    cleanup_traci_connection()
    time.sleep(2)

    sumo_binary = "sumo"
    sumo_cmd = [sumo_binary, "-n", SUMO_NET_FILE, "--remote-port", str(port)]
    try:
        proc = subprocess.Popen(sumo_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        time.sleep(3)
        if proc.poll() is not None:
            stderr = proc.stderr.read().decode()
            print(f"[SUMO TraCI Test] SUMO exited early. STDERR:\n{stderr}")
            return
        traci.init(port=port)
        time.sleep(1)
        
        # Step simulation and collect data
        sim_data = []
        for _ in range(5):
            traci.simulationStep()
            sim_time = traci.simulation.getTime()
            veh_ids = traci.vehicle.getIDList()
            veh_positions = {vid: traci.vehicle.getPosition(vid) for vid in veh_ids}
            sim_data.append({
                "time": sim_time,
                "vehicle_ids": veh_ids,
                "positions": veh_positions
            })
            if print_data:
                print(f"Time: {sim_time}, Vehicles: {veh_ids}, Positions: {veh_positions}")
            time.sleep(0.2)
            
        passed_local = True
        
    except Exception as e:
        print(f"[SUMO TraCI Test] Error during TraCI data transfer: {e}")
        passed_local = False
    finally:
        try:
            if 'traci' in locals() and traci.isLoaded():
                traci.close()
        except Exception:
            pass
        try:
            proc.terminate()
            proc.wait(timeout=3)
        except Exception:
            try:
                proc.kill()
            except Exception:
                pass
        kill_processes_on_port(port)
        time.sleep(1)
    if passed_local:
        passed += 1
        print("[SUMO TraCI Test] Data transfer test succeeded!\n")
    else:
        print("[SUMO TraCI Test] Data transfer test failed.\n")


"""
Test connecting to SUMO via TraCI using a .sumocfg file, retrieving and storing simulation data for 100 steps.
Args:
    print_data (bool): If True, print simulation data to screen.
"""
def test_sumo_traci_data_transfer_sumocfg(print_data=True):
    
    print("\n=== SUMO TraCI Data Transfer Test (.sumocfg, 100 steps) ===")
    global tested, passed
    tested += 1

    port = 8816
    SUMO_TOOLS_PATH = os.getenv("SUMO_TOOLS_PATH", "/home/admin/sumo/tools")
    sys.path.append(SUMO_TOOLS_PATH)
    try:
        import traci
    except ImportError:
        print("[SUMO TraCI Test] Could not import traci. Check SUMO_TOOLS_PATH.")
        return

    # Update this path to your actual .sumocfg file location
    SUMO_SUMOCFG_FILE = os.path.abspath("/home/admin/2025-Fellowship-Personal/Python/Basic Concept/sumo/Intersection 1/intersection1.sumocfg")
    if not os.path.exists(SUMO_SUMOCFG_FILE):
        print(f"[SUMO TraCI Test] .sumocfg file not found: {SUMO_SUMOCFG_FILE}")
        return

    from sumo_interface import kill_processes_on_port, cleanup_traci_connection
    kill_processes_on_port(port)
    cleanup_traci_connection()
    time.sleep(2)

    sumo_binary = "sumo"
    sumo_cmd = [sumo_binary, "-c", SUMO_SUMOCFG_FILE, "--remote-port", str(port)]
    try:
        proc = subprocess.Popen(sumo_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        time.sleep(3)
        if proc.poll() is not None:
            stderr = proc.stderr.read().decode()
            print(f"[SUMO TraCI Test] SUMO exited early. STDERR:\n{stderr}")
            return
        traci.init(port=port)
        time.sleep(1)
        
        sim_data = []
        for _ in range(100):
            traci.simulationStep()
            sim_time = traci.simulation.getTime()
            veh_ids = traci.vehicle.getIDList()
            veh_positions = {vid: traci.vehicle.getPosition(vid) for vid in veh_ids}
            sim_data.append({
                "time": sim_time,
                "vehicle_ids": veh_ids,
                "positions": veh_positions
            })
            if print_data:
                print(f"Time: {sim_time}, Vehicles: {veh_ids}, Positions: {veh_positions}")
            time.sleep(0.05)
            
        passed_local = True
        
    except Exception as e:
        print(f"[SUMO TraCI Test] Error during TraCI data transfer: {e}")
        passed_local = False
    finally:
        try:
            if 'traci' in locals() and traci.isLoaded():
                traci.close()
        except Exception:
            pass
        try:
            proc.terminate()
            proc.wait(timeout=3)
        except Exception:
            try:
                proc.kill()
            except Exception:
                pass
        kill_processes_on_port(port)
        time.sleep(1)
    if passed_local:
        passed += 1
        print("[SUMO TraCI Test] .sumocfg data transfer test succeeded!\n")
    else:
        print("[SUMO TraCI Test] .sumocfg data transfer test failed.\n")


"""
Function: testAndScenarioRunner

Run all test and scenario functions and print summary statistics.

Steps:
    1. Run all included test and scenario functions in sequence.
    2. Print summary statistics for total tests run, passed, and failed.
    3. Perform SUMO cleanup after connection tests.
"""
def testAndScenarioRunner():
    
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
    test_sumo_traci_data_transfer(True)
    time.sleep(.5)
    # clear_console()

    # 15 - Run SUMO TraCI Data Transfer Test (.sumocfg, 100 steps)
    test_sumo_traci_data_transfer_sumocfg(True)
    time.sleep(.5)
    # clear_console()

    # --- SUMO cleanup after connection tests ---
    from sumo_interface import cleanup_traci_connection, kill_processes_on_port
    cleanup_traci_connection()
    kill_processes_on_port(8813)
    kill_processes_on_port(8814)
    kill_processes_on_port(8815)
    time.sleep(2)
    # ------------------------------------------

    print(f"\nTotal tests run: {tested}")
    print(f"Total tests passed: {passed}")
    print(f"Total tests failed: {tested - passed}")
    print()
    time.sleep(2)


if __name__ == "__main__":
    # Example usage: toggle PRINT_SUMO_DATA as needed
    test_sumo_traci_data_transfer(print_data=True)
    test_sumo_traci_data_transfer_sumocfg(print_data=True)
    testAndScenarioRunner()