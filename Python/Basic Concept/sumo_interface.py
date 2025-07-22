import sys
import subprocess
import os
import time
import socket
import psutil
import xml.etree.ElementTree as ET
import tempfile

DEBUG_MODE = False

def set_debug_mode(enabled):
    global DEBUG_MODE
    DEBUG_MODE = enabled

def kill_processes_on_port(port):
    """Kill any processes using the specified port."""
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
        time.sleep(2)  # Give time for processes to die
    return killed_any

def is_port_available(port):
    """Check if a port is available for use."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('localhost', port))
            return True
    except OSError:
        return False

def wait_for_port_available(port, timeout=15):
    """Wait for a port to become available, forcefully cleaning if needed."""
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

def cleanup_traci_connection():
    """
    Ensure any existing TraCI connection is properly closed.
    """
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

def test_sumo_connection():
    """
    Test the connection to SUMO using TraCI.
    Returns:
        bool: True if connection succeeded, False otherwise.
    """
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
        # Always ensure proper cleanup
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
        
        # Force cleanup port
        kill_processes_on_port(port)
        time.sleep(2)  # Give OS time to release port and clean up
    return connected

def create_non_gui_config(original_config_path):
    """Create a temporary config file without GUI elements and with essential simulation parameters."""
    try:
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
        
        step_length_elem = time_elem.find('step-length')
        if step_length_elem is None:
            step_length_elem = ET.SubElement(time_elem, 'step-length')
        step_length_elem.set('value', '1')
        
        # Add processing settings to prevent immediate exit
        processing_elem = root.find('processing')
        if processing_elem is None:
            processing_elem = ET.SubElement(root, 'processing')
        
        ignore_route_errors_elem = processing_elem.find('ignore-route-errors')
        if ignore_route_errors_elem is None:
            ignore_route_errors_elem = ET.SubElement(processing_elem, 'ignore-route-errors')
        ignore_route_errors_elem.set('value', 'true')
        
        # Create temporary file
        temp_fd, temp_path = tempfile.mkstemp(suffix='.sumocfg', text=True)
        os.close(temp_fd)
        
        tree.write(temp_path, encoding='utf-8', xml_declaration=True)
        if DEBUG_MODE:
            print(f"[SUMO Config Test] Created temporary non-GUI config: {temp_path}")
        return temp_path
        
    except Exception as e:
        if DEBUG_MODE:
            print(f"[SUMO Config Test] Failed to create non-GUI config: {e}")
        return None

def test_sumo_config_connection():
    """
    Test the connection to SUMO using a .sumocfg configuration file.
    Returns:
        bool: True if connection succeeded, False otherwise.
    """
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

    def start_sumo_with_config():
        # Create a temporary config file without GUI elements
        temp_config = create_non_gui_config(SUMO_CONFIG_FILE)
        if not temp_config:
            print("[SUMO Config Test] Failed to create temporary config file.")
            return None, None, None, None
        
        sumo_binary = "sumo"
        if DEBUG_MODE:
            print(f"[SUMO Config Test] Using standard sumo binary with cleaned config")
        
        # Add additional parameters to keep SUMO stable
        sumo_cmd = [
            sumo_binary, 
            "-c", temp_config, 
            "--remote-port", str(port),
            "--no-step-log",
            "--no-warnings", 
            "--quit-on-end"
        ]
        
        try:
            proc = subprocess.Popen(sumo_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            time.sleep(4)  # Give even more time to start
            if proc.poll() is not None:
                # SUMO exited early, print stderr for diagnostics
                stderr = proc.stderr.read().decode()
                print(f"[SUMO Config Test] SUMO exited early. STDERR:\n{stderr}")
                # Clean up temp file
                try:
                    os.unlink(temp_config)
                except:
                    pass
                return None, None, None, None
            if DEBUG_MODE:
                print(f"[SUMO Config Test] SUMO process started with PID {proc.pid}")
            return proc, sumo_binary, SUMO_CONFIG_FILE, temp_config
        except Exception as e:
            if DEBUG_MODE:
                print(f"[SUMO Config Test] Failed to start SUMO: {e}")
            # Clean up temp file
            try:
                os.unlink(temp_config)
            except:
                pass
            return None, None, None, None

    proc, sumo_binary, config_file, temp_config = start_sumo_with_config()
    if not proc:
        print("[SUMO Config Test] Could not start SUMO process with configuration file.")
        return False
    connected = False
    try:
        time.sleep(2)  # Additional wait before connecting
        traci.init(port=port)
        connected = True
        if DEBUG_MODE:
            print("[SUMO Config Test] Successfully connected to SUMO via traci with configuration file!")
            print(f"  SUMO binary used: {sumo_binary}")
            print(f"  Configuration file: {config_file}")
            print(f"  SUMO process PID: {proc.pid}")
            print("  SUMO process started with full configuration and connection established.")
        
        # Perform a simple simulation step to verify functionality
        traci.simulationStep()
        if DEBUG_MODE:
            print("  Successfully performed simulation step.")
            
    except Exception as e:
        if DEBUG_MODE:
            print(f"[SUMO Config Test] Failed to connect to SUMO: {e}")
    finally:
        # Always ensure proper cleanup
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
        
        # Clean up temporary config file
        if temp_config:
            try:
                os.unlink(temp_config)
                if DEBUG_MODE:
                    print(f"  Cleaned up temporary config file: {temp_config}")
            except Exception as e:
                if DEBUG_MODE:
                    print(f"  Failed to clean up temp config: {e}")
        
        # Force cleanup port
        kill_processes_on_port(port)
        time.sleep(2)  # Give OS time to release port and clean up
    return connected

def test_sumo_connection_wrapper(tested, passed):
    """
    Run both SUMO connection tests and count as tests.
    """
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
