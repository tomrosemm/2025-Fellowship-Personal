##
# @file main.py
# @author Tom Rose
#
# @brief
#   Orchestrates the simulation of a privacy-preserving vehicle authentication protocol using One-Time Passwords (OTP), Zero-Knowledge 
#   Proofs (ZKP) and blockchain logging. Demonstrates both simulated and (eventually) real workflows for ZoKrates-based ZKPs, blockchain 
#   verification and event logging, and SUMO integration for vehicle-RSU interactions.
##

## @note
# Could use hash table for menu options to avoid long match-case statements, not strictly needed atm

# Imports
import time

import preliminary_tests
import sumo_interface

from settings import (
    SUMO_PORT_BASIC,
    SUMO_PORT_CONFIG,
    SUMO_PORT_DATA
)


# Row of stars for menu formatting
##@var row_of_stars
row_of_stars = "*********************************************************************"

##
# @brief Top-level command-line interface menu for organizing protocol simulation tests and experiments.
#
# @details
#   Provides hierarchical navigation through:
#     1. Entire groups of tests
#     2. Subgroups of tests
#     3. Individual tests
#     4. Entire groups of experiments
#     5. Subgroups of experiments
#     6. Individual experiments
##
def main_menu():
    
    # Main loop for top-level CLI menu
    while True:
        
        # Print menu header
        print("\n")
        print(row_of_stars)
        print("*** Privacy-Preserving Vehicle Authentication Protocol Simulation ***")
        print("***                     Main Menu                                 ***")
        print(row_of_stars)
        print("\n")

        # Display main menu options
        print("Select a category:")
        print("1 - Entire groups of tests")
        print("2 - Subgroups of tests")
        print("3 - Individual tests")
        print("4 - Entire groups of experiments")
        print("5 - Subgroups of experiments")
        print("6 - Individual experiments")
        print("dbon - Enable Debug Mode")
        print("dboff - Disable Debug Mode")
        print("e - Exit\n")
        
        # Accept user input
        choice = input("Enter your choice: ").strip().lower()
        
        # Process user choice
        match choice:
            case "1":
                entire_groups_tests_menu()
            case "2":
                subgroups_tests_menu()
            case "3":
                individual_tests_menu()
            case "4":
                entire_groups_experiments_menu()
            case "5":
                subgroups_experiments_menu()
            case "6":
                individual_experiments_menu()
            case "dbon":
                ## @details
                # Enable debug mode for detailed output
                preliminary_tests.set_debug_mode(True)
                print("Debug mode enabled.\n")
            case "dboff":
                ## @details
                # Disable debug mode for less verbose output
                preliminary_tests.set_debug_mode(False)
                print("Debug mode disabled.\n")
            case "e":
                print("Exiting.")
                break
            case _:
                print("Invalid choice. Please try again.")


##
# @brief Menu for entire groups of tests
##
def entire_groups_tests_menu():
    
    # Local flag for menu session
    ##@var unused_print_sumo_data
    ##@brief Controls whether SUMO TraCI data is printed during tests.
    unused_print_sumo_data = True

    # Main loop for CLI menu
    while True:
        
        # Print menu header
        print("\n")
        print(row_of_stars)
        print("*** Entire Groups of Tests Menu ***")
        print(row_of_stars)
        print("\n")
        
        # Display menu options
        print("Select an option:")
        print("1 - Run all tests and scenarios with Debug Mode disabled")
        print("2 - Run all tests and scenarios with Debug Mode enabled")
        print("3 - Run Progress Presentation Suite")
        print("dbon - Enable Debug Mode")
        print("dboff - Disable Debug Mode")
        print("b - Back to Main Menu")
        print("e - Exit\n")
        
        # Accept user input, strip whitespace, and convert to lowercase
        choice = input("Enter your choice: ").strip().lower()
        
        # Process user choice with match-case
        match choice:
            
            case "1":
                ## @test Run all tests and scenarios with Debug Mode disabled
                preliminary_tests.set_debug_mode(False)
                preliminary_tests.testAndScenarioRunner()
                
            case "2":
                ## @test Run all tests and scenarios with Debug Mode enabled, then disable it again
                preliminary_tests.set_debug_mode(True)
                preliminary_tests.testAndScenarioRunner()
                preliminary_tests.set_debug_mode(False)
                
            case "3":
                ## @test Run Progress Presentation Suite
                progressPresentationSuite()
                
            case "dbon":
                ## @details
                # Enable debug mode for detailed output
                preliminary_tests.set_debug_mode(True)
                print("Debug mode enabled.\n")
                
            case "dboff":
                ## @details
                # Disable debug mode for less verbose output
                preliminary_tests.set_debug_mode(False)
                print("Debug mode disabled.\n")
                
            case "b":
                return
                
            case "e":
                ## @details
                # Exit the program
                print("Exiting.")
                exit()
            
            case _:
                ## @details
                # Handle invalid input
                print("Invalid choice. Please try again.")



