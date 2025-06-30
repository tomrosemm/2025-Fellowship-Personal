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
    print("2. Run individual test")
    print("0. Exit")
    return input("Enter your choice: ").strip()

def list_individual_tests():
    # List all callable functions in preliminary_tests that look like tests, except the runner
    return [
        func for func in dir(preliminary_tests)
        if callable(getattr(preliminary_tests, func))
        and func.startswith("test")
        and func != "testAndScenarioRunner"
        and not func.startswith("_")
    ]

if __name__ == "__main__":
    while True:
        choice = cli_menu()
        if choice == "1":
            preliminary_tests.testAndScenarioRunner()
        elif choice == "2":
            tests = list_individual_tests()
            if not tests:
                print("No individual tests found.")
                continue
            print("Available individual tests:")
            for idx, test_name in enumerate(tests, 1):
                print(f"{idx}. {test_name}")
            test_choice = input("Select test to run (number): ").strip()
            try:
                test_idx = int(test_choice) - 1
                if 0 <= test_idx < len(tests):
                    test_func = getattr(preliminary_tests, tests[test_idx])
                    print(f"Running {tests[test_idx]}...\n")
                    test_func()
                else:
                    print("Invalid selection.")
            except Exception:
                print("Invalid input.")
        elif choice == "0":
            print("Exiting.")
            break
        else:
            print("Invalid choice. Please try again.")