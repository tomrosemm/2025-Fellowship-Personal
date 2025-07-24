"""
main.py

Author: Tom Rose

Purpose:
    Orchestrates the simulation of a privacy-preserving vehicle authentication protocol using Zero-Knowledge Proofs (ZKP) and blockchain logging.
    Demonstrates both a simulated and (eventually) real ZoKrates-based ZKP workflow, as well as simulated and (eventually) real blockchain 
    verification and event logging.
"""

import preliminary_tests


def cli_menu_loop():
    print_sumo_data = True  # Local flag for menu session

    while True:
        
        print("\n*********************************************************************")
        print("*** Privacy-Preserving Vehicle Authentication Protocol Simulation ***")
        print("*********************************************************************\n")
        print("Select an option:")
        print("1 - Run all tests and scenarios with Debug Mode disabled")
        print("2 - Run all tests and scenarios with Debug Mode enabled")
        print("3 - Run Simulated ZKP Test")
        print("4 - Run Simulated Blockchain ZKP Test")
        print("5 - Run Simulated End-to-End Scenario: Successful Authentication")
        print("6 - Run Simulated End-to-End Scenario: Failed Authentication")
        print("7 - Run Real ZoKrates End-to-End Test with dummy.zok")
        print("8 - Simulated ZKP Isolated Test: Multiple Vehicles")
        print("9 - Simulated End-to-End Test: Multiple Vehicles")
        print("10 - ZoKrates-Integrated Isolated Test: Multiple Vehicles")
        print("11 - ZoKrates-Integrated End-to-End Test: Multiple Vehicles")
        print("12 - Run SUMO Connection Tests (Basic Network + Configuration File)")
        print("13 - Run ZoKrates CLI Connection Test")
        print("14 - Run SUMO TraCI Data Transfer Test")
        print("15 - Run SUMO TraCI Data Transfer Test (.sumocfg, 100 steps)")
        print("dbon - Enable Debug Mode")
        print("dboff - Disable Debug Mode")
        print("pdsumo - Print SUMO TraCI data ON")
        print("nosumo - Print SUMO TraCI data OFF")
        print("e - Exit\n")
        
        choice = input("Enter your choice: ").strip().lower()
        
        match choice:
            case "1":
                preliminary_tests.set_debug_mode(False)
                preliminary_tests.testAndScenarioRunner()
                
            case "2":
                preliminary_tests.set_debug_mode(True)
                preliminary_tests.testAndScenarioRunner()
                preliminary_tests.set_debug_mode(False)
                
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
                preliminary_tests.tested, preliminary_tests.passed = preliminary_tests.test_sumo_connection_wrapper(
                    preliminary_tests.tested, preliminary_tests.passed
                )
                
            case "13":
                preliminary_tests.test_zokrates_connection()
                
            case "14":
                preliminary_tests.test_sumo_traci_data_transfer(print_data=print_sumo_data)
                
            case "15":
                preliminary_tests.test_sumo_traci_data_transfer_sumocfg(print_data=print_sumo_data)
                
            case "dbon":
                preliminary_tests.set_debug_mode(True)
                print("Debug mode enabled.\n")
                
            case "dboff":
                preliminary_tests.set_debug_mode(False)
                print("Debug mode disabled.\n")
                
            case "pdsumo":
                print_sumo_data = True
                preliminary_tests.set_print_sumo_data(True)
                print("SUMO TraCI data printing enabled.\n")
                
            case "nosumo":
                print_sumo_data = False
                preliminary_tests.set_print_sumo_data(False)
                print("SUMO TraCI data printing disabled.\n")
                
            case "e":
                print("Exiting.")
                break
            
            case _:
                print("Invalid choice. Please try again.")

if __name__ == "__main__":
    cli_menu_loop()
