import sys
import subprocess
import os
import time
import socket

DEBUG_MODE = False

def set_debug_mode(enabled):
    global DEBUG_MODE
    DEBUG_MODE = enabled

def is_port_available(port):
    """Check if a port is available for use."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('localhost', port))
            return True
    except OSError:
        return False

def wait_for_port_available(port, timeout=10):
    """Wait for a port to become available."""
    start_time = time.time()
    while time.time() - start_time < timeout:
        if is_port_available(port):
            return True
        time.sleep(0.5)
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
    if not wait_for_port_available(port, timeout=10):
        print(f"[SUMO Test] Port {port} is not available after waiting.")
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
            time.sleep(2)
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
            proc.communicate(timeout=5)
            if DEBUG_MODE:
                print("  SUMO process terminated.")
        except Exception as e:
            if DEBUG_MODE:
                print(f"  SUMO process termination error: {e}")
        time.sleep(3)  # Give OS more time to release port and clean up
    return connected

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
    if not wait_for_port_available(port, timeout=10):
        print(f"[SUMO Config Test] Port {port} is not available after waiting.")
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

    def check_if_gui_config(config_file):
        """Check if the config file contains GUI-specific settings."""
        try:
            with open(config_file, 'r') as f:
                content = f.read()
                return 'gui-settings-file' in content or 'viewsettings' in content
        except Exception:
            return False

    def start_sumo_with_config():
        # For config test, always use non-GUI sumo to avoid GUI issues
        sumo_binary = "sumo"
        if DEBUG_MODE:
            print(f"[SUMO Config Test] Using standard sumo binary for config test")
        
        sumo_cmd = [sumo_binary, "-c", SUMO_CONFIG_FILE, "--remote-port", str(port)]
        
        try:
            proc = subprocess.Popen(sumo_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            time.sleep(3)  # Give more time to start
            if proc.poll() is not None:
                # SUMO exited early, print stderr for diagnostics
                stderr = proc.stderr.read().decode()
                print(f"[SUMO Config Test] SUMO exited early. STDERR:\n{stderr}")
                return None, None, None
            if DEBUG_MODE:
                print(f"[SUMO Config Test] SUMO process started with PID {proc.pid}")
            return proc, sumo_binary, SUMO_CONFIG_FILE
        except Exception as e:
            if DEBUG_MODE:
                print(f"[SUMO Config Test] Failed to start SUMO: {e}")
            return None, None, None

    proc, sumo_binary, config_file = start_sumo_with_config()
    if not proc:
        print("[SUMO Config Test] Could not start SUMO process with configuration file.")
        return False
    connected = False
    try:
        traci.init(port=port)
        connected = True
        if DEBUG_MODE:
            print("[SUMO Config Test] Successfully connected to SUMO via traci with configuration file!")
            print(f"  SUMO binary used: {sumo_binary}")
            print(f"  Configuration file: {config_file}")
            print(f"  SUMO process PID: {proc.pid}")
            print("  SUMO process started with full configuration and connection established.")
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
            proc.communicate(timeout=5)
            if DEBUG_MODE:
                print("  SUMO process terminated.")
        except Exception as e:
            if DEBUG_MODE:
                print(f"  SUMO process termination error: {e}")
        time.sleep(3)  # Give OS more time to release port and clean up
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
