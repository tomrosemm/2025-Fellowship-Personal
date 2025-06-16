"""
main.py

Purpose:
    Orchestrates the simulation of a privacy-preserving vehicle authentication protocol using Zero-Knowledge Proofs (ZKP) and blockchain logging.
    Demonstrates both a simulated and (optionally) real ZoKrates-based ZKP workflow, as well as a simulated blockchain verification and event logging.
"""

from preliminary_tests import (
    test_vehicle_rsu_interaction_simulated,
    test_vehicle_rsu_blockchain_simulated,
    test_vehicle_rsu_interaction_real
)

if __name__ == "__main__":
    print()
    print("=== Simulated ZKP Test ===")
    test_vehicle_rsu_interaction_simulated()
    print("----------------------------------------------------------------------------")
    print()
    print("=== Simulated Blockchain ZKP Test ===")
    test_vehicle_rsu_blockchain_simulated()
    print("----------------------------------------------------------------------------")
    # Uncomment the next line to run the real ZoKrates workflow (requires ZoKrates and a valid circuit (.zok) file)
    # print("=== Real ZKP Test ===")
    # test_vehicle_rsu_interaction_real()
    # print("----------------------------------------------------------------------------")
