##
# @file main.py
# @author Tom Rose
#
# @brief
#   Orchestrates the simulation of a privacy-preserving vehicle authentication protocol using One-Time Passwords (OTP), Zero-Knowledge 
#   Proofs (ZKP) and blockchain logging. Demonstrates both simulated and real workflows for ZoKrates-based ZKPs, blockchain 
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
    
    # Define menu actions as a dictionary
    menu_actions = {
        "1": entire_groups_tests_menu,
        "2": subgroups_tests_menu,
        "3": individual_tests_menu,
        "4": entire_groups_experiments_menu,
        "5": subgroups_experiments_menu,
        "6": individual_experiments_menu,
        "dbon": lambda: (preliminary_tests.set_debug_mode(True), print("Debug mode enabled.\n")),
        "dboff": lambda: (preliminary_tests.set_debug_mode(False), print("Debug mode disabled.\n")),
        "e": None  # Special handling for exit
    }
    
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
        
        # Process user choice using the dictionary
        if choice in menu_actions:
            if choice == "e":
                print("Exiting.")
                break
            else:
                action = menu_actions[choice]
                # If the action is a function, call it
                if callable(action):
                    action()
        else:
            print("Invalid choice. Please try again.")


##
# @brief Menu for entire groups of tests
##
def entire_groups_tests_menu():
    unused_print_sumo_data = True

    menu_actions = {
        "1": lambda: (preliminary_tests.set_debug_mode(False), preliminary_tests.testAndScenarioRunner()),
        "2": lambda: (preliminary_tests.set_debug_mode(True), preliminary_tests.testAndScenarioRunner(), preliminary_tests.set_debug_mode(False)),
        "3": progressPresentationSuite,
        "dbon": lambda: (preliminary_tests.set_debug_mode(True), print("Debug mode enabled.\n")),
        "dboff": lambda: (preliminary_tests.set_debug_mode(False), print("Debug mode disabled.\n")),
        "b": "back",
        "e": "exit"
    }

    while True:
        print("\n")
        print(row_of_stars)
        print("*** Entire Groups of Tests Menu ***")
        print(row_of_stars)
        print("\n")
        print("Select an option:")
        print("1 - Run all tests and scenarios with Debug Mode disabled")
        print("2 - Run all tests and scenarios with Debug Mode enabled")
        print("3 - Run Progress Presentation Suite")
        print("dbon - Enable Debug Mode")
        print("dboff - Disable Debug Mode")
        print("b - Back to Main Menu")
        print("e - Exit\n")
        choice = input("Enter your choice: ").strip().lower()
        if choice in menu_actions:
            action = menu_actions[choice]
            if action == "back":
                return
            elif action == "exit":
                print("Exiting.")
                exit()
            elif callable(action):
                action()
        else:
            print("Invalid choice. Please try again.")

##
# @brief Menu for subgroups of tests.
##
def subgroups_tests_menu():
    menu_actions = {
        "1": fully_simulated_tests,
        "2": zokrates_integration_tests,
        "3": sumo_and_traci_tests,
        "dbon": lambda: (preliminary_tests.set_debug_mode(True), print("Debug mode enabled.\n")),
        "dboff": lambda: (preliminary_tests.set_debug_mode(False), print("Debug mode disabled.\n")),
        "b": "back",
        "e": "exit"
    }
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
        if choice in menu_actions:
            action = menu_actions[choice]
            if action == "back":
                return
            elif action == "exit":
                print("Exiting.")
                exit()
            elif callable(action):
                action()
        else:
            print("Invalid choice. Please try again.")

