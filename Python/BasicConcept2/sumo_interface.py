##
# @file sumo_interface.py
# @author Tom Rose
#
# @brief
#   Provides utility functions for managing SUMO simulation processes and TraCI connections
#   Includes port cleanup, connection testing, configuration file handling, and data transfer routines
#   for integration with SUMO in automated testing and simulation workflows
#
# @details
#   - Cleans up processes using specific ports to avoid conflicts
#   - Checks and waits for port availability before launching SUMO
#   - Starts SUMO with network or configuration files and connects via TraCI
#   - Supports aggressive cleanup and diagnostics for robust automated testing
#   - Handles temporary configuration file creation and output management
##

## Imports
# Libraries
import sys
import subprocess
import os
import time
import xml.etree.ElementTree as ET
import tempfile
import shutil

# Classes and Functions
from settings import (
    DEBUG_MODE as DEFAULT_DEBUG_MODE,
    SUMO_TOOLS_PATH,
    SUMO_SIMPLE_NET_FILE,
    SUMO_CITY_CONFIG_FILE,
    SUMO_PORT_BASIC,
    SUMO_PORT_CONFIG
)

from utilities import (
    # is_port_available,
    kill_processes_on_port,
    wait_for_port_available
)


## Unused, Leftover Functions
# ##
# # @brief Start SUMO and connect via TraCI
# # @param sumo_cmd SUMO command list
# # @param port Port to use for TraCI connection
# # @param sumo_tools_path Path to SUMO tools directory
# # @return tuple (proc, traci_module) - SUMO process and TraCI module
# #
# # @details
# #   Steps:
# #     1. Add SUMO tools to path
# #     2. Import TraCI
# #     3. Start SUMO process
# #     4. Connect via TraCI
# #     5. Return process and TraCI module
# ##
# def start_sumo_and_traci(sumo_cmd, port, sumo_tools_path):
#     sys.path.append(sumo_tools_path)
#     try:
#         import traci
#     except ImportError:
#         print("[SUMO TraCI Test] Could not import traci. Check SUMO_TOOLS_PATH.")
#         return None, None
#     proc = subprocess.Popen(sumo_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#     time.sleep(3)
#     if proc.poll() is not None:
#         stderr = proc.stderr.read().decode()
#         print(f"[SUMO TraCI Test] SUMO exited early. STDERR:\n{stderr}")
#         return None, None
#     traci.init(port=port)
#     time.sleep(1)
#     return proc, traci


## @var DEBUG_MODE
## @brief Global variable to control debug output
DEBUG_MODE = DEFAULT_DEBUG_MODE


##
# @brief Enable or disable debug mode for detailed output
#
# @param enabled True to enable debug mode, False to disable
#
# @details
#   Steps:
#     1. Set the global DEBUG_MODE variable to the provided value
##
def set_debug_mode(enabled):
    
    # Set the global DEBUG_MODE variable
    global DEBUG_MODE
    DEBUG_MODE = enabled


##
# @brief Test the connection to SUMO using TraCI
#
# @return True if connection succeeded, False otherwise
#
# @details
#   Steps:
#     1. Aggressively clean up port and connections
#     2. Start SUMO with network file
#     3. Attempt to connect via TraCI
#     4. Clean up after test
##
def test_sumo_connection():
    
    # Aggressive cleanup before starting test
    kill_processes_on_port(SUMO_PORT_BASIC)
    cleanup_traci_connection()
    
    # Wait for port to be available
    print("Wait time begins for processes to die and OS to release port")
    time.sleep(10) 
    print("Wait time ends for processes to die and OS to release port")

    # Clean up any existing connections first
    cleanup_traci_connection()
    
    # port - Define the port to use for SUMO connection
    port = SUMO_PORT_BASIC
    
    # If port is not available, wait for it to become available until timeout
    if not wait_for_port_available(port, timeout=15):
        
        # If port is not available, print failure info and return False
        print(f"[SUMO Test] Port {port} is not available after waiting and cleanup attempts.")
        return False
    
    # Get SUMO tools path from settings
    sys.path.append(SUMO_TOOLS_PATH)

    # Try to import traci and handle import errors
    try:
        
        import traci
    
    # If traci import fails, print debug info and return False
    except ImportError as e:
        
        if DEBUG_MODE:
            print(f"[SUMO Test] Could not import traci: {e}")
            print(f"Check that SUMO_TOOLS_PATH is correct: {SUMO_TOOLS_PATH}")
            
        return False

    # Define the path to the SUMO network file from settings
    SUMO_NET_FILE = SUMO_SIMPLE_NET_FILE
    
    # Check if the SUMO network file exists
    if not os.path.exists(SUMO_NET_FILE):
        
        # If network file does not exist, print debug info and return False
        print(f"[SUMO Test] Network file not found: {SUMO_NET_FILE}")
        return False

    # Start the SUMO process with the network file
    proc, sumo_binary, net_file = start_sumo()
    
    # If the process could not be started, print debug info and return False
    if not proc:
        
        print("[SUMO Test] Could not start SUMO process.")
        return False
    
    # connected - Initialize connection status
    connected = False
    
    # Try to connect to SUMO via TraCI
    try:
        
        time.sleep(2)
        
        # Initialize TraCI connection to SUMO using the specified port, setting connected to true if successful
        traci.init(port=port)
        connected = True
        
        # If debug mode is enabled, print connection info
        if DEBUG_MODE:
            print("[SUMO Test] Successfully connected to SUMO via traci!")
            print(f"SUMO binary used: {sumo_binary}")
            print(f"Network file: {net_file}")
            print(f"SUMO process PID: {proc.pid}")
            print("SUMO process started and connection established.")
    
    # If TraCI connection fails, print debug info if DEBUG_MODE is enabled and return False
    except Exception as e:
        
        if DEBUG_MODE:
            print(f"[SUMO Test] Failed to connect to SUMO: {e}")

    # Finally block to ensure cleanup after the test regardless of success or failure
    finally:
        
        # Try to close the TraCI connection if it is loaded
        try:
            
            # If TraCI is loaded, close the connection
            if traci.isLoaded():
                traci.close()
                
                # If debug mode is enabled, print debug info
                if DEBUG_MODE:
                    print("SUMO TraCI connection closed.")
        
        # If closing TraCI fails, print debug info if Debug mode is enabled
        except Exception as e:
            
            if DEBUG_MODE:
                print(f"TraCI close error: {e}")
        
        # Try to terminate the SUMO process
        try:
            
            # Terminate the SUMO process and wait for it to finish with a timeout of 3 seconds
            proc.terminate()
            proc.wait(timeout=3)
            
            # If debug mode is enabled, print debug info
            if DEBUG_MODE:
                print("  SUMO process terminated.")
        
        # If terminating SUMO fails, try to kill the process
        except subprocess.TimeoutExpired:
            
            proc.kill()
            
            # If debug mode is enabled, print debug info
            if DEBUG_MODE:
                print("  SUMO process killed (timeout).")
        
        # If killing the process fails, print debug info if Debug mode is enabled
        except Exception as e:
            
            if DEBUG_MODE:
                print(f"  SUMO process termination error: {e}")
        
        # Force cleanup
        kill_processes_on_port(port)
        
        time.sleep(2)
    
    return connected


