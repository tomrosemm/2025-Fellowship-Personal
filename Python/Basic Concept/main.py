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

def cli_menu_loop():
    while True:
        print("Privacy-Preserving Vehicle Authentication Protocol Simulation")
        print("Select an option:")
        print("1. Run all tests and scenarios")
        print("2. Run ZoKrates CLI Connection Test")
        print("3. Run Simulated ZKP Test")
        print("4. Run Simulated Blockchain ZKP Test")
        print("5. Run Simulated End-to-End Scenario: Successful Authentication")
        print("6. Run Simulated End-to-End Scenario: Failed Authentication")
        print("7. Run Real ZoKrates End-to-End Test with dummy.zok")
        print("8. Simulated ZKP Isolated Test: Multiple Vehicles")
        print("9. Simulated End-to-End Test: Multiple Vehicles")
        print("10. ZoKrates-Integrated Isolated Test: Multiple Vehicles")
        print("11. ZoKrates-Integrated End-to-End Test: Multiple Vehicles")
        print("12. Run all tests and scenarios with Debug Mode enabled")
        print("d. Enable Debug Mode")
        print("n. Disable Debug Mode")
        print("0. Exit")
        choice = input("Enter your choice: ").strip()
        match choice:
            case "1":
                preliminary_tests.testAndScenarioRunner()
            case "2":
                preliminary_tests.test_zokrates_connection()
            case "3":
                preliminary_tests.test_vehicle_rsu_interaction_simulated()
            case "4":
                preliminary_tests.test_vehicle_rsu_blockchain_simulated()
            case "5":
                preliminary_tests.scenario_successful_authentication()
            case "6":
                preliminary_tests.scenario_failed_authentication()
            case "7":
                preliminary_tests.test_vehicle_rsu_interaction_real_zokrates_dummy()
            case "8":
                preliminary_tests.test_simulated_isolated_multiple_vehicles()
            case "9":
                preliminary_tests.test_simulated_end_to_end_multiple_vehicles()
            case "10":
                preliminary_tests.test_zokrates_isolated_multiple_vehicles()
            case "11":
                preliminary_tests.test_zokrates_end_to_end_multiple_vehicles()
            case "12":
                preliminary_tests.set_debug_mode(True)
                preliminary_tests.testAndScenarioRunner()
            case "d":
                preliminary_tests.set_debug_mode(True)
                print("Debug mode enabled.\n")
            case "n":
                preliminary_tests.set_debug_mode(False)
                print("Debug mode disabled.\n")
            case "0":
                print("Exiting.")
                break
            case _:
                print("Invalid choice. Please try again.")

if __name__ == "__main__":
    cli_menu_loop()