##
# @brief Menu for individual tests.
##
def individual_tests_menu():
    menu_actions = {
        "1": preliminary_tests.test_VehicleRsuBasicInteraction_SimulatedZkp,
        "2": preliminary_tests.test_VehicleRsuBasicInteraction_SimulatedZkpAndBlockchain,
        "3": preliminary_tests.test_EndToEnd_SimulatedZkpAndBlockchain_Success,
        "4": preliminary_tests.test_EndToEnd_SimulatedZkpAndBlockchain_Failure,
        "5": preliminary_tests.test_PartialWorkflow_RealZokrates_UsingDummyCircuit,
        "6": preliminary_tests.test_PartialWorkflow_MultipleVehicles_Simulated,
        "7": preliminary_tests.test_EndToEnd_MultipleVehicles_Simulated,
        "8": preliminary_tests.test_PartialWorkflow_RealZokrates_MultipleVehicles_UsingDummyCircuit,
        "9": preliminary_tests.test_PartialWorkflow_RealZokratesSimulatedBlockchain_MultipleVehicles_UsingDummyCircuit,
        "10": lambda: setattr(preliminary_tests, "tested", preliminary_tests.test_sumo_connection_wrapper(preliminary_tests.tested, preliminary_tests.passed)[0]) or setattr(preliminary_tests, "passed", preliminary_tests.test_sumo_connection_wrapper(preliminary_tests.tested, preliminary_tests.passed)[1]),
        "11": preliminary_tests.test_Zokrates_BasicConnectionTest_UsingDummyCircuit,
        "12": lambda: preliminary_tests.test_DataTransfer_SumoAndTraCI_UsingSimpleNet(print_data=preliminary_tests.PRINT_DATA),
        "13": lambda: preliminary_tests.test_DataTransfer_SumoAndTraCI_UsingIntersection1Config(print_data=preliminary_tests.PRINT_DATA),
        "14": lambda: preliminary_tests.test_DataTransfer_SumoAndTraCI_UsingIntersection2Config(print_data=preliminary_tests.PRINT_DATA),
        "15": lambda: preliminary_tests.test_DataTransfer_SumoAndTraCI_UsingStraightaway1Config(print_data=preliminary_tests.PRINT_DATA),
        "16": lambda: preliminary_tests.test_DataTransfer_SumoAndTraCI_UsingStraightaway2Config(print_data=preliminary_tests.PRINT_DATA),
        "17": lambda: preliminary_tests.test_LiveManipulation_SumoAndTraCI_UsingStraightaway1Config(print_data=preliminary_tests.PRINT_DATA),
        "18": preliminary_tests.test_Zokrates_UsingVtoICircuit,
        "19": preliminary_tests.test_Zokrates_UsingAuthCircuit,
        "20": lambda: preliminary_tests.test_DataTransfer_SumoAndTraCI_SmallStepLength_UsingStraightaway1Config(print_data=preliminary_tests.PRINT_DATA),
        "21": lambda: preliminary_tests.test_LiveManipulation_SumoAndTraCI_SpawnCarsDynamically_UsingStraightaway5(print_data=preliminary_tests.PRINT_DATA),
        "22": lambda: preliminary_tests.test_LiveManipulation_SumoAndTraCI_RsuMessageWithDelay_UsingStraightaway6(print_data=preliminary_tests.PRINT_DATA),
        "dbon": lambda: (preliminary_tests.set_debug_mode(True), print("Debug mode enabled.\n")),
        "dboff": lambda: (preliminary_tests.set_debug_mode(False), print("Debug mode disabled.\n")),
        "b": "back",
        "e": "exit"
    }
    
    while True:
        print("\n*** Individual Tests Menu ***")
        print("1 - Run Vehicle - Rsu Basic Interaction; Simulated Zkp Test")
        print("2 - Run Vehicle - Rsu Basic Interaction; Simulated Zkp And Blockchain Test")
        print("3 - Run End - To - End; Simulated Zkp And Blockchain; Success Test")
        print("4 - Run End - To - End; Simulated Zkp And Blockchain; Failure Test")
        print("5 - Run Partial Workflow - Real Zokrates (using dummy.zok) Test")
        print("6 - Run Partial Workflow - Multiple Vehicles; Simulated Test")
        print("7 - Run End - To - End; Multiple Vehicles; Simulated Test")
        print("8 - Run Partial Workflow - Real Zokrates; Multiple Vehicles (using dummy.zok) Test")
        print("9 - Run Partial Workflow - Real Zokrates, Simulated Blockchain; Multiple Vehicles (using dummy.zok) Test")
        print("10 - Run SUMO Connection Tests (Basic Network + Configuration File)")
        print("11 - Run Zokrates Basic Connection (using dummy.zok) Test")
        print("12 - Run Data Transfer (using simple.net.xml) Test")
        print("13 - Run Data Transfer (using intersection1.sumocfg) Test")
        print("14 - Run Data Transfer (using intersection2.sumocfg) Test")
        print("15 - Run Data Transfer (using straightaway1.sumocfg) Test")
        print("16 - Run Data Transfer (using straightaway2.sumocfg) Test")
        print("17 - Run Live Manipulation (using straightaway1.sumocfg) Test")
        print("18 - Run Zokrates (using VtoI_test.zok) Test")
        print("19 - Run Zokrates (using auth.zok) Test")
        print("20 - Run Data Transfer; Small Step (using straightaway1.sumocfg) Test")
        print("21 - Run Dynamic Car Spawning (using straightaway5.sumocfg) Test")
        print("22 - Run RSU Message With Delay (using straightaway6.sumocfg) Test")
        print("dbon - Enable Debug Mode")
        print("dboff - Disable Debug Mode")
        print("b - Back to Main Menu")
        print("e - Exit\n")
        choice = input("Enter your choice: ").strip().lower()
        if choice in menu_actions:
            action = menu_actions[choice]
            if action == "back":
                return
            elif action == "exit":
                print("Exiting.")
                exit()
            elif callable(action):
                action()
        else:
            print("Invalid choice. Please try again.")

