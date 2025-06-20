"""
main.py

Purpose:
    Orchestrates the simulation of a privacy-preserving vehicle authentication protocol using Zero-Knowledge Proofs (ZKP) and blockchain logging.
    Demonstrates both a simulated and (optionally) real ZoKrates-based ZKP workflow, as well as a simulated blockchain verification and event logging.
"""

import preliminary_tests

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
