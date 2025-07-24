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

import sys
import subprocess
import os
import time
import socket
import psutil
import xml.etree.ElementTree as ET
import tempfile


DEBUG_MODE = False


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
    
    global DEBUG_MODE
    DEBUG_MODE = enabled


##
# @brief Kill any processes using the specified port.
#
# @param port Port number to clean up.
# @return True if any processes were killed, False otherwise.
#
# @details
#   Steps:
#     1. Iterate over processes and kill those using the port.
#     2. Wait for OS to release the port if any were killed.
##
def kill_processes_on_port(port):
    
    killed_any = False
    
    try:
        for proc in psutil.process_iter(['pid', 'name', 'connections']):
            
            try:
                
                connections = proc.info['connections']
                
                if connections:
                    for conn in connections:
                        if hasattr(conn, 'laddr') and conn.laddr and conn.laddr.port == port:

                            if DEBUG_MODE:                                
                                print(f"[Port Cleanup] Killing process {proc.info['pid']} ({proc.info['name']}) using port {port}")
                                
                            proc.kill()
                            killed_any = True
                            
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
            
    except Exception as e:
        
        if DEBUG_MODE:
            print(f"[Port Cleanup] Error during port cleanup: {e}")
    
    if killed_any:
        print("Wait time begins for processes to die and OS to release port")
        time.sleep(10)
        print("Wait time ends for processes to die and OS to release port")
        
    return killed_any


##
# @brief Check if a port is available for use.
#
# @param port Port number to check.
# @return True if port is available, False otherwise.
#
# @details
#   Steps:
#     1. Attempt to bind to the port.
#     2. Return True if successful, False otherwise.
##
def is_port_available(port):
    
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            
            s.bind(('localhost', port))
            return True
        
    except OSError:
        return False


##
# @brief Wait for a port to become available, forcefully cleaning if needed.
#
# @param port Port number to wait for.
# @param timeout Timeout in seconds.
# @return True if port becomes available, False otherwise.
#
# @details
#   Steps:
#     1. Check port availability in a loop.
#     2. After 3 failed attempts, try to kill processes on the port.
##
def wait_for_port_available(port, timeout=15):
    
    start_time = time.time()
    attempts = 0
    
    while time.time() - start_time < timeout:
        if is_port_available(port):
            
            return True
        
        attempts += 1
        
        if attempts == 3:  # After 3 failed attempts, try to kill processes
            
            if DEBUG_MODE:
                print(f"[Port Management] Port {port} still busy, attempting to kill processes")
                
            killed = kill_processes_on_port(port)
            
            if killed and DEBUG_MODE:
                print(f"[Port Management] Killed processes on port {port}")
        
        time.sleep(1)
    
    return False