##
# @brief Menu for subgroups of tests.
##
def subgroups_tests_menu():
    
    while True:
        print("\n*** Subgroups of Tests Menu ***")
        print("1 - Fully Simulated Tests")
        print("2 - Zokrates Integration Tests")
        print("3 - SUMO and TraCI Tests")
        print("dbon - Enable Debug Mode")
        print("dboff - Disable Debug Mode")
        print("b - Back to Main Menu")
        print("e - Exit\n")
        
        choice = input("Enter your choice: ").strip().lower()
        
        match choice:
            case "1":
                fully_simulated_tests()
                
            case "2":
                zokrates_integration_tests()
            
            case "3":
                sumo_and_traci_tests()
            
            case "dbon":
                ## @details
                # Enable debug mode for detailed output
                preliminary_tests.set_debug_mode(True)
                print("Debug mode enabled.\n")
                
            case "dboff":
                ## @details
                # Disable debug mode for less verbose output
                preliminary_tests.set_debug_mode(False)
                print("Debug mode disabled.\n")
                
            case "b":
                return
            case "e":
                print("Exiting.")
                exit()
            case _:
                print("Invalid choice. Please try again.")


##
# @brief Menu for individual tests.
##
def individual_tests_menu():
    
    while True:
        
        print("\n*** Individual Tests Menu ***")
        print("1 - Run Simulated ZKP Test")
        print("2 - Run Simulated Blockchain ZKP Test")
        print("3 - Run Simulated End-to-End Scenario: Successful Authentication")
        print("4 - Run Simulated End-to-End Scenario: Failed Authentication")
        print("5 - Run Real ZoKrates End-to-End Test with dummy.zok")
        print("6 - Simulated ZKP Isolated Test: Multiple Vehicles")
        print("7 - Simulated End-to-End Test: Multiple Vehicles")
        print("8 - ZoKrates-Integrated Isolated Test: Multiple Vehicles")
        print("9 - ZoKrates-Integrated End-to-End Test: Multiple Vehicles")
        print("10 - Run SUMO Connection Tests (Basic Network + Configuration File)")
        print("11 - Run ZoKrates CLI Connection Test")
        print("12 - Run SUMO TraCI Data Transfer Test")
        print("13 - Run SUMO TraCI Data Transfer Test (.sumocfg, 100 steps)")
        print("14 - Run SUMO TraCI Data Transfer Test (intersection2.sumocfg, explicit vehicles)")
        print("15 - Run SUMO TraCI Data Transfer Test (straightaway1.sumocfg)")
        print("16 - Run SUMO TraCI Data Transfer Test (straightaway2.sumocfg)")
        print("17 - Run SUMO Live Vehicle Manipulation Test (straightaway1.sumocfg)")
        print("18 - Run Vehicle-to-Infrastructure ZKP Test with zokrates/VtoI_test.zok")
        print("19 - Run Authentication Circuit Test with auth.zok")
        print("20 - Run SUMO Small Step Length Test (10ms steps)")
        print("dbon - Enable Debug Mode")
        print("dboff - Disable Debug Mode")
        print("b - Back to Main Menu")
        print("e - Exit\n")
        
        choice = input("Enter your choice: ").strip().lower()
        
        match choice:
            case "1":
                ## @test Run a single simulated ZKP experiment with zokrates/dummy.zok
                preliminary_tests.test_vehicle_rsu_interaction_simulated()
                
            case "2":
                ## @test Run a single simulated blockchain ZKP experiment with zokrates/dummy.zok
                preliminary_tests.test_vehicle_rsu_blockchain_simulated()
                
            case "3":
                ## @test Run a simulated end-to-end scenario with successful authentication
                preliminary_tests.scenario_successful_authentication()
                
            case "4":
                ## @test Run a simulated end-to-end scenario with failed authentication
                preliminary_tests.scenario_failed_authentication()
                
            case "5":
                ## @test Run a real ZoKrates end-to-end test with dummy.zok
                preliminary_tests.test_vehicle_rsu_interaction_real_zokrates_dummy()
                
            case "6":
                ## @test Run a simulated ZKP isolated test with multiple vehicles
                preliminary_tests.test_simulated_isolated_multiple_vehicles()
                
            case "7":
                ## @test Run a simulated end-to-end test with multiple vehicles
                preliminary_tests.test_simulated_end_to_end_multiple_vehicles()
                
            case "8":
                ## @test Run a ZoKrates-integrated isolated test with multiple vehicles using zokrates/dummy.zok
                preliminary_tests.test_zokrates_isolated_multiple_vehicles()
                
            case "9":
                ## @test Run a ZoKrates-integrated end-to-end test with multiple vehicles using zokrates/dummy.zok
                preliminary_tests.test_zokrates_end_to_end_multiple_vehicles()
                
            case "10":
                ## @test Run SUMO connection tests (basic network + configuration file)
                preliminary_tests.tested, preliminary_tests.passed = preliminary_tests.test_sumo_connection_wrapper(
                    preliminary_tests.tested, preliminary_tests.passed
                )
                
            case "11":
                ## @test Run ZoKrates CLI connection test with zokrates/dummy.zok
                preliminary_tests.test_zokrates_connection()
                
            case "12":
                ## @test Run SUMO TraCI data transfer test with sumo/Intersection 1/intersection1.sumocfg
                preliminary_tests.test_sumo_traci_data_transfer(print_data=preliminary_tests.PRINT_DATA)
                
            case "13":
                ## @test Run SUMO TraCI data transfer test with sumo/Intersection 1/intersection1.sumocfg for 100 steps
                preliminary_tests.test_sumo_traci_data_transfer_sumocfg(print_data=preliminary_tests.PRINT_DATA)
                
            case "14":
                ## @test Run SUMO TraCI data transfer test with sumo/Intersection 2/intersection2.sumocfg with explicit vehicles
                preliminary_tests.test_sumo_traci_data_transfer_intersection2(print_data=preliminary_tests.PRINT_DATA)
                
            case "15":
                ## @test Run SUMO TraCI data transfer test with sumo/StraightAway1/straightaway1.sumocfg
                preliminary_tests.test_sumo_traci_data_transfer_straightaway1(print_data=preliminary_tests.PRINT_DATA)
                
            case "16":
                ## @test Run SUMO TraCI data transfer test with sumo/StraightAway2/straightaway2.sumocfg
                preliminary_tests.test_sumo_traci_data_transfer_straightaway2(print_data=preliminary_tests.PRINT_DATA)
                
            case "17":
                ## @test Run SUMO Live Vehicle Manipulation Test with sumo/StraightAway1/straightaway1.sumocfg
                preliminary_tests.test_sumo_live_manipulation_straightaway1(print_data=preliminary_tests.PRINT_DATA)
        
            case "18":
                ## @test Run Vehicle-to-Infrastructure ZKP Test with zokrates/VtoI_test.zok
                preliminary_tests.test_vehicle_to_infrastructure_VtoI_zkp()
                
            case "19":
                ## @test Run Authentication Circuit Test with auth.zok
                preliminary_tests.test_authentication_circuit_auth_zok()
            
            case "20":
                ## @test Run SUMO with small step length of 10ms
                preliminary_tests.test_sumo_small_step_length_straightaway1(
                    print_data=preliminary_tests.PRINT_DATA
                )
            
            case "dbon":
                ## @details
                # Enable debug mode for detailed output
                preliminary_tests.set_debug_mode(True)
                print("Debug mode enabled.\n")
                
            case "dboff":
                ## @details
                # Disable debug mode for less verbose output
                preliminary_tests.set_debug_mode(False)
                print("Debug mode disabled.\n")
                
            case "b":
                return
            case "e":
                print("Exiting.")
                exit()
            case _:
                print("Invalid choice. Please try again.")


