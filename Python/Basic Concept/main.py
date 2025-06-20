"""
main.py

Purpose:
    Orchestrates the simulation of a privacy-preserving vehicle authentication protocol using Zero-Knowledge Proofs (ZKP) and blockchain logging.
    Demonstrates both a simulated and (optionally) real ZoKrates-based ZKP workflow, as well as a simulated blockchain verification and event logging.
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


if __name__ == "__main__":
    
    print()
    print("=== Simulated ZKP Test ===")
    preliminary_tests.test_vehicle_rsu_interaction_simulated()
    print("----------------------------------------------------------------------------")
    
    print()
    print("=== Simulated Blockchain ZKP Test ===")
    preliminary_tests.test_vehicle_rsu_blockchain_simulated()
    print("----------------------------------------------------------------------------")
    
    # Uncomment the next line to run the real ZoKrates workflow (requires ZoKrates and a valid circuit (.zok) file)
    # print()
    # print("=== Real ZKP Test ===")
    # preliminary_tests.test_vehicle_rsu_interaction_real()
    # print("----------------------------------------------------------------------------")
    
    print()
    print("=== End-to-End Scenario: Successful Authentication ===")
    preliminary_tests.scenario_successful_authentication()
    print("----------------------------------------------------------------------------")
    
    print()
    print("=== End-to-End Scenario: Failed Authentication ===")
    preliminary_tests.scenario_failed_authentication()
    print("----------------------------------------------------------------------------")
    
    print()
    print(f"Total tests run: {preliminary_tests.tested}")
    print(f"Total tests passed: {preliminary_tests.passed}")
    print(f"Total tests failed: {preliminary_tests.tested - preliminary_tests.passed}")
    print()