##
# @brief Ensure any existing TraCI connection is properly closed.
#
# @details
#   Steps:
#     1. Import traci and close connection if loaded.
#     2. Wait for cleanup.
##
def cleanup_traci_connection():

    SUMO_TOOLS_PATH = os.getenv("SUMO_TOOLS_PATH", "/home/admin/sumo/tools")
    sys.path.append(SUMO_TOOLS_PATH)
    
    try:
        
        import traci
        
        if traci.isLoaded():
            
            traci.close()
            
            if DEBUG_MODE:
                print("[SUMO Cleanup] Closed existing TraCI connection")
                
        time.sleep(1)  # Give time for cleanup
        
    except ImportError:
        pass  # TraCI not available
    
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
    
    # --- Aggressive cleanup before starting test ---
    kill_processes_on_port(8813)
    cleanup_traci_connection()
    
    print("Wait time begins for processes to die and OS to release port")
    time.sleep(10) 
    print("Wait time ends for processes to die and OS to release port")


    # Clean up any existing connections first
    cleanup_traci_connection()
    
    # Wait for port to be available
    port = 8813
    
    if not wait_for_port_available(port, timeout=15):
        
        print(f"[SUMO Test] Port {port} is not available after waiting and cleanup attempts.")
        return False
    
    SUMO_TOOLS_PATH = os.getenv("SUMO_TOOLS_PATH", "/home/admin/sumo/tools")
    sys.path.append(SUMO_TOOLS_PATH)

    try:
        
        import traci
        
    except ImportError as e:
        
        if DEBUG_MODE:
            print(f"[SUMO Test] Could not import traci: {e}")
            print(f"Check that SUMO_TOOLS_PATH is correct: {SUMO_TOOLS_PATH}")
            
        return False

    SUMO_NET_FILE = os.path.abspath("/home/admin/2025-Fellowship-Personal/Python/Basic Concept/sumo/simple.net.xml")
    
    if not os.path.exists(SUMO_NET_FILE):
        
        print(f"[SUMO Test] Network file not found: {SUMO_NET_FILE}")
        return False


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
        
        sumo_binary = "sumo"
        sumo_cmd = [sumo_binary, "-n", SUMO_NET_FILE, "--remote-port", str(port)]
        
        try:
            
            proc = subprocess.Popen(sumo_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            time.sleep(3)  # Give more time to start
            
            if proc.poll() is not None:
                
                # SUMO exited early, print stderr for diagnostics
                stderr = proc.stderr.read().decode()
                print(f"[SUMO Test] SUMO exited early. STDERR:\n{stderr}")
                return None, None, None
            
            if DEBUG_MODE:
                print(f"[SUMO Test] SUMO process started with PID {proc.pid}")
                
            return proc, sumo_binary, SUMO_NET_FILE
        
        except Exception as e:
            
            if DEBUG_MODE:
                print(f"[SUMO Test] Failed to start SUMO: {e}")
                
            return None, None, None

    proc, sumo_binary, net_file = start_sumo()
    
    if not proc:
        
        print("[SUMO Test] Could not start SUMO process.")
        return False
    
    connected = False
    
    try:
        
        time.sleep(2)  # Additional wait before connecting
        traci.init(port=port)
        connected = True
        
        if DEBUG_MODE:
            print("[SUMO Test] Successfully connected to SUMO via traci!")
            print(f"  SUMO binary used: {sumo_binary}")
            print(f"  Network file: {net_file}")
            print(f"  SUMO process PID: {proc.pid}")
            print("  SUMO process started and connection established.")
            
    except Exception as e:
        
        if DEBUG_MODE:
            print(f"[SUMO Test] Failed to connect to SUMO: {e}")
            
    finally:
        
        # To ensure proper cleanup
        try:
            if traci.isLoaded():
                
                traci.close()
                
                if DEBUG_MODE:
                    print("  SUMO TraCI connection closed.")
                    
        except Exception as e:
            
            if DEBUG_MODE:
                print(f"  TraCI close error: {e}")
        
        try:
            
            proc.terminate()
            proc.wait(timeout=3)
            
            if DEBUG_MODE:
                print("  SUMO process terminated.")
                
        except subprocess.TimeoutExpired:
            
            proc.kill()
            
            if DEBUG_MODE:
                print("  SUMO process killed (timeout).")
                
        except Exception as e:
            
            if DEBUG_MODE:
                print(f"  SUMO process termination error: {e}")
        
        # Force cleanup
        kill_processes_on_port(port)
        time.sleep(2)  # Give OS time to release port and clean up
        
    return connected


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
    
    try:
        
        tree = ET.parse(config_path)
        root = tree.getroot()
        base_dir = os.path.dirname(config_path)
        missing_files = []
        
        # Find all file references in the XML
        for elem in root.iter():
            for attr_name, attr_value in elem.attrib.items():
                if attr_name.endswith('-file') or attr_name == 'value' and attr_value.endswith(('.xml', '.csv', '.json')):
                    
                    file_path = os.path.join(base_dir, attr_value)
                    
                    if not os.path.exists(file_path):
                        
                        missing_files.append((attr_name, attr_value, file_path))
        
        if missing_files:
            if DEBUG_MODE:
                
                print("[SUMO Config Check] Missing referenced files:")
                
                for attr_name, attr_value, file_path in missing_files:
                    
                    print(f"  - {attr_name}='{attr_value}' → {file_path}")
                    
            return False, missing_files
        
        return True, []
    
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
    
    try:
        
        # Get the directory of the original config file for resolving relative paths
        original_config_dir = os.path.dirname(original_config_path)
        
        # First check if files referenced in original config exist
        files_exist, unused_missing_files = check_config_file_references(original_config_path)
        
        if not files_exist and DEBUG_MODE:
            print(f"[SUMO Config Warning] Some referenced files are missing in the original config.")

        tree = ET.parse(original_config_path)
        root = tree.getroot()
        
        # Remove GUI-related elements
        gui_elements_to_remove = [
            'gui-settings-file',
            'viewsettings-file',
            'gui-settings',
            'viewsettings'
        ]
        
        for elem in root.iter():
            for gui_elem in gui_elements_to_remove:
                if gui_elem in elem.attrib:
                    
                    del elem.attrib[gui_elem]
                    
                gui_child = elem.find(gui_elem)
                
                if gui_child is not None:
                    
                    elem.remove(gui_child)
        
        # Create temp output directory for files
        temp_output_dir = tempfile.mkdtemp(prefix='sumo_outputs_')
        
        if DEBUG_MODE:
            print(f"[SUMO Config Test] Created temporary output directory: {temp_output_dir}")

        # Convert relative paths to absolute paths
        for elem in root.iter():
            for attr_name, attr_value in list(elem.attrib.items()):
                
                # For input files, make sure they use absolute paths
                if attr_name == 'value' and attr_value.endswith(('.xml', '.csv', '.json')) and not os.path.isabs(attr_value):
                    
                    if not attr_value.startswith(('out/', 'output')):
                        
                        # Input file - convert to absolute path based on original config location
                        abs_path = os.path.join(original_config_dir, attr_value)
                        elem.set(attr_name, abs_path)
                        
                        if DEBUG_MODE:
                            print(f"[SUMO Config Test] Converting input path: {attr_value} -> {abs_path}")
                            
                    else:
                        
                        # Output file - direct to temp directory
                        output_file = os.path.basename(attr_value)
                        output_path = os.path.join(temp_output_dir, output_file)
                        elem.set(attr_name, output_path)
                        
                        if DEBUG_MODE:
                            print(f"[SUMO Config Test] Converting output path: {attr_value} -> {output_path}")
        
        # Ensure we have time settings to keep SUMO running
        time_elem = root.find('time')
        
        if time_elem is None:
            
            time_elem = ET.SubElement(root, 'time')
        
        # Set or update time parameters
        begin_elem = time_elem.find('begin')
        
        if begin_elem is None:
            
            begin_elem = ET.SubElement(time_elem, 'begin')
            begin_elem.set('value', '0')
        
        end_elem = time_elem.find('end')
        
        if end_elem is None:
            
            end_elem = ET.SubElement(time_elem, 'end')
            end_elem.set('value', '100')  # Run for 100 simulation seconds
        
        # Add report settings for verbose output
        report_elem = root.find('report')
        
        if report_elem is None:
            
            report_elem = ET.SubElement(root, 'report')
        
        # Add verbose attribute for detailed error reporting
        verbose_elem = report_elem.find('verbose')
        
        if verbose_elem is None:
            
            verbose_elem = ET.SubElement(report_elem, 'verbose')
            verbose_elem.set('value', 'true')
        
        # Add error-log attribute
        error_log_elem = report_elem.find('error-log')
        
        if error_log_elem is None:
            
            error_log_elem = ET.SubElement(report_elem, 'error-log')
            error_log_elem.set('value', os.path.join(temp_output_dir, 'sumo_errors.log'))
        
        # Create temporary file
        temp_fd, temp_path = tempfile.mkstemp(suffix='.sumocfg', text=True)
        os.close(temp_fd)
        
        tree.write(temp_path, encoding='utf-8', xml_declaration=True)
        
        if DEBUG_MODE:
            print(f"[SUMO Config Test] Created temporary non-GUI config: {temp_path}")
            # Output the content of the modified config file for debugging
            print("\n[SUMO Config Test] Modified configuration content:")
            
            with open(temp_path, 'r') as f:
                print(f.read())
            
            # Check if files referenced in the new config exist
            files_exist, unused_missing_file = check_config_file_references(temp_path)
            
            if not files_exist:
                print(f"[SUMO Config Warning] Some referenced files are missing in the modified config.")
        
        # Return both the temporary config path and the output directory for later cleanup
        return temp_path, temp_output_dir
        
    except Exception as e:
        
        if DEBUG_MODE:
            print(f"[SUMO Config Test] Failed to create non-GUI config: {e}")
            
        return None, None


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
    
    # --- Aggressive cleanup before starting test ---
    kill_processes_on_port(8814)
    cleanup_traci_connection()
    
    print("Wait time begins for processes to die and OS to release port")
    time.sleep(10) 
    print("Wait time ends for processes to die and OS to release port")

    
    # Clean up any existing connections first
    cleanup_traci_connection()
    
    # Wait for port to be available
    port = 8814
    
    if not wait_for_port_available(port, timeout=15):
        
        print(f"[SUMO Config Test] Port {port} is not available after waiting and cleanup attempts.")
        return False
    
    SUMO_TOOLS_PATH = os.getenv("SUMO_TOOLS_PATH", "/home/admin/sumo/tools")
    sys.path.append(SUMO_TOOLS_PATH)

    try:
        
        import traci
        
    except ImportError as e:
        
        if DEBUG_MODE:
            print(f"[SUMO Config Test] Could not import traci: {e}")
            print(f"Check that SUMO_TOOLS_PATH is correct: {SUMO_TOOLS_PATH}")
            
        return False

    SUMO_CONFIG_FILE = os.path.abspath("/home/admin/2025-Fellowship-Personal/Python/Basic Concept/sumo/3x3 city block 1/threebythreecityblock1.sumocfg")
    
    if not os.path.exists(SUMO_CONFIG_FILE):
        
        print(f"[SUMO Config Test] Configuration file not found: {SUMO_CONFIG_FILE}")
        print(f"[SUMO Config Test] Create a .sumocfg file to test full SUMO functionality")
        return False


    ##
    # @brief Start the SUMO process with the specified config file and port.
    #
    # @return tuple (proc, sumo_binary, SUMO_CONFIG_FILE, temp_config, temp_output_dir)
    #
    # @details
    #   Steps:
    #     1. Create a temporary config file without GUI elements.
    #     2. Build SUMO command.
    #     3. Start SUMO process.
    #     4. Wait for process to start.
    #     5. Return process and info.
    ##
    def start_sumo_with_config():
        
        # Create a temporary config file without GUI elements
        temp_config, temp_output_dir = create_non_gui_config(SUMO_CONFIG_FILE)
        
        if not temp_config:
            
            print("[SUMO Config Test] Failed to create temporary config file.")
            return None, None, None, None, None
        
        sumo_binary = "sumo"
        
        if DEBUG_MODE:
            
            print(f"[SUMO Config Test] Using standard sumo binary with cleaned config")
        
        # Use command line arguments for better diagnostics
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
        
        if DEBUG_MODE:
            print(f"[SUMO Config Test] SUMO command: {' '.join(sumo_cmd)}")
        
        try:
            
            proc = subprocess.Popen(sumo_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            time.sleep(4)  # Give time to start
            
            if proc.poll() is not None:
                
                # SUMO exited early, print stderr for diagnostics
                stderr = proc.stderr.read().decode()
                stdout = proc.stdout.read().decode()
                print(f"[SUMO Config Test] SUMO exited early with return code {proc.returncode}.")
                print(f"[SUMO Config Test] STDERR output:\n{stderr}")
                
                if stdout:
                    print(f"[SUMO Config Test] STDOUT output:\n{stdout}")
                    
                # Check for log files
                log_files = ["sumo_run.log", "sumo_messages.log", "sumo_errors.log"]
                
                for log_file in log_files:
                    
                    log_path = os.path.join(temp_output_dir, log_file)
                    
                    if os.path.exists(log_path):
                        with open(log_path, 'r') as f:
                            
                            content = f.read()
                            
                            if content:
                                
                                print(f"[SUMO Config Test] Content of {log_file}:\n{content}")
                
                # Clean up temp file
                try:
                    
                    os.unlink(temp_config)
                    import shutil
                    shutil.rmtree(temp_output_dir, ignore_errors=True)
                    
                except:
                    
                    pass
                
                return None, None, None, None, None
            
            if DEBUG_MODE:
                print(f"[SUMO Config Test] SUMO process started with PID {proc.pid}")
                
            return proc, sumo_binary, SUMO_CONFIG_FILE, temp_config, temp_output_dir
        
        except Exception as e:
            
            if DEBUG_MODE:
                print(f"[SUMO Config Test] Failed to start SUMO: {e}")
                
            # Clean up temp file and directory
            try:
                
                os.unlink(temp_config)
                import shutil
                shutil.rmtree(temp_output_dir, ignore_errors=True)
                
            except:
                
                pass
            
            return None, None, None, None, None

    proc, sumo_binary, config_file, temp_config, temp_output_dir = start_sumo_with_config()
    
    if not proc:
        
        print("[SUMO Config Test] Could not start SUMO process with configuration file.")
        return False
        
    connected = False
    
    try:
        
        time.sleep(2)  # Additional wait before connecting
        
        if DEBUG_MODE:
            print("[SUMO Config Test] Attempting to connect to SUMO via traci...")
        
        traci.init(port=port)
        connected = True
        
        if DEBUG_MODE:
            print("[SUMO Config Test] Successfully connected to SUMO via traci with configuration file!")
            print(f"  SUMO binary used: {sumo_binary}")
            print(f"  Configuration file: {config_file}")
            print(f"  SUMO process PID: {proc.pid}")
            print("  SUMO process started with full configuration and connection established.")
        
        # Perform a simple simulation step to verify functionality
        if DEBUG_MODE:
            print("  Performing simulation step...")
            
        traci.simulationStep()
        
        if DEBUG_MODE:
            print("  Successfully performed simulation step.")
            print("  Simulation time:", traci.simulation.getTime())
            
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
                
    finally:
        
        # Ensure proper cleanup
        try:
            if traci.isLoaded():
                
                traci.close()
                
                if DEBUG_MODE:
                    print("  SUMO TraCI connection closed.")
                    
        except Exception as e:
            
            if DEBUG_MODE:
                print(f"  TraCI close error: {e}")
        
        try:
            
            proc.terminate()
            proc.wait(timeout=3)
            
            if DEBUG_MODE:
                print("  SUMO process terminated.")
                
        except subprocess.TimeoutExpired:
            proc.kill()
            
            if DEBUG_MODE:
                print("  SUMO process killed (timeout).")
                
        except Exception as e:
            
            if DEBUG_MODE:
                print(f"  SUMO process termination error: {e}")
        
        # Clean up temporary files
        if temp_config:
            try:
                
                os.unlink(temp_config)
                
                if DEBUG_MODE:
                    print(f"  Cleaned up temporary config file: {temp_config}")
                    
            except Exception as e:
                
                if DEBUG_MODE:
                    print(f"  Failed to clean up temp config: {e}")
        
        # Clean up output directory
        if temp_output_dir and os.path.exists(temp_output_dir):
            try:
                
                import shutil
                # Check log files before removal
                log_files = ["sumo_run.log", "sumo_messages.log", "sumo_errors.log"]
                
                for log_file in log_files:
                    
                    log_path = os.path.join(temp_output_dir, log_file)
                    
                    if os.path.exists(log_path):
                        
                        if DEBUG_MODE:
                            with open(log_path, 'r') as f:
                                
                                content = f.read()
                                
                                if content:
                                    print(f"[SUMO Config Test] Content of {log_file}:\n{content}")
                
                # Remove the temp directory
                shutil.rmtree(temp_output_dir, ignore_errors=True)
                
                if DEBUG_MODE:
                    print(f"  Cleaned up temporary output directory: {temp_output_dir}")
                    
            except Exception as e:
                
                if DEBUG_MODE:
                    print(f"  Failed to clean up temp output directory: {e}")
        
        # Force cleanup port
        kill_processes_on_port(port)
        time.sleep(2)  # Give OS time to release port and clean up
        
    return connected


##
# @brief Run both SUMO connection tests and count as tests.
#
# @param tested Current count of tests run.
# @param passed Current count of tests passed.
# @return tuple (tested, passed) Updated counts of tests run and passed.
##
def test_sumo_connection_wrapper(tested, passed):
    
    print("\n=== SUMO Connection Tests ===")
    
    # Test 1: Basic network file connection
    print("\n--- SUMO Basic Network Test ---")
    
    tested += 1
    result1 = test_sumo_connection()
    
    if result1:
        
        passed += 1
        print("[SUMO Basic Test] SUMO basic network connection test completed successfully.")
        
    else:
        
        print("[SUMO Basic Test] SUMO basic network connection test failed.")
    
    # Test 2: Configuration file connection
    print("\n--- SUMO Configuration File Test ---")
    
    tested += 1
    result2 = test_sumo_config_connection()
    
    if result2:
        
        passed += 1
        print("[SUMO Config Test] SUMO configuration file connection test completed successfully.")
        
    else:
        print("[SUMO Config Test] SUMO configuration file connection test failed.")
    
    print()
    return tested, passed