##
# @brief Menu for entire groups of experiments.
##
def entire_groups_experiments_menu():
    
    while True:
        
        print("\n*** Entire Groups of Experiments Menu ***")
        print("Implementation pending")
        print("dbon - Enable Debug Mode")
        print("dboff - Disable Debug Mode")
        print("b - Back to Main Menu")
        print("e - Exit\n")
        
        choice = input("Enter your choice: ").strip().lower()
        
        match choice:
            case "dbon":
                ## @details
                # Enable debug mode for detailed output
                preliminary_tests.set_debug_mode(True)
                print("Debug mode enabled.\n")
                
            case "dboff":
                ## @details
                # Disable debug mode for less verbose output
                preliminary_tests.set_debug_mode(False)
                print("Debug mode disabled.\n")
            case "b":
                return
            case "e":
                print("Exiting.")
                exit()
            case _:
                print("Invalid choice. Please try again.")


##
# @brief Menu for subgroups of experiments.
##
def subgroups_experiments_menu():
    
    while True:
        
        print("\n*** Subgroups of Experiments Menu ***")
        print("Implementation pending")
        print("dbon - Enable Debug Mode")
        print("dboff - Disable Debug Mode")
        print("b - Back to Main Menu")
        print("e - Exit\n")
        
        choice = input("Enter your choice: ").strip().lower()
        
        match choice:
            case "dbon":
                ## @details
                # Enable debug mode for detailed output
                preliminary_tests.set_debug_mode(True)
                print("Debug mode enabled.\n")
                
            case "dboff":
                ## @details
                # Disable debug mode for less verbose output
                preliminary_tests.set_debug_mode(False)
                print("Debug mode disabled.\n")
            case "b":
                return
            case "e":
                print("Exiting.")
                exit()
            case _:
                print("Invalid choice. Please try again.")


