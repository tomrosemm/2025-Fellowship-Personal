##
# @file sumo_interface.py
# @author Tom Rose
#
# @brief
#   Provides utility functions for managing SUMO simulation processes and TraCI connections.
#   Includes port cleanup, connection testing, configuration file handling, and data transfer routines
#   for integration with SUMO in automated testing and simulation workflows.
#
# @details
#   - Cleans up processes using specific ports to avoid conflicts.
#   - Checks and waits for port availability before launching SUMO.
#   - Starts SUMO with network or configuration files and connects via TraCI.
#   - Supports aggressive cleanup and diagnostics for robust automated testing.
#   - Handles temporary configuration file creation and output management.
##

# Imports
import sys
import subprocess
import os
import time
import xml.etree.ElementTree as ET
import tempfile
import shutil

from settings import (
    DEBUG_MODE as DEFAULT_DEBUG_MODE,
    SUMO_TOOLS_PATH,
    SUMO_SIMPLE_NET_FILE,
    SUMO_CITY_CONFIG_FILE,
    SUMO_PORT_BASIC,
    SUMO_PORT_CONFIG
)

from utilities import (
    kill_processes_on_port,
    wait_for_port_available,
    is_port_available
)

## @var DEBUG_MODE
# @brief Global variable to control debug output.
DEBUG_MODE = DEFAULT_DEBUG_MODE


##
# @brief Enable or disable debug mode for detailed output.
#
# @param enabled True to enable debug mode, False to disable.
#
# @details
#   Steps:
#     1. Set the global DEBUG_MODE variable to the provided value.
##
def set_debug_mode(enabled):
    
    # Set the global DEBUG_MODE variable
    global DEBUG_MODE
    DEBUG_MODE = enabled