##
# @brief Test the connection to SUMO using a .sumocfg configuration file
#
# @return True if connection succeeded, False otherwise
#
# @details
#   Steps:
#     1. Aggressively clean up port and connections
#     2. Start SUMO with config file
#     3. Attempt to connect via TraCI
#     4. Clean up after test
##
def test_sumo_config_connection():
    
    # Aggressive cleanup before starting test
    kill_processes_on_port(SUMO_PORT_CONFIG)
    
    # Wait for port to be available
    print("Wait time begins for processes to die and OS to release port")
    time.sleep(10) 
    print("Wait time ends for processes to die and OS to release port")
    
    # Clean up any existing connections first
    cleanup_traci_connection()
    
    # port - Define the port to use for SUMO connection
    port = SUMO_PORT_CONFIG
    
    # If port is not available, wait for it to become available until timeout
    if not wait_for_port_available(port, timeout=15):
        
        # If port is not available and timeout expires, print failure info and return False
        print(f"[SUMO Config Test] Port {port} is not available after waiting and cleanup attempts.")
        return False
    
    # Get SUMO tools path from settings
    sys.path.append(SUMO_TOOLS_PATH)

    # Try to import traci
    try:
        
        import traci
    
    # If traci import fails, print debug info if DEBUG_MODE is enabled and return False
    except ImportError as e:
        
        if DEBUG_MODE:
            print(f"[SUMO Config Test] Could not import traci: {e}")
            print(f"Check that SUMO_TOOLS_PATH is correct: {SUMO_TOOLS_PATH}")
            
        return False

    # Define the path to the SUMO configuration file from settings
    SUMO_CONFIG_FILE = SUMO_CITY_CONFIG_FILE
    
    # Check if the SUMO configuration file exists; if not, print debug info and return False
    if not os.path.exists(SUMO_CONFIG_FILE):
        
        print(f"[SUMO Config Test] Configuration file not found: {SUMO_CONFIG_FILE}")
        print(f"[SUMO Config Test] Create a .sumocfg file to test full SUMO functionality")
        return False

    # Start the SUMO process with the configuration file
    proc, sumo_binary, config_file, temp_config, temp_output_dir = start_sumo_with_config(port, SUMO_CONFIG_FILE)
    
    # If the process could not be started, print debug info and return False
    if not proc:
        
        print("[SUMO Config Test] Could not start SUMO process with configuration file.")
        return False
    
    # connected - Initialize connection status
    connected = False
    
    # Try to connect to SUMO via TraCI
    try:
        
        time.sleep(2)
        
        # If debug mode is enabled, print connection attempt info
        if DEBUG_MODE:
            print("[SUMO Config Test] Attempting to connect to SUMO via traci...")
        
        # Initialize TraCI connection to SUMO using the specified port, raising an exception if it fails and setting connected to true if successful
        traci.init(port=port)
        connected = True
        
        # If debug mode is enabled, print connection success info
        if DEBUG_MODE:
            print("[SUMO Config Test] Successfully connected to SUMO via traci with configuration file!")
            print(f"SUMO binary used: {sumo_binary}")
            print(f"Configuration file: {config_file}")
            print(f"SUMO process PID: {proc.pid}")
            print("SUMO process started with full configuration and connection established.")
        
        # If debug mode is enabled, print simulation step info
        if DEBUG_MODE:
            print("  Performing simulation step...")
        
        # Perform a simple simulation step to verify functionality
        traci.simulationStep()
        
        # If debug mode is enabled, print success info
        if DEBUG_MODE:
            print("  Successfully performed simulation step.")
            print("  Simulation time:", traci.simulation.getTime())
    
    # If TraCI connection fails, print debug info if DEBUG_MODE is enabled and return False
    except Exception as e:
        
        if DEBUG_MODE:
            
            print(f"[SUMO Config Test] Failed to connect to SUMO: {e}")
            
            # Try to capture stderr from the process if it's still running
            if proc and proc.poll() is None:
                
                # Try to read stderr output
                try:
                    
                    # Read up to 4096 bytes from stderr
                    stderr = proc.stderr.read(4096).decode()
                    
                    # If there is stderr output, print it
                    if stderr:
                        print(f"[SUMO Config Test] SUMO process stderr:\n{stderr}")
                        
                # If reading stderr fails, ignore the error
                except:
                    pass
    
    # Finally block to ensure cleanup after the test that will always execute regardless of success or failure            
    finally:
        
        # Try to close the TraCI connection if it is loaded
        try:
            if traci.isLoaded():
                traci.close()
                
                # If debug mode is enabled, print debug info
                if DEBUG_MODE:
                    print("  SUMO TraCI connection closed.")
                    
        # If closing TraCI fails, print debug info if DEBUG_MODE is enabled    
        except Exception as e:
            
            if DEBUG_MODE:
                print(f"  TraCI close error: {e}")
        
        # Try to terminate the SUMO process
        try:
            
            proc.terminate()
            proc.wait(timeout=3)
            
            # If debug mode is enabled, print debug info
            if DEBUG_MODE:
                print("  SUMO process terminated.")
                
        # If terminating SUMO fails, try to kill the process
        except subprocess.TimeoutExpired:
            proc.kill()
            
            # If debug mode is enabled, print debug info
            if DEBUG_MODE:
                print("  SUMO process killed (timeout).")
                
        # If killing the process fails, print debug info if DEBUG_MODE is enabled
        except Exception as e:
            
            if DEBUG_MODE:
                print(f"  SUMO process termination error: {e}")
        
        # Clean up temporary files
        if temp_config:
            
            # Try to remove the temporary config file
            try:

                # Remove the temporary config file with unlink
                os.unlink(temp_config)
                
                # If debug mode is enabled, print debug info
                if DEBUG_MODE:
                    print(f"  Cleaned up temporary config file: {temp_config}")
                    
            # If unlink fails, print debug info if DEBUG_MODE is enabled
            except Exception as e:
                
                if DEBUG_MODE:
                    print(f"  Failed to clean up temp config: {e}")
        
        # If a temporary output directory was created, try to remove it
        if temp_output_dir and os.path.exists(temp_output_dir):
            
            # Try to remove the temporary output directory
            try:
                
                # Check log files before removal
                log_files = ["sumo_run.log", "sumo_messages.log", "sumo_errors.log"]
                
                # Iterate through log files and print their content if they exist and if DEBUG_MODE is enabled
                for log_file in log_files:
                    
                    log_path = os.path.join(temp_output_dir, log_file)
                    if os.path.exists(log_path):
                        
                        if DEBUG_MODE:
                            
                            with open(log_path, 'r') as f:
                                content = f.read()
                                
                                if content:
                                    print(f"[SUMO Config Test] Content of {log_file}:\n{content}")
                
                # Remove the temp directory with shutil
                shutil.rmtree(temp_output_dir, ignore_errors=True)
                
                # If debug mode is enabled, print debug info
                if DEBUG_MODE:
                    print(f"  Cleaned up temporary output directory: {temp_output_dir}")
            
            # If removing the temp directory fails, print debug info if DEBUG_MODE is enabled
            except Exception as e:
                
                if DEBUG_MODE:
                    print(f"  Failed to clean up temp output directory: {e}")
        
        # Force cleanup port
        kill_processes_on_port(port)

        time.sleep(2)
    
    # Return the connection status
    return connected