##
# @brief Menu for individual experiments.
##
def individual_experiments_menu():
    
    while True:
        
        print("\n*** Individual Experiments Menu ***")
        print("Implementation pending")
        print("dbon - Enable Debug Mode")
        print("dboff - Disable Debug Mode")
        print("b - Back to Main Menu")
        print("e - Exit\n")
        
        choice = input("Enter your choice: ").strip().lower()
        
        match choice:
            case "dbon":
                ## @details
                # Enable debug mode for detailed output
                preliminary_tests.set_debug_mode(True)
                print("Debug mode enabled.\n")
                
            case "dboff":
                ## @details
                # Disable debug mode for less verbose output
                preliminary_tests.set_debug_mode(False)
                print("Debug mode disabled.\n")
            case "b":
                return
            case "e":
                print("Exiting.")
                exit()
            case _:
                print("Invalid choice. Please try again.")


## Test SubGroups
def fully_simulated_tests():
    
    # Print menu header
    print("\n")
    print(row_of_stars)
    print("*** Fully Simulated Tests ***")
    print(row_of_stars)
    print("\n")
    
    print("Simulated ZKP Test")
    print("Simulated Blockchain ZKP Test")
    print("Simulated End-to-End Scenario: Successful Authentication")
    print("Simulated End-to-End Scenario: Failed Authentication")
    print("Simulated ZKP Isolated Test: Multiple Vehicles")
    print("Simulated End-to-End Test: Multiple Vehicles")
    
    preliminary_tests.test_vehicle_rsu_interaction_simulated()
    preliminary_tests.test_vehicle_rsu_blockchain_simulated()
    preliminary_tests.scenario_successful_authentication()
    preliminary_tests.scenario_failed_authentication()
    preliminary_tests.test_simulated_isolated_multiple_vehicles()
    preliminary_tests.test_simulated_end_to_end_multiple_vehicles()
                
                
def zokrates_integration_tests():
    
    # Print menu header
    print("\n")
    print(row_of_stars)
    print("*** Zokrates Integration Tests ***")
    print(row_of_stars)
    print("\n")
    
    print("Run Real ZoKrates End-to-End Test with dummy.zok")
    print("ZoKrates-Integrated Isolated Test: Multiple Vehicles")
    print("ZoKrates-Integrated End-to-End Test: Multiple Vehicles")
    print("Run ZoKrates CLI Connection Test")
    print("Run Vehicle-to-Infrastructure ZKP Test with VtoI_test.zok")
    print("Run Authentication Circuit Test with auth.zok")
    
    preliminary_tests.test_vehicle_rsu_interaction_real_zokrates_dummy()
    preliminary_tests.test_zokrates_isolated_multiple_vehicles()
    preliminary_tests.test_zokrates_end_to_end_multiple_vehicles()
    preliminary_tests.test_zokrates_connection()
    preliminary_tests.test_vehicle_to_infrastructure_VtoI_zkp()
    preliminary_tests.test_authentication_circuit_auth_zok()