##
# @brief Check if all files referenced in the configuration file exist.
#
# @param config_path Path to SUMO configuration file.
# @return tuple (bool, list) - True if all files exist, list of missing files.
#
# @details
#   Steps:
#     1. Parse XML and check file references.
#     2. Return missing files if any.
##
def check_config_file_references(config_path):
    
    # Try to parse and check the configuration file
    try:
        
        # Parse the XML configuration file
        tree = ET.parse(config_path)
        root = tree.getroot()
        
        # Get the directory containing the config file to resolve relative paths
        base_dir = os.path.dirname(config_path)
        
        # Initialize a list to track missing files
        missing_files = []
        
        # Iterate through all XML elements in the tree
        for elem in root.iter():
            
            # Check all attributes of each element
            for attr_name, attr_value in elem.attrib.items():
                
                # Look for attributes that reference files (ending with -file or file extensions)
                if attr_name.endswith('-file') or attr_name == 'value' and attr_value.endswith(('.xml', '.csv', '.json')):
                    
                    # Convert relative path to absolute path
                    file_path = os.path.join(base_dir, attr_value)
                    
                    # Check if the file exists
                    if not os.path.exists(file_path):
                        
                        # If file doesn't exist, add it to missing files list
                        missing_files.append((attr_name, attr_value, file_path))
        
        # If any files are missing, print them in debug mode and return False
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
# @brief Create a temporary config file without GUI elements and with essential simulation parameters.
#
# @param original_config_path Path to original SUMO config file.
# @return tuple (str, str) - Path to temp config file, output directory.
#
# @details
#   Steps:
#     1. Remove GUI elements.
#     2. Convert relative paths to absolute.
#     3. Add time and report settings.
#     4. Write to temp file.
##
def create_non_gui_config(original_config_path):
    
    # Try to create a modified config without GUI elements
    try:
        
        # Get the directory containing the original config file
        original_config_dir = os.path.dirname(original_config_path)
        
        # Check if all referenced files exist in the original config
        files_exist, unused_missing_files = check_config_file_references(original_config_path)
        
        # Print warning if files are missing
        if not files_exist and DEBUG_MODE:
            print(f"[SUMO Config Warning] Some referenced files are missing in the original config.")

        # Parse the original configuration file
        tree = ET.parse(original_config_path)
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
            
            # Remove GUI attributes from elements
            for gui_elem in gui_elements_to_remove:
                
                # Remove attribute if it exists
                if gui_elem in elem.attrib:
                    del elem.attrib[gui_elem]
                    
                # Remove child element if it exists
                gui_child = elem.find(gui_elem)
                if gui_child is not None:
                    elem.remove(gui_child)
        
        # Create temporary directory for output files
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
        
        # Ensure simulation time settings exist
        time_elem = root.find('time')
        
        # If time element does not exist, create it
        if time_elem is None:
            time_elem = ET.SubElement(root, 'time')
        
        # Set start time if not defined
        begin_elem = time_elem.find('begin')
        
        # If begin time is not defined, set a default value
        if begin_elem is None:
            begin_elem = ET.SubElement(time_elem, 'begin')
            begin_elem.set('value', '0')
        
        # Set end time if not defined
        end_elem = time_elem.find('end')
        
        # If end time is not defined, set a default value
        if end_elem is None:
            end_elem = ET.SubElement(time_elem, 'end')
            end_elem.set('value', '100')
        
        # Add reporting configuration
        report_elem = root.find('report')
        
        # If report element does not exist, create it
        if report_elem is None:
            report_elem = ET.SubElement(root, 'report')
        
        # Enable verbose output for better diagnostics
        verbose_elem = report_elem.find('verbose')
        
        # If verbose element does not exist, create it and set to true
        if verbose_elem is None:
            verbose_elem = ET.SubElement(report_elem, 'verbose')
            verbose_elem.set('value', 'true')
        
        # Set error log location
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
            
            # If any files are missing, print a warning
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
# @brief Start the SUMO process with the specified network file and port.
#
# @return tuple: (proc, sumo_binary, SUMO_NET_FILE)
#
# @details
#   Steps:
#     1. Build SUMO command.
#     2. Start SUMO process.
#     3. Wait for process to start.
#     4. Return process and info.
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
    
        # Wait for port to be available
    port = SUMO_PORT_BASIC
    
    # Build the SUMO command with the network file and remote port
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
# @brief Ensure any existing TraCI connection is properly closed.
#
# @details
#   Steps:
#     1. Import traci and close connection if loaded.
#     2. Wait for cleanup.
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
        
    # Structure to handle if traci is not available, currently just ignore here
    except ImportError:
        pass
    
    # Handle any other exceptions and print debug info if enabled
    except Exception as e:
        
        if DEBUG_MODE:
            print(f"[SUMO Cleanup] Error during cleanup: {e}")