##
# @brief Run both SUMO connection tests and count as tests
#
# @param tested Current count of tests run
# @param passed Current count of tests passed
# @return tuple (tested, passed) Updated counts of tests run and passed
#
# @details Eventually this should be broken apart and the separate tests called individually from preliminary_tests.py
##
def test_sumo_connection_wrapper(tested, passed):
    
    # Print header for SUMO connection tests
    print("\n=== SUMO Connection Tests ===")
    
    # Test 1: Basic network file connection
    print("\n--- SUMO Basic Network Test (simple.net) ---")
    
    # Increment the count of tests run
    tested += 1
    
    # result1 - Run the SUMO basic connection test, storing the result in result1
    result1 = test_sumo_connection()
    
    # If the basic connection test succeeded, increment the count of passed tests and print success message
    # Otherwise, print failure message
    if result1:
        
        passed += 1
        print("[SUMO Basic Test] SUMO basic network connection test completed successfully.")
        
    else:
        
        print("[SUMO Basic Test] SUMO basic network connection test failed.")
    
    # Test 2: Configuration file connection
    print("\n--- SUMO Configuration File Test (threebythreecityblock1.sumocfg) ---")
    
    # Increment the count of tests run
    tested += 1
    
    # result2 - Run the SUMO configuration connection test, storing the result in result2
    result2 = test_sumo_config_connection()
    
    # If the configuration connection test succeeded, increment the count of passed tests and print success message
    # Otherwise, print failure message
    if result2:
        
        passed += 1
        print("[SUMO Config Test] SUMO configuration file connection test completed successfully.")
        
    else:
        print("[SUMO Config Test] SUMO configuration file connection test failed.")
    
    print()
    return tested, passed