def sumo_and_traci_tests(print_sumo_data=True):
    
    # Print menu header
    print("\n")
    print(row_of_stars)
    print("*** SUMO and TraCI Integration Tests ***")
    print(row_of_stars)
    print("\n")
    
    print("Run SUMO Connection Tests (Basic Network + Configuration File)")
    print("Run SUMO TraCI Data Transfer Test (simple.net)")
    print("Run SUMO TraCI Data Transfer Test (.sumocfg, 100 steps)")
    print("Run SUMO TraCI Data Transfer Test (intersection2.sumocfg, explicit vehicles)")
    print("Run SUMO TraCI Data Transfer Test (straightaway1.sumocfg)")
    print("Run SUMO TraCI Data Transfer Test (straightaway2.sumocfg)")
    print("Run SUMO Live Vehicle Manipulation Test (straightaway1.sumocfg)")
    print("Run SUMO Small Step Length Test (10ms steps)")
    
    preliminary_tests.tested, preliminary_tests.passed = preliminary_tests.test_sumo_connection_wrapper(
        preliminary_tests.tested, preliminary_tests.passed
    )
    preliminary_tests.test_sumo_traci_data_transfer(print_data=print_sumo_data)
    preliminary_tests.test_sumo_traci_data_transfer_sumocfg(print_data=print_sumo_data)
    preliminary_tests.test_sumo_traci_data_transfer_intersection2(print_data=print_sumo_data)
    preliminary_tests.test_sumo_traci_data_transfer_straightaway1(print_data=print_sumo_data)
    preliminary_tests.test_sumo_traci_data_transfer_straightaway2(print_data=print_sumo_data)
    preliminary_tests.test_sumo_live_manipulation_straightaway1(print_data=print_sumo_data)
    preliminary_tests.test_sumo_small_step_length_straightaway1(print_data=print_sumo_data)
    
    
def progressPresentationSuite():
    
    # Instead of initializing local counters, use the ones from preliminary_tests module
    # Get initial values to calculate the difference later
    initial_tested = preliminary_tests.tested
    initial_passed = preliminary_tests.passed

    # Run ZoKrates CLI Connection Test
    preliminary_tests.test_zokrates_connection()
    time.sleep(.5)
    # clear_console()
    
    # Run Real ZoKrates End-to-End Test with dummy.zok
    preliminary_tests.test_vehicle_rsu_interaction_real_zokrates_dummy()
    time.sleep(.5)
    # clear_console()

    # ZoKrates-Integrated Isolated Test: Multiple Vehicles
    preliminary_tests.test_zokrates_isolated_multiple_vehicles()
    time.sleep(.5)
    # clear_console()

    # ZoKrates-Integrated End-to-End Test: Multiple Vehicles
    preliminary_tests.test_zokrates_end_to_end_multiple_vehicles()
    time.sleep(.5)
    # clear_console()

    # Toggle PRINT_SUMO_DATA as needed
    # EX: test_sumo_traci_data_transfer(print_data=True)
    
    # Run SUMO TraCI Data Transfer Test (.sumocfg, 100 steps)
    preliminary_tests.test_sumo_traci_data_transfer_sumocfg(True)
    time.sleep(.5)
    # clear_console()

    # Run SUMO TraCI Data Transfer Test (intersection2.sumocfg, explicit vehicles)
    preliminary_tests.test_sumo_traci_data_transfer_intersection2(True)
    time.sleep(.5)
    # clear_console()

    # Run SUMO TraCI Data Transfer Test (straightaway1.sumocfg)
    preliminary_tests.test_sumo_traci_data_transfer_straightaway1(True)
    time.sleep(.5)
    # clear_console()

    # Run SUMO TraCI Data Transfer Test (straightaway2.sumocfg)
    preliminary_tests.test_sumo_traci_data_transfer_straightaway2(True)
    time.sleep(.5)
    # clear_console()
    
    # Run SUMO Live Vehicle Manipulation Test (straightaway1.sumocfg)
    preliminary_tests.test_sumo_live_manipulation_straightaway1(True)
    time.sleep(.5)
    # clear_console()

    # Run Vehicle-to-Infrastructure ZKP Test with the
    # zokrates/VtoI_test.zok circuit for vehicle-to-infrastructure authentication
    preliminary_tests.test_vehicle_to_infrastructure_VtoI_zkp()
    time.sleep(.5)
    # clear_console()

    # SUMO cleanup after connection tests
    sumo_interface.cleanup_traci_connection()
    sumo_interface.kill_processes_on_port(SUMO_PORT_BASIC)
    sumo_interface.kill_processes_on_port(SUMO_PORT_CONFIG)
    sumo_interface.kill_processes_on_port(SUMO_PORT_DATA)
    time.sleep(2)

    # Calculate tests run and passed during this suite
    tests_run = preliminary_tests.tested - initial_tested
    tests_passed = preliminary_tests.passed - initial_passed
    
    print(f"\nProgress Presentation Suite Results:")
    print(f"Tests run: {tests_run}")
    print(f"Tests passed: {tests_passed}")
    print(f"Tests failed: {tests_run - tests_passed}")
    print()
    time.sleep(2)


##
# @brief Legacy function for backward compatibility.
# @deprecated Use main_menu() instead.
##
# def cli_menu_loop():
#     """Legacy function - redirects to main menu."""
#     main_menu()


## Main entry point for the script
# If this script is run directly, start the main menu
if __name__ == "__main__":
    
    ## @brief Main entry point for running the protocol simulation tests.
    main_menu()
