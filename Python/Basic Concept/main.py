"""
main.py

Purpose:
    Orchestrates the simulation of a privacy-preserving vehicle authentication protocol using Zero-Knowledge Proofs (ZKP) and blockchain logging.
    Demonstrates both a simulated and (eventually) real ZoKrates-based ZKP workflow, as well as simulated and (eventually) real blockchain 
    verification and event logging.
"""

import preliminary_tests

# Breakdown of the workflow, based on the original paper's description:

# Part One
# 1. Vehicle generates an OTP using unique secret and timestamp
# 2. OTP is embedded into a ZKP, proving the OTP valid without revealing the secret
# 3. ZKP is sent to the RSU, where it is verified
# 4. Upon successful verification, the RSU sends a signal to the vehicle authenticating it and proceeding with session

# Part Two
# 1. ZKP-OTP proof is submitted to RSU
# 2. RSU invokes a smart contract on the blockchain, verifying the ZKP-OTP proof
# 3. The blockchain logs the event, including anonymized record of the vehicle’s identity and authentication status
# 4. The outcome is returned to the infrastructure, which grants or denies access.

def cli_menu():
    print("Privacy-Preserving Vehicle Authentication Protocol Simulation")
    print("Select an option:")
    print("1. Run all tests and scenarios")
    print("2. Run ZoKrates CLI Connection Test")
    print("3. Run Simulated ZKP Test")
    print("4. Run Simulated Blockchain ZKP Test")
    print("5. Run Simulated End-to-End Scenario: Successful Authentication")
    print("6. Run Simulated End-to-End Scenario: Failed Authentication")
    print("7. Run Real ZoKrates End-to-End Test with dummy.zok")
    print("0. Exit")
    return input("Enter your choice: ").strip()

if __name__ == "__main__":
    while True:
        choice = cli_menu()
        if choice == "1":
            preliminary_tests.testAndScenarioRunner()
        elif choice == "2":
            preliminary_tests.test_zokrates_connection()
        elif choice == "3":
            preliminary_tests.test_vehicle_rsu_interaction_simulated()
        elif choice == "4":
            preliminary_tests.test_vehicle_rsu_blockchain_simulated()
        elif choice == "5":
            preliminary_tests.scenario_successful_authentication()
        elif choice == "6":
            preliminary_tests.scenario_failed_authentication()
        elif choice == "7":
            preliminary_tests.test_vehicle_rsu_interaction_real_zokrates_dummy()
        elif choice == "0":
            print("Exiting.")
            break
        else:
            print("Invalid choice. Please try again.")