##
# @brief Check if all files referenced in the configuration file exist
#
# @param config_path Path to SUMO configuration file
# @return tuple (bool, list) - True if all files exist, list of missing files
#
# @details
#   Steps:
#     1. Parse XML and check file references
#     2. Return missing files if any
##
def check_config_file_references(config_path):
    
    # Try to parse and check the configuration file
    try:
        
        # tree - Parse the XML configuration file
        tree = ET.parse(config_path)
        
        # root - Get the root element of the XML tree
        root = tree.getroot()
        
        # base_dir - Get the directory containing the config file to resolve relative paths
        base_dir = os.path.dirname(config_path)
        
        # missing_files - Initialize list to track missing files
        missing_files = []
        
        # Iterate through all XML elements in the tree
        for elem in root.iter():
            
            # Check all attributes of each element
            for attr_name, attr_value in elem.attrib.items():
                
                # Look for attributes that reference files (ending with -file or file extensions)
                if attr_name.endswith('-file') or attr_name == 'value' and attr_value.endswith(('.xml', '.csv', '.json')):
                    
                    # file_path - Construct the full path to the referenced file
                    file_path = os.path.join(base_dir, attr_value)
                    
                    # Check if the file exists
                    if not os.path.exists(file_path):
                        
                        # If file doesn't exist, add it to missing files list
                        missing_files.append((attr_name, attr_value, file_path))
        
        # If any files are missing, print them in debug mode and return False and the list of missing files
        if missing_files:
            
            if DEBUG_MODE:
                
                print("[SUMO Config Check] Missing referenced files:")
                
                # Print each missing file with its attribute name and path
                for attr_name, attr_value, file_path in missing_files:
                    print(f"  - {attr_name}='{attr_value}' → {file_path}")
                    
            return False, missing_files
        
        # If all files exist, return True and an empty list
        return True, []
    
    # Handle any exceptions during file checking by printing debug info if enabled and returning False and an empty list
    except Exception as e:
        
        if DEBUG_MODE:
            print(f"[SUMO Config Check] Error checking file references: {e}")
            
        return False, []


##
# @brief Create a temporary config file without GUI elements and with essential simulation parameters
#
# @param original_config_path Path to original SUMO config file
# @return tuple (str, str) - Path to temp config file, output directory
#
# @details
#   Steps:
#     1. Remove GUI elements
#     2. Convert relative paths to absolute
#     3. Add time and report settings
#     4. Write to temp file
##
def create_non_gui_config(original_config_path):
    
    # Try to create a modified config without GUI elements
    try:
        
        # original_config_dir - Get the directory of the original config file
        original_config_dir = os.path.dirname(original_config_path)
        
        # Check if all referenced files exist in the original config
        files_exist, unused_missing_files = check_config_file_references(original_config_path)
        
        # Print warning if files are missing - Can use missing_files on output if desired
        if not files_exist and DEBUG_MODE:
            print(f"[SUMO Config Warning] Some referenced files are missing in the original config.")

        # tree - Parse the original configuration XML file
        tree = ET.parse(original_config_path)
        
        # root - Get the root element of the XML tree
        root = tree.getroot()
        
        # Define GUI-related elements to remove from the config
        gui_elements_to_remove = [
            'gui-settings-file',
            'viewsettings-file',
            'gui-settings',
            'viewsettings'
        ]
        
        # Iterate through all elements to remove GUI settings
        for elem in root.iter():
            
            # Iterate through the list of GUI elements to remove
            for gui_elem in gui_elements_to_remove:
                
                # Remove attribute if it exists
                if gui_elem in elem.attrib:
                    del elem.attrib[gui_elem]
                    
                # Remove child element if it exists
                gui_child = elem.find(gui_elem)
                if gui_child is not None:
                    elem.remove(gui_child)
        
        # temp_output_dir - Create a temporary directory for output files
        temp_output_dir = tempfile.mkdtemp(prefix='sumo_outputs_')
        
        # If debug mode is enabled, print the temporary output directory
        if DEBUG_MODE:
            print(f"[SUMO Config Test] Created temporary output directory: {temp_output_dir}")

        # Process all paths in the config to make input paths absolute and redirect outputs
        for elem in root.iter():
            
            # Check all attributes for file paths
            for attr_name, attr_value in list(elem.attrib.items()):
                
                # Look for file path attributes that are relative
                if attr_name == 'value' and attr_value.endswith(('.xml', '.csv', '.json')) and not os.path.isabs(attr_value):
                    
                    ## Handle input vs output files differently
                    # If the path does not start with 'out/' or 'output', treat it as an input file
                    if not attr_value.startswith(('out/', 'output')):
                        
                        # Input file - convert to absolute path
                        abs_path = os.path.join(original_config_dir, attr_value)
                        elem.set(attr_name, abs_path)
                        
                        # If debug mode is enabled, print the conversion
                        if DEBUG_MODE:
                            print(f"[SUMO Config Test] Converting input path: {attr_value} -> {abs_path}")
                    
                    # If the path starts with 'out/' or 'output', treat it as an output file        
                    else:
                        
                        # Output file - redirect to temp directory
                        # Extract the file name and create a new path in the temp output directory
                        output_file = os.path.basename(attr_value)
                        output_path = os.path.join(temp_output_dir, output_file)
                        elem.set(attr_name, output_path)
                        
                        # If debug mode is enabled, print the conversion
                        if DEBUG_MODE:
                            print(f"[SUMO Config Test] Converting output path: {attr_value} -> {output_path}")
        
        # time_elem - Find or create the time element in the config
        time_elem = root.find('time')
        
        # If time element does not exist, create it
        if time_elem is None:
            time_elem = ET.SubElement(root, 'time')
        
        # begin_elem - Find the begin time element
        begin_elem = time_elem.find('begin')
        
        # If begin time is not defined, set a default value
        if begin_elem is None:
            begin_elem = ET.SubElement(time_elem, 'begin')
            begin_elem.set('value', '0')
        
        # end_elem - Find the end time element
        end_elem = time_elem.find('end')
        
        # If end time is not defined, set a default value
        if end_elem is None:
            end_elem = ET.SubElement(time_elem, 'end')
            end_elem.set('value', '100')
        
        # report_elem - Find the report element in the config
        report_elem = root.find('report')
        
        # If report element does not exist, create it
        if report_elem is None:
            report_elem = ET.SubElement(root, 'report')
        
        # verbose_elem - Find the verbose element in the report
        verbose_elem = report_elem.find('verbose')
        
        # If verbose element does not exist, create it and set to true
        if verbose_elem is None:
            verbose_elem = ET.SubElement(report_elem, 'verbose')
            verbose_elem.set('value', 'true')
        
        # error_log_elem - Find the error log element in the report
        error_log_elem = report_elem.find('error-log')
        
        # If error log element does not exist, create it and set the path
        if error_log_elem is None:
            error_log_elem = ET.SubElement(report_elem, 'error-log')
            error_log_elem.set('value', os.path.join(temp_output_dir, 'sumo_errors.log'))
        
        # Create temporary file to store modified config
        temp_fd, temp_path = tempfile.mkstemp(suffix='.sumocfg', text=True)
        
        # Close the file descriptor to avoid resource leak
        os.close(temp_fd)
        
        # Write modified XML to temp file
        tree.write(temp_path, encoding='utf-8', xml_declaration=True)
        
        # Print debug info about created config
        if DEBUG_MODE:
            print(f"[SUMO Config Test] Created temporary non-GUI config: {temp_path}")
            print("\n[SUMO Config Test] Modified configuration content:")
            
            # Print the content of the modified config file
            with open(temp_path, 'r') as f:
                print(f.read())
            
            # Verify that all referenced files exist in the modified config
            files_exist, unused_missing_file = check_config_file_references(temp_path)
            
            # If any files are missing, print a warning -  - Can use missing_files on output if desired
            if not files_exist:
                print(f"[SUMO Config Warning] Some referenced files are missing in the modified config.")
        
        # Return the path to the temp config and the output directory
        return temp_path, temp_output_dir
        
    # Handle any exceptions during config creation by printing debug info if enabled and returning None, None
    except Exception as e:
        
        if DEBUG_MODE:
            print(f"[SUMO Config Test] Failed to create non-GUI config: {e}")
            
        return None, None


