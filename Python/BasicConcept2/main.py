##
# @file main.py
# @author Tom Rose
#
# @brief
#   Orchestrates the simulation of a privacy-preserving vehicle authentication protocol using One-Time Passwords (OTP), Zero-Knowledge 
#   Proofs (ZKP) and blockchain logging. Demonstrates both simulated and (eventually) real workflows for ZoKrates-based ZKPs, blockchain 
#   verification and event logging, and SUMO integration for vehicle-RSU interactions.
##

# Imports
import preliminary_tests


##
# @brief Command-line interface menu loop for running protocol simulation tests.
#
# @details
#   Steps:
#     1. Display menu options.
#     2. Accept user input.
#     3. Execute the appropriate test/scenario functions based on input.
#     4. Allow toggling debug mode and SUMO data printing.
#     5. Exit on user request.
##
def cli_menu_loop():
    
    # Local flag for menu session
    ##@var print_sumo_data
    ##@brief Controls whether SUMO TraCI data is printed during tests.
    print_sumo_data = True
    
    # Row of stars for menu formatting
    ##@var row_of_stars
    row_of_stars = "*********************************************************************"

    # Print menu header
    print("\n")
    print(row_of_stars)
    print("*** Privacy-Preserving Vehicle Authentication Protocol Simulation ***")
    print(row_of_stars)
    print("\n")

    # Main loop for CLI menu
    ## @var choice
    ## @brief User's menu choice input.
    while True:
        
        # Display menu options
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
        print("15b - Run SUMO TraCI Data Transfer Test (intersection2.sumocfg, explicit vehicles)")
        print("15c - Run SUMO TraCI Data Transfer Test (straightaway1.sumocfg)")
        print("15d - Run SUMO TraCI Data Transfer Test (straightaway2.sumocfg)")
        print("16 - Run Vehicle-to-Infrastructure ZKP Test with zokrates/VtoI_test.zok")
        print("dbon - Enable Debug Mode")
        print("dboff - Disable Debug Mode")
        
        ## @todo
        # Fix implementation
        # print("pdsumo - Print SUMO TraCI data ON")
        # print("ndsumo - Print SUMO TraCI data OFF")
        
        print("e - Exit\n")
        
        # Accept user input, strip whitespace, and convert to lowercase
        ## @var choice
        # @brief User's choice input for menu options.
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
                ## @test Run a single simulated ZKP experiment with zokrates/dummy.zok
                preliminary_tests.test_vehicle_rsu_interaction_simulated()
                
            case "4":
                ## @test Run a single simulated blockchain ZKP experiment with zokrates/dummy.zok
                preliminary_tests.test_vehicle_rsu_blockchain_simulated()
                
            case "5":
                ## @test Run a simulated end-to-end scenario with successful authentication
                preliminary_tests.scenario_successful_authentication()
                
            case "6":
                ## @test Run a simulated end-to-end scenario with failed authentication
                preliminary_tests.scenario_failed_authentication()
                
            case "7":
                ## @test Run a real ZoKrates end-to-end test with dummy.zok
                preliminary_tests.test_vehicle_rsu_interaction_real_zokrates_dummy()
                
            case "8":
                ## @test Run a simulated ZKP isolated test with multiple vehicles
                preliminary_tests.test_simulated_isolated_multiple_vehicles()
                
            case "9":
                ## @test Run a simulated end-to-end test with multiple vehicles
                preliminary_tests.test_simulated_end_to_end_multiple_vehicles()
                
            case "10":
                ## @test Run a ZoKrates-integrated isolated test with multiple vehicles using zokrates/dummy.zok
                preliminary_tests.test_zokrates_isolated_multiple_vehicles()
                
            case "11":
                ## @test Run a ZoKrates-integrated end-to-end test with multiple vehicles using zokrates/dummy.zok
                preliminary_tests.test_zokrates_end_to_end_multiple_vehicles()
                
            case "12":
                ## @test Run SUMO connection tests (basic network + configuration file)
                preliminary_tests.tested, preliminary_tests.passed = preliminary_tests.test_sumo_connection_wrapper(
                    preliminary_tests.tested, preliminary_tests.passed
                )
                
            case "13":
                ## @test Run ZoKrates CLI connection test with zokrates/dummy.zok
                preliminary_tests.test_zokrates_connection()
                
            case "14":
                ## @test Run SUMO TraCI data transfer test with sumo/Intersection 1/intersection1.sumocfg
                preliminary_tests.test_sumo_traci_data_transfer(print_data=print_sumo_data)
                
            case "15":
                ## @test Run SUMO TraCI data transfer test with sumo/Intersection 1/intersection1.sumocfg for 100 steps
                preliminary_tests.test_sumo_traci_data_transfer_sumocfg(print_data=print_sumo_data)
                
            case "15b":
                ## @test Run SUMO TraCI data transfer test with sumo/Intersection 2/intersection2.sumocfg with explicit vehicles
                preliminary_tests.test_sumo_traci_data_transfer_intersection2(print_data=print_sumo_data)
                
            case "15c":
                ## @test Run SUMO TraCI data transfer test with sumo/StraightAway1/straightaway1.sumocfg
                preliminary_tests.test_sumo_traci_data_transfer_straightaway1(print_data=print_sumo_data)
                
            case "15d":
                ## @test Run SUMO TraCI data transfer test with sumo/StraightAway2/straightaway2.sumocfg
                preliminary_tests.test_sumo_traci_data_transfer_straightaway2(print_data=print_sumo_data)
        
            case "16":
                ## @test Run Vehicle-to-Infrastructure ZKP Test with zokrates/VtoI_test.zok
                preliminary_tests.test_vehicle_to_infrastructure_VtoI_zkp()
                
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
                
            # case "pdsumo":
            #     ## @details
            #     # Enable printing of SUMO TraCI data during tests
            #     print_sumo_data = True
            #     preliminary_tests.set_print_sumo_data(True)
            #     print("SUMO TraCI data printing enabled.\n")
                
            # case "ndsumo":
            #     ## @details
            #     # Disable printing of SUMO TraCI data during tests
            #     print_sumo_data = False
            #     preliminary_tests.set_print_sumo_data(False)
            #     print("SUMO TraCI data printing disabled.\n")
                
            case "e":
                ## @details
                # Exit the CLI menu loop
                print("Exiting.")
                break
            
            case _:
                ## @details
                # Handle invalid input
                print("Invalid choice. Please try again.")


## Main entry point for the script
# If this script is run directly, start the CLI menu loop
if __name__ == "__main__":
    
    ## @brief Main entry point for running the protocol simulation tests.
    cli_menu_loop()