##
# @brief Menu for entire groups of experiments.
##
def entire_groups_experiments_menu():
    menu_actions = {
        "dbon": lambda: (preliminary_tests.set_debug_mode(True), print("Debug mode enabled.\n")),
        "dboff": lambda: (preliminary_tests.set_debug_mode(False), print("Debug mode disabled.\n")),
        "b": "back",
        "e": "exit"
    }
    while True:
        print("\n*** Entire Groups of Experiments Menu ***")
        print("Implementation pending")
        print("dbon - Enable Debug Mode")
        print("dboff - Disable Debug Mode")
        print("b - Back to Main Menu")
        print("e - Exit\n")
        choice = input("Enter your choice: ").strip().lower()
        if choice in menu_actions:
            action = menu_actions[choice]
            if action == "back":
                return
            elif action == "exit":
                print("Exiting.")
                exit()
            elif callable(action):
                action()
        else:
            print("Invalid choice. Please try again.")

##
# @brief Menu for subgroups of experiments.
##
def subgroups_experiments_menu():
    menu_actions = {
        "dbon": lambda: (preliminary_tests.set_debug_mode(True), print("Debug mode enabled.\n")),
        "dboff": lambda: (preliminary_tests.set_debug_mode(False), print("Debug mode disabled.\n")),
        "b": "back",
        "e": "exit"
    }
    while True:
        print("\n*** Subgroups of Experiments Menu ***")
        print("Implementation pending")
        print("dbon - Enable Debug Mode")
        print("dboff - Disable Debug Mode")
        print("b - Back to Main Menu")
        print("e - Exit\n")
        choice = input("Enter your choice: ").strip().lower()
        if choice in menu_actions:
            action = menu_actions[choice]
            if action == "back":
                return
            elif action == "exit":
                print("Exiting.")
                exit()
            elif callable(action):
                action()
        else:
            print("Invalid choice. Please try again.")

##
# @brief Menu for individual experiments.
##
def individual_experiments_menu():
    menu_actions = {
        "dbon": lambda: (preliminary_tests.set_debug_mode(True), print("Debug mode enabled.\n")),
        "dboff": lambda: (preliminary_tests.set_debug_mode(False), print("Debug mode disabled.\n")),
        "b": "back",
        "e": "exit"
    }
    while True:
        print("\n*** Individual Experiments Menu ***")
        print("Implementation pending")
        print("dbon - Enable Debug Mode")
        print("dboff - Disable Debug Mode")
        print("b - Back to Main Menu")
        print("e - Exit\n")
        choice = input("Enter your choice: ").strip().lower()
        if choice in menu_actions:
            action = menu_actions[choice]
            if action == "back":
                return
            elif action == "exit":
                print("Exiting.")
                exit()
            elif callable(action):
                action()
        else:
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
    
    preliminary_tests.test_VehicleRsuBasicInteraction_SimulatedZkp()
    preliminary_tests.test_VehicleRsuBasicInteraction_SimulatedZkpAndBlockchain()
    preliminary_tests.test_EndToEnd_SimulatedZkpAndBlockchain_Success()
    preliminary_tests.test_EndToEnd_SimulatedZkpAndBlockchain_Failure()
    preliminary_tests.test_PartialWorkflow_MultipleVehicles_Simulated()
    preliminary_tests.test_EndToEnd_MultipleVehicles_Simulated()
                
                
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
    
    preliminary_tests.test_PartialWorkflow_RealZokrates_UsingDummyCircuit()
    preliminary_tests.test_PartialWorkflow_RealZokrates_MultipleVehicles_UsingDummyCircuit()
    preliminary_tests.test_PartialWorkflow_RealZokratesSimulatedBlockchain_MultipleVehicles_UsingDummyCircuit()
    preliminary_tests.test_Zokrates_BasicConnectionTest_UsingDummyCircuit()
    preliminary_tests.test_Zokrates_UsingVtoICircuit()
    preliminary_tests.test_Zokrates_UsingAuthCircuit()


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
    print("Run SUMO Dynamic Car Spawning Test (straightaway5.sumocfg)")
    print("Run SUMO RSU Message With Delay Test (straightaway5.sumocfg)")
    
    preliminary_tests.tested, preliminary_tests.passed = preliminary_tests.test_sumo_connection_wrapper(
        preliminary_tests.tested, preliminary_tests.passed
    )
    preliminary_tests.test_DataTransfer_SumoAndTraCI_UsingSimpleNet(print_data=print_sumo_data)
    preliminary_tests.test_DataTransfer_SumoAndTraCI_UsingIntersection1Config(print_data=print_sumo_data)
    preliminary_tests.test_DataTransfer_SumoAndTraCI_UsingIntersection2Config(print_data=print_sumo_data)
    preliminary_tests.test_DataTransfer_SumoAndTraCI_UsingStraightaway1Config(print_data=print_sumo_data)
    preliminary_tests.test_DataTransfer_SumoAndTraCI_UsingStraightaway2Config(print_data=print_sumo_data)
    preliminary_tests.test_LiveManipulation_SumoAndTraCI_UsingStraightaway1Config(print_data=print_sumo_data)
    preliminary_tests.test_DataTransfer_SumoAndTraCI_SmallStepLength_UsingStraightaway1Config(print_data=print_sumo_data)
    preliminary_tests.test_LiveManipulation_SumoAndTraCI_SpawnCarsDynamically_UsingStraightaway5(print_data=print_sumo_data)
    preliminary_tests.test_LiveManipulation_SumoAndTraCI_RsuMessageWithDelay_UsingStraightaway6(print_data=print_sumo_data)

    