##
# @brief Start the SUMO process with the specified network file and port
#
# @return tuple: (proc, sumo_binary, SUMO_NET_FILE)
#
# @details
#   Steps:
#     1. Build SUMO command
#     2. Start SUMO process
#     3. Wait for process to start
#     4. Return process and info
##
def start_sumo():
    
    # Define the path to the SUMO network file from settings
    SUMO_NET_FILE = SUMO_SIMPLE_NET_FILE
    
    # Check if the SUMO network file exists
    if not os.path.exists(SUMO_NET_FILE):
        
        # If network file does not exist, print debug info and return False
        print(f"[SUMO Test] Network file not found: {SUMO_NET_FILE}")
        return False
    
    # Define the SUMO binary to use (non-GUI version for testing)
    sumo_binary = "sumo"
    
    # port - Define the port to use for SUMO connection
    port = SUMO_PORT_BASIC
    
    # sumo_cmd - Build the SUMO command with network file and remote port
    sumo_cmd = [sumo_binary, "-n", SUMO_NET_FILE, "--remote-port", str(port)]
    
    # Try to start the SUMO process
    try:
        
        # Start SUMO as a subprocess, capturing stdout and stderr
        proc = subprocess.Popen(sumo_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait for SUMO to initialize
        time.sleep(3)
        
        # Check if SUMO exited early (which indicates an error)
        if proc.poll() is not None:
            
            # If SUMO exited early, read and print its error output
            stderr = proc.stderr.read().decode()
            print(f"[SUMO Test] SUMO exited early. STDERR:\n{stderr}")
            
            # Return None to indicate failure
            return None, None, None
        
        # If in debug mode, print success message with process ID
        if DEBUG_MODE:
            print(f"[SUMO Test] SUMO process started with PID {proc.pid}")
            
        # Return the process handle, binary name, and network file path
        return proc, sumo_binary, SUMO_NET_FILE
        
    # Handle any exceptions during SUMO startup
    except Exception as e:
        
        # If in debug mode, print the error message
        if DEBUG_MODE:
            print(f"[SUMO Test] Failed to start SUMO: {e}")
            
        # Return None to indicate failure
        return None, None, None
    
    
##
# @brief Start the SUMO process with the specified config file and port
#
# @return tuple (proc, sumo_binary, config_file, temp_config, temp_output_dir)
#
# @details
#   Steps:
#     1. Create a temporary config file without GUI elements
#     2. Build SUMO command
#     3. Start SUMO process
#     4. Wait for process to start
#     5. Return process and info
##
def start_sumo_with_config(port, sumo_config_file):
    
    # Create a modified configuration file without GUI elements and with essential parameters
    temp_config, temp_output_dir = create_non_gui_config(sumo_config_file)
    
    # If config creation failed, print error and return None values
    if not temp_config:
        print("[SUMO Config Test] Failed to create temporary config file.")
        return None, None, None, None, None
    
    # sumo_binary - Define the SUMO binary to use (non-GUI version for testing)
    sumo_binary = "sumo"
    
    # Print debug info about SUMO binary
    if DEBUG_MODE:
        print(f"[SUMO Config Test] Using standard sumo binary with cleaned config")
    
    # sumo_cmd - Build the SUMO command with config file and remote port, redirecting logs to temp output directory
    sumo_cmd = [
        sumo_binary, 
        "-c", temp_config, 
        "--remote-port", str(port),
        "--log", os.path.join(temp_output_dir, "sumo_run.log"),
        "--message-log", os.path.join(temp_output_dir, "sumo_messages.log"),
        "--error-log", os.path.join(temp_output_dir, "sumo_errors.log"),
        "--no-step-log", 
        "--no-warnings"
    ]
    
    # Print full command in debug mode
    if DEBUG_MODE:
        print(f"[SUMO Config Test] SUMO command: {' '.join(sumo_cmd)}")
    
    # Try to start SUMO process
    try:
        
        # Start SUMO as a subprocess
        proc = subprocess.Popen(sumo_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait for SUMO to initialize
        time.sleep(4)
        
        # Check if SUMO exited early (indicating an error)
        if proc.poll() is not None:
            
            # Capture and print stderr and stdout
            stderr = proc.stderr.read().decode()
            stdout = proc.stdout.read().decode()
            print(f"[SUMO Config Test] SUMO exited early with return code {proc.returncode}.")
            print(f"[SUMO Config Test] STDERR output:\n{stderr}")
            
            # Print stdout if it exists
            if stdout:
                print(f"[SUMO Config Test] STDOUT output:\n{stdout}")
            
            # log_files - List of log files to check in the temp output directory
            log_files = ["sumo_run.log", "sumo_messages.log", "sumo_errors.log"]
            
            # Iterate through log files and print their content if they exist
            for log_file in log_files:
                
                # log_path - Construct the full path to the log file
                log_path = os.path.join(temp_output_dir, log_file)
                
                # If the log file exists, read and print its content
                if os.path.exists(log_path):
                    with open(log_path, 'r') as f:
                        content = f.read()
                        if content:
                            print(f"[SUMO Config Test] Content of {log_file}:\n{content}")
            
            # Try to clean up temporary files
            try:
                
                # Remove the temporary config file with unlink
                os.unlink(temp_config)
                
                # Remove the temporary output directory with shutil
                shutil.rmtree(temp_output_dir, ignore_errors=True)
                
            # Ignore errors during cleanup
            except:
                pass
            
            # Return Nones to indicate failure if SUMO could not start
            return None, None, None, None, None
        
        # Print process ID in debug mode
        if DEBUG_MODE:
            print(f"[SUMO Config Test] SUMO process started with PID {proc.pid}")
        
        # Return process and configuration information
        return proc, sumo_binary, sumo_config_file, temp_config, temp_output_dir
    
    # Handle any exceptions during SUMO startup
    except Exception as e:
        
        # If in debug mode, print the error message
        if DEBUG_MODE:
            print(f"[SUMO Config Test] Failed to start SUMO: {e}")
        
        # Clean up temporary files on error
        try:
            
            # Remove the temporary config file with unlink
            os.unlink(temp_config)
            
            # Remove the temporary output directory with shutil
            shutil.rmtree(temp_output_dir, ignore_errors=True)
            
        # Ignore errors during cleanup
        except:
            pass
        
        # Return Nones to indicate failure if SUMO could not start
        return None, None, None, None, None


##
# @brief Start a SUMO simulation with flexible configuration
#
# @param file_path Path to SUMO network file or config file
# @param is_config If True, file_path is treated as a config file; otherwise as a network file
# @param port Port to use for TraCI connection
# @param sumo_binary SUMO binary to use ('sumo' or 'sumo-gui')
# @param connect_traci If True, establishes TraCI connection
# @param step_length Simulation step length in seconds
# @param additional_args Dictionary of additional command-line arguments
# @param sumo_tools_path Path to SUMO tools directory
# @return tuple (proc, traci_module, config_file, temp_config, temp_output_dir)
#
# @details
#   Steps:
#     1. Cleans up any existing processes using the specified port
#     2. Optionally imports TraCI module for connection
#     3. Creates a temporary non-GUI config file if a config file is specified
#     4. Builds the SUMO command with the network or config file and additional options
#     5. Starts the SUMO process and waits for initialization
#     6. If requested, establishes a TraCI connection to the running SUMO instance
##
def start_sumo_simulation(
    file_path,
    is_config=False,
    port=8813,
    sumo_binary="sumo",
    connect_traci=True,
    step_length=None,
    additional_args=None,
    sumo_tools_path=None
):
    
    # Use default SUMO_TOOLS_PATH if not provided
    if sumo_tools_path is None:
        sumo_tools_path = SUMO_TOOLS_PATH

    # Kill any processes using the specified port to avoid conflicts
    kill_processes_on_port(port)
    
    # Clean up any existing TraCI connections
    cleanup_traci_connection()
    
    # Wait for the port to become available, with a timeout
    if not wait_for_port_available(port, timeout=15):
        
        # If port is not available after timeout, print error and return None values
        print(f"[SUMO Simulation] Port {port} is not available after cleanup attempts.")
        return None, None, None, None, None

    # traci_module - Initialize traci_module to None
    traci_module = None
    
    # If TraCI connection is requested, import traci from SUMO tools path
    if connect_traci:
        
        # Append SUMO tools path to sys.path for importing traci
        sys.path.append(sumo_tools_path)
        
        # Try to import traci module
        try:
            
            import traci
            
            # traci_module - Assign imported traci to traci_module
            traci_module = traci
        
        # If import fails, print error and return None values
        except ImportError as e:
            print(f"[SUMO Simulation] Could not import traci: {e}")
            return None, None, None, None, None

    # temp_config, temp_output_dir - Initialize to None
    temp_config = None
    temp_output_dir = None
    
    # sumo_cmd - Start building the SUMO command
    sumo_cmd = [sumo_binary]

    # If using a config file, handle accordingly
    if is_config:
        
        # For non-GUI SUMO, create a temporary config without GUI elements
        if sumo_binary == "sumo":
            
            # Create a temporary non-GUI config file
            temp_config, temp_output_dir = create_non_gui_config(file_path)
            
            # If temp_config is True, use it; otherwise, fall back to original config
            if temp_config:
                sumo_cmd.extend(["-c", temp_config])
                
            else:
                sumo_cmd.extend(["-c", file_path])
                
        else:
            # For GUI SUMO, use the original config file
            sumo_cmd.extend(["-c", file_path])
    
    # If using a network file, handle accordingly
    else:
        
        # If using a network file, add it to the command
        sumo_cmd.extend(["-n", file_path])

    # Add step length argument if specified
    if step_length is not None:
        sumo_cmd.extend(["--step-length", str(step_length)])
        
    # Add remote port argument
    sumo_cmd.extend(["--remote-port", str(port)])

    # Add any additional command-line arguments
    if additional_args:
        
        # Iterate through additional arguments and add them to the command
        for arg, value in additional_args.items():
            
            # If value is None, add the argument as a flag
            if value is None:
                sumo_cmd.append(f"--{arg}")
            
            # Otherwise, add the argument with its value
            else:
                sumo_cmd.extend([f"--{arg}", str(value)])

    # Print the full SUMO command if debug mode is enabled
    if DEBUG_MODE:
        print(f"[SUMO Simulation] Starting SUMO with command: {' '.join(sumo_cmd)}")

    # Try to start the SUMO process
    try:
        
        # proc - Start SUMO as a subprocess, capturing stdout and stderr
        proc = subprocess.Popen(sumo_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait for SUMO to initialize
        time.sleep(3)
        
        # Check if SUMO exited early (indicating an error) and return None values if so
        if proc.poll() is not None:
            
            # Capture and print stderr and stdout
            stderr = proc.stderr.read().decode()
            stdout = proc.stdout.read().decode()
            
            # Output error information
            print(f"[SUMO Simulation] SUMO exited early with return code {proc.returncode}.")
            print(f"[SUMO Simulation] STDERR output:\n{stderr}")
            
            # Print stdout if it exists
            if stdout:
                print(f"[SUMO Simulation] STDOUT output:\n{stdout}")
                
            # If a temporary config was created, clean it up
            if temp_config:
                
                # Try to remove the temporary config file with unlink
                try: 
                    os.unlink(temp_config)
                
                # If unlink fails, ignore the error
                except: 
                    pass
            # If a temporary output directory was created, clean it up
            if temp_output_dir and os.path.exists(temp_output_dir):
                
                # Try to remove the temporary output directory with shutil
                try: 
                    shutil.rmtree(temp_output_dir)
                
                # If removal fails, ignore the error
                except: 
                    pass
                
            return None, None, None, None, None
        
        # Print process ID if debug mode is enabled
        if DEBUG_MODE:
            print(f"[SUMO Simulation] SUMO process started with PID {proc.pid}")
            
        # If TraCI connection is requested, initialize it
        if connect_traci and traci_module:
            
            # Try to establish TraCI connection
            try:
                traci_module.init(port=port)
                
                # If debug mode is enabled, print success message
                if DEBUG_MODE:
                    print(f"[SUMO Simulation] TraCI connection established on port {port}")
            
            # If connection fails, print error, terminate SUMO process, and return None values
            except Exception as e:
                print(f"[SUMO Simulation] Failed to connect to TraCI: {e}")
                proc.terminate()
                return None, None, None, None, None
            
        # Return process, traci module, file path, temp config, and temp output directory
        return proc, traci_module, file_path, temp_config, temp_output_dir
    
    # Handle any exceptions during SUMO startup and return None values if an error occurs
    except Exception as e:
        
        print(f"[SUMO Simulation] Failed to start SUMO: {e}")
        
        # Try to clean up temporary files on error
        if temp_config:
            
            # Try to remove the temporary config file with unlink
            try: 
                os.unlink(temp_config)
            
            # If unlink fails, ignore the error
            except: 
                pass
            
        # If a temporary output directory was created, try to remove it
        if temp_output_dir and os.path.exists(temp_output_dir):
            
            # Try to remove the temporary output directory with shutil
            try: 
                shutil.rmtree(temp_output_dir)
            
            # If removal fails, ignore the error
            except: 
                pass
            
        return None, None, None, None, None


##
# @brief Run a SUMO simulation for a specified number of steps and collect vehicle data, with flexible options
#
# @param traci TraCI module instance with an active connection
# @param steps Number of simulation steps to run
# @param print_data If True, print simulation data to screen.
# @param collect_data List of data types to collect (e.g. ["position", "speed", "color"])
# @param step_delay Time in seconds to wait between steps
# @param vehicle_callbacks Dictionary of callback functions to execute on vehicles
# @return List of dictionaries containing simulation data for each step
#
# @details
#   Steps:
#     1. Advances the simulation by the specified number of steps
#     2. Collects data for each vehicle at each step, including position, speed, color, lane, and lane position
#     3. Executes any specified callback functions for each vehicle at each step
#     4. Optionally prints the collected data to the screen
#     5. Waits for the specified delay between steps
##
def run_sumo_simulation_flexible(
    traci,
    steps,
    print_data=True,
    collect_data=None,
    step_delay=0.1,
    vehicle_callbacks=None
):
    
    # If collect_data is None, default to collecting position data
    if collect_data is None:
        collect_data = ["position"]
        
    # If vehicle_callbacks is None, initialize to an empty dictionary
    if vehicle_callbacks is None:
        vehicle_callbacks = {}

    # sim_data - Initialize an empty list to store simulation data for each step
    sim_data = []
    
    # Execute the specified number of simulation steps
    for step_num in range(steps):
        
        # Advance SUMO simulation by one step
        traci.simulationStep()
        
        # sim_time - Get the current simulation time
        sim_time = traci.simulation.getTime()
        
        # veh_ids - Get the list of all vehicle IDs currently in the simulation
        veh_ids = traci.vehicle.getIDList()
        
        # step_data - Initialize a dictionary to store data for each step
        step_data = {
            "time": sim_time,
            "vehicle_ids": veh_ids,
        }
        
        # Collect requested data types for each vehicle
        for data_type in collect_data:
            
            # Get (x,y) coordinates for each vehicle
            if data_type == "position":
                step_data["position"] = {vid: traci.vehicle.getPosition(vid) for vid in veh_ids}
            
            # Get current speed for each vehicle
            elif data_type == "speed":
                step_data["speed"] = {vid: traci.vehicle.getSpeed(vid) for vid in veh_ids}
                
            # Get RGB color values for each vehicle
            elif data_type == "color":
                step_data["color"] = {vid: traci.vehicle.getColor(vid) for vid in veh_ids}
            
            # Get current lane ID for each vehicle
            elif data_type == "lane":
                step_data["lane"] = {vid: traci.vehicle.getLaneID(vid) for vid in veh_ids}
            
            # Get position along the current lane for each vehicle
            elif data_type == "lane_position":
                step_data["lane_position"] = {vid: traci.vehicle.getLanePosition(vid) for vid in veh_ids}
        
        # Execute any provided callback functions on each vehicle
        for callback_name, callback_func in vehicle_callbacks.items():
            
            # Iterate through each vehicle ID
            for vid in veh_ids:
                
                # Try to call the callback function with the current TraCI instance, vehicle ID, and step number
                try:
                    callback_func(traci, vid, step_num)
                
                # If callback fails, log the error if in debug mode
                except Exception as e:
                    
                    if DEBUG_MODE:
                        print(f"Callback {callback_name} failed for vehicle {vid}: {e}")
        
        # Store this step's data in the simulation history given by sim_data
        sim_data.append(step_data)
        
        # If print_data is enabled, print the collected data for this step
        if print_data:
            print(f"\nTime: {sim_time}, Vehicles: {veh_ids}")
            
            for data_type in collect_data:
                
                if data_type in step_data and step_data[data_type]:
                    print(f"{data_type.capitalize()}: {step_data[data_type]}")
        
        # Add delay between steps if specified - This is the wrong thing I believe, it's a manual delay between each step instead of a step length
        if step_delay > 0:
            time.sleep(step_delay)
            
    # Return the complete simulation data history
    return sim_data


##
# @brief Ensure any existing TraCI connection is properly closed
#
# @details
#   Steps:
#     1. Import traci and close connection if loaded
#     2. Wait for cleanup
##
def cleanup_traci_connection():
    
    # Get SUMO tools path from environment or use default
    SUMO_TOOLS_PATH = os.getenv("SUMO_TOOLS_PATH", "/home/admin/sumo/tools")
    
    # Add SUMO tools path to sys.path for module import
    sys.path.append(SUMO_TOOLS_PATH)

    # Try to import traci and close any existing connection
    try:
        
        import traci

        # If a TraCI connection is loaded, close it
        if traci.isLoaded():
            traci.close()
            
            # If debug mode is enabled, print debug info
            if DEBUG_MODE:
                print("[SUMO Cleanup] Closed existing TraCI connection")
                
        # Wait for cleanup to complete
        time.sleep(1)
        
    # If traci import fails, ignore the error
    except ImportError:
        pass
    
    # Handle any other exceptions and print debug info if enabled
    except Exception as e:
        
        if DEBUG_MODE:
            print(f"[SUMO Cleanup] Error during cleanup: {e}")


##
# @brief Clean up SUMO process and TraCI connection
# @param proc SUMO process
# @param port Port used by TraCI
# @param traci_module TraCI module
#
# @details
#   Steps:
#     1. Close TraCI connection if active
#     2. Terminate SUMO process
#     3. Kill any processes still using the port
##
def cleanup_sumo_and_traci(proc, port, traci_module=None):
    
    # Try to close TraCI connection if it exists
    try:
        
        # If a TraCI module is provided and is loaded, close it
        if traci_module and traci_module.isLoaded():
            traci_module.close()
    
    # If traci import fails, ignore the error
    except Exception:
        pass
    
    # Try to terminate the SUMO process gracefully
    try:
        
        proc.terminate()
        proc.wait(timeout=3)
    
    # If termination fails, try to kill the process
    except Exception:
        
        try:
            proc.kill()
        
        # If killing the process fails, ignore the error
        except Exception:
            pass
    
    # Kill any processes still using the specified port
    kill_processes_on_port(port)
    time.sleep(1)
    
    