##
# @brief Test the connection to SUMO using TraCI.
#
# @return True if connection succeeded, False otherwise.
#
# @details
#   Steps:
#     1. Aggressively clean up port and connections.
#     2. Start SUMO with network file.
#     3. Attempt to connect via TraCI.
#     4. Clean up after test.
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
    
    # Wait for port to be available
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
    
    # Initialize connection status
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
            print(f"  SUMO binary used: {sumo_binary}")
            print(f"  Network file: {net_file}")
            print(f"  SUMO process PID: {proc.pid}")
            print("  SUMO process started and connection established.")
    
    # If TraCI connection fails, print debug info if DEBUG_MODE is enabled and return False
    except Exception as e:
        
        if DEBUG_MODE:
            print(f"[SUMO Test] Failed to connect to SUMO: {e}")

    # Finally block to ensure cleanup after the test
    # This block will always execute regardless of success or failure
    finally:
        
        # Try to close the TraCI connection if it is loaded
        try:
            
            # If TraCI is loaded, close the connection
            if traci.isLoaded():
                traci.close()
                
                # If debug mode is enabled, print debug info
                if DEBUG_MODE:
                    print("  SUMO TraCI connection closed.")
        
        # If closing TraCI fails, print debug info if Debug mode is enabled
        except Exception as e:
            
            if DEBUG_MODE:
                print(f"  TraCI close error: {e}")
        
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
# @brief Start the SUMO process with the specified config file and port.
#
# @return tuple (proc, sumo_binary, config_file, temp_config, temp_output_dir)
#
# @details
#   Steps:
#     1. Create a temporary config file without GUI elements.
#     2. Build SUMO command.
#     3. Start SUMO process.
#     4. Wait for process to start.
#     5. Return process and info.
##
def start_sumo_with_config(port, sumo_config_file):
    # Create a modified configuration file without GUI elements
    temp_config, temp_output_dir = create_non_gui_config(sumo_config_file)
    
    # If config creation failed, print error and return None values
    if not temp_config:
        print("[SUMO Config Test] Failed to create temporary config file.")
        return None, None, None, None, None
    
    # Define SUMO binary (non-GUI version)
    sumo_binary = "sumo"
    
    # Print debug info about SUMO binary
    if DEBUG_MODE:
        print(f"[SUMO Config Test] Using standard sumo binary with cleaned config")
    
    # Build comprehensive SUMO command with logging options
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
            
            # Check log files for additional error information
            log_files = ["sumo_run.log", "sumo_messages.log", "sumo_errors.log"]
            
            # Iterate through log files and print their content if they exist
            for log_file in log_files:
                log_path = os.path.join(temp_output_dir, log_file)
                
                if os.path.exists(log_path):
                    with open(log_path, 'r') as f:
                        content = f.read()
                        if content:
                            print(f"[SUMO Config Test] Content of {log_file}:\n{content}")
            
            # Clean up temporary files
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
# @brief Test the connection to SUMO using a .sumocfg configuration file.
#
# @return True if connection succeeded, False otherwise.
#
# @details
#   Steps:
#     1. Aggressively clean up port and connections.
#     2. Start SUMO with config file.
#     3. Attempt to connect via TraCI.
#     4. Clean up after test.
##
def test_sumo_config_connection():
    
    # Aggressive cleanup before starting test
    kill_processes_on_port(SUMO_PORT_CONFIG)
    
    # Wait for port to be available
    print("Wait time begins for processes to die and OS to release port")
    time.sleep(10) 
    print("Wait time ends for processes to die and OS to release port")
    
    cleanup_traci_connection()
    
    # Define the port to use for SUMO connection
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
    
    # Initialize connection status
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
            print(f"  SUMO binary used: {sumo_binary}")
            print(f"  Configuration file: {config_file}")
            print(f"  SUMO process PID: {proc.pid}")
            print("  SUMO process started with full configuration and connection established.")
        
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
                
                try:
                    stderr = proc.stderr.read(4096).decode()
                    if stderr:
                        print(f"[SUMO Config Test] SUMO process stderr:\n{stderr}")
                        
                except:
                    pass
    
    # Finally block to ensure cleanup after the test
    # This block will always execute regardless of success or failure            
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
        
        # Clean up output directory
        if temp_output_dir and os.path.exists(temp_output_dir):
            
            # Try to remove the temporary output directory
            try:
                
                # Check log files before removal
                log_files = ["sumo_run.log", "sumo_messages.log", "sumo_errors.log"]
                
                # Iterate through log files and print their content if they exist, if DEBUG_MODE is enabled
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
# @brief Run both SUMO connection tests and count as tests.
#
# @param tested Current count of tests run.
# @param passed Current count of tests passed.
# @return tuple (tested, passed) Updated counts of tests run and passed.
##
def test_sumo_connection_wrapper(tested, passed):
    
    # Print header for SUMO connection tests
    print("\n=== SUMO Connection Tests ===")
    
    # Test 1: Basic network file connection
    print("\n--- SUMO Basic Network Test (simple.net) ---")
    
    # Increment the count of tests run
    tested += 1
    
    # Run the basic SUMO connection test, storing the result in result1
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
    
    # Run the SUMO configuration connection test, storing the result in result2
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
# @brief Start SUMO and connect via TraCI.
# @param sumo_cmd SUMO command list.
# @param port Port to use for TraCI connection.
# @param sumo_tools_path Path to SUMO tools directory.
# @return tuple (proc, traci_module) - SUMO process and TraCI module.
#
# @details
#   Steps:
#     1. Add SUMO tools to path.
#     2. Import TraCI.
#     3. Start SUMO process.
#     4. Connect via TraCI.
#     5. Return process and TraCI module.
##
def start_sumo_and_traci(sumo_cmd, port, sumo_tools_path):
    sys.path.append(sumo_tools_path)
    try:
        import traci
    except ImportError:
        print("[SUMO TraCI Test] Could not import traci. Check SUMO_TOOLS_PATH.")
        return None, None
    proc = subprocess.Popen(sumo_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    time.sleep(3)
    if proc.poll() is not None:
        stderr = proc.stderr.read().decode()
        print(f"[SUMO TraCI Test] SUMO exited early. STDERR:\n{stderr}")
        return None, None
    traci.init(port=port)
    time.sleep(1)
    return proc, traci

##
# @brief Clean up SUMO process and TraCI connection.
# @param proc SUMO process.
# @param port Port used by TraCI.
# @param traci_module TraCI module.
#
# @details
#   Steps:
#     1. Close TraCI connection if active.
#     2. Terminate SUMO process.
#     3. Kill any processes still using the port.
##
def cleanup_sumo_and_traci(proc, port, traci_module=None):
    try:
        if traci_module and traci_module.isLoaded():
            traci_module.close()
    except Exception:
        pass
    try:
        proc.terminate()
        proc.wait(timeout=3)
    except Exception:
        try:
            proc.kill()
        except Exception:
            pass
    kill_processes_on_port(port)
    time.sleep(1)

##
# @brief Start a SUMO simulation with flexible configuration.
#
# @param file_path Path to SUMO network file or config file.
# @param is_config If True, file_path is treated as a config file; otherwise as a network file.
# @param port Port to use for TraCI connection.
# @param sumo_binary SUMO binary to use ('sumo' or 'sumo-gui').
# @param connect_traci If True, establishes TraCI connection.
# @param step_length Simulation step length in seconds.
# @param additional_args Dictionary of additional command-line arguments.
# @param sumo_tools_path Path to SUMO tools directory.
# @return tuple (proc, traci_module, config_file, temp_config, temp_output_dir)
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

    kill_processes_on_port(port)
    cleanup_traci_connection()
    if not wait_for_port_available(port, timeout=15):
        print(f"[SUMO Simulation] Port {port} is not available after cleanup attempts.")
        return None, None, None, None, None

    traci_module = None
    if connect_traci:
        sys.path.append(sumo_tools_path)
        try:
            import traci
            traci_module = traci
        except ImportError as e:
            print(f"[SUMO Simulation] Could not import traci: {e}")
            return None, None, None, None, None

    temp_config = None
    temp_output_dir = None
    sumo_cmd = [sumo_binary]

    if is_config:
        # For config files, create a temporary non-GUI config if using non-GUI SUMO
        if sumo_binary == "sumo":
            temp_config, temp_output_dir = create_non_gui_config(file_path)
            if temp_config:
                sumo_cmd.extend(["-c", temp_config])
            else:
                sumo_cmd.extend(["-c", file_path])
        else:
            sumo_cmd.extend(["-c", file_path])
    else:
        sumo_cmd.extend(["-n", file_path])

    if step_length is not None:
        sumo_cmd.extend(["--step-length", str(step_length)])
    sumo_cmd.extend(["--remote-port", str(port)])

    if additional_args:
        for arg, value in additional_args.items():
            if value is None:
                sumo_cmd.append(f"--{arg}")
            else:
                sumo_cmd.extend([f"--{arg}", str(value)])

    if DEBUG_MODE:
        print(f"[SUMO Simulation] Starting SUMO with command: {' '.join(sumo_cmd)}")

    try:
        proc = subprocess.Popen(sumo_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        time.sleep(3)
        if proc.poll() is not None:
            stderr = proc.stderr.read().decode()
            stdout = proc.stdout.read().decode()
            print(f"[SUMO Simulation] SUMO exited early with return code {proc.returncode}.")
            print(f"[SUMO Simulation] STDERR output:\n{stderr}")
            if stdout:
                print(f"[SUMO Simulation] STDOUT output:\n{stdout}")
            if temp_config:
                try: os.unlink(temp_config)
                except: pass
            if temp_output_dir and os.path.exists(temp_output_dir):
                try: shutil.rmtree(temp_output_dir)
                except: pass
            return None, None, None, None, None
        if DEBUG_MODE:
            print(f"[SUMO Simulation] SUMO process started with PID {proc.pid}")
        if connect_traci and traci_module:
            try:
                traci_module.init(port=port)
                if DEBUG_MODE:
                    print(f"[SUMO Simulation] TraCI connection established on port {port}")
            except Exception as e:
                print(f"[SUMO Simulation] Failed to connect to TraCI: {e}")
                proc.terminate()
                return None, None, None, None, None
        return proc, traci_module, file_path, temp_config, temp_output_dir
    except Exception as e:
        print(f"[SUMO Simulation] Failed to start SUMO: {e}")
        if temp_config:
            try: os.unlink(temp_config)
            except: pass
        if temp_output_dir and os.path.exists(temp_output_dir):
            try: shutil.rmtree(temp_output_dir)
            except: pass
        return None, None, None, None, None

##
# @brief Run a SUMO simulation for a specified number of steps and collect vehicle data, with flexible options.
#
# @param traci TraCI module instance with an active connection.
# @param steps Number of simulation steps to run.
# @param print_data If True, print simulation data to screen.
# @param collect_data List of data types to collect (e.g. ["position", "speed", "color"])
# @param step_delay Time in seconds to wait between steps.
# @param vehicle_callbacks Dictionary of callback functions to execute on vehicles.
# @return List of dictionaries containing simulation data for each step.
##
def run_sumo_simulation_flexible(
    traci,
    steps,
    print_data=True,
    collect_data=None,
    step_delay=0.1,
    vehicle_callbacks=None
):
    if collect_data is None:
        collect_data = ["position"]
    if vehicle_callbacks is None:
        vehicle_callbacks = {}

    sim_data = []
    for step_num in range(steps):
        traci.simulationStep()
        sim_time = traci.simulation.getTime()
        veh_ids = traci.vehicle.getIDList()
        step_data = {
            "time": sim_time,
            "vehicle_ids": veh_ids,
        }
        for data_type in collect_data:
            if data_type == "position":
                step_data["positions"] = {vid: traci.vehicle.getPosition(vid) for vid in veh_ids}
            elif data_type == "speed":
                step_data["speeds"] = {vid: traci.vehicle.getSpeed(vid) for vid in veh_ids}
            elif data_type == "color":
                step_data["colors"] = {vid: traci.vehicle.getColor(vid) for vid in veh_ids}
            elif data_type == "lane":
                step_data["lanes"] = {vid: traci.vehicle.getLaneID(vid) for vid in veh_ids}
            elif data_type == "lane_position":
                step_data["lane_positions"] = {vid: traci.vehicle.getLanePosition(vid) for vid in veh_ids}
        for callback_name, callback_func in vehicle_callbacks.items():
            for vid in veh_ids:
                try:
                    callback_func(traci, vid, step_num)
                except Exception as e:
                    if DEBUG_MODE:
                        print(f"Callback {callback_name} failed for vehicle {vid}: {e}")
        sim_data.append(step_data)
        if print_data:
            print(f"\nTime: {sim_time}, Vehicles: {veh_ids}")
            for data_type in collect_data:
                if data_type in step_data and step_data[data_type]:
                    print(f"{data_type.capitalize()}: {step_data[data_type]}")
        if step_delay > 0:
            time.sleep(step_delay)
    return sim_data