def progressPresentationSuite():
    
    # Instead of initializing local counters, use the ones from preliminary_tests module
    # Get initial values to calculate the difference later
    initial_tested = preliminary_tests.tested
    initial_passed = preliminary_tests.passed

    # Run ZoKrates CLI Connection Test
    preliminary_tests.test_Zokrates_BasicConnectionTest_UsingDummyCircuit()
    time.sleep(.5)
    # clear_console()
    
    # Run Real ZoKrates End-to-End Test with dummy.zok
    preliminary_tests.test_PartialWorkflow_RealZokrates_UsingDummyCircuit()
    time.sleep(.5)
    # clear_console()

    # ZoKrates-Integrated Isolated Test: Multiple Vehicles
    preliminary_tests.test_PartialWorkflow_RealZokrates_MultipleVehicles_UsingDummyCircuit()
    time.sleep(.5)
    # clear_console()

    # ZoKrates-Integrated End-to-End Test: Multiple Vehicles
    preliminary_tests.test_PartialWorkflow_RealZokratesSimulatedBlockchain_MultipleVehicles_UsingDummyCircuit()
    time.sleep(.5)
    # clear_console()

    # Toggle PRINT_SUMO_DATA as needed
    # EX: test_sumo_traci_data_transfer(print_data=True)
    
    # Run SUMO TraCI Data Transfer Test (.sumocfg, 100 steps)
    preliminary_tests.test_DataTransfer_SumoAndTraCI_UsingIntersection1Config(True)
    time.sleep(.5)
    # clear_console()

    # Run SUMO TraCI Data Transfer Test (intersection2.sumocfg, explicit vehicles)
    preliminary_tests.test_DataTransfer_SumoAndTraCI_UsingIntersection2Config(True)
    time.sleep(.5)
    # clear_console()

    # Run SUMO TraCI Data Transfer Test (straightaway1.sumocfg)
    preliminary_tests.test_DataTransfer_SumoAndTraCI_UsingStraightaway1Config(True)
    time.sleep(.5)
    # clear_console()

    # Run SUMO TraCI Data Transfer Test (straightaway2.sumocfg)
    preliminary_tests.test_DataTransfer_SumoAndTraCI_UsingStraightaway2Config(True)
    time.sleep(.5)
    # clear_console()
    
    # Run SUMO Live Vehicle Manipulation Test (straightaway1.sumocfg)
    preliminary_tests.test_LiveManipulation_SumoAndTraCI_UsingStraightaway1Config(True)
    time.sleep(.5)
    # clear_console()

    # Run Vehicle-to-Infrastructure ZKP Test with the
    # zokrates/VtoI_test.zok circuit for vehicle-to-infrastructure authentication
    preliminary_tests.test_Zokrates_UsingVtoICircuit()
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


## Main entry point for the script
# If this script is run directly, start the main menu
if __name__ == "__main__":
    
    ## @brief Main entry point for running the protocol simulation tests.
    main_menu()
