import sys
import subprocess
import os
import time

DEBUG_MODE = False

def set_debug_mode(enabled):
    global DEBUG_MODE
    DEBUG_MODE = enabled

def test_sumo_connection():
    """
    Test the connection to SUMO using TraCI.
    Returns:
        bool: True if connection succeeded, False otherwise.
    """
    SUMO_TOOLS_PATH = os.getenv("SUMO_TOOLS_PATH", "/home/admin/sumo/tools")
    sys.path.append(SUMO_TOOLS_PATH)

    try:
        import traci
    except ImportError as e:
        if DEBUG_MODE:
            print(f"[SUMO Test] Could not import traci: {e}")
            print(f"Check that SUMO_TOOLS_PATH is correct: {SUMO_TOOLS_PATH}")
        return False

    SUMO_NET_FILE = "Python/Basic Concept/sumo/simple.net.xml"

    def start_sumo():
        sumo_binary = "sumo"
        sumo_cmd = [sumo_binary, "-n", SUMO_NET_FILE, "--remote-port", "8813"]
        try:
            proc = subprocess.Popen(sumo_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            time.sleep(2)
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
        traci.init(port=8813)
        connected = True
        if DEBUG_MODE:
            print("[SUMO Test] Successfully connected to SUMO via traci!")
            print(f"  SUMO binary used: {sumo_binary}")
            print(f"  Network file: {net_file}")
            print(f"  SUMO process PID: {proc.pid}")
            print("  SUMO process started and connection established.")
        traci.close()
        if DEBUG_MODE:
            print("  SUMO connection closed.")
    except Exception as e:
        if DEBUG_MODE:
            print(f"[SUMO Test] Failed to connect to SUMO: {e}")
    finally:
        try:
            proc.terminate()
            proc.communicate(timeout=5)
            if DEBUG_MODE:
                print("  SUMO process terminated.")
        except Exception as e:
            if DEBUG_MODE:
                print(f"  SUMO process termination error: {e}")
        time.sleep(1)  # Give OS time to release port
    return connected

def test_sumo_connection_wrapper(tested, passed):
    """
    Run the SUMO connection test and count as a test.
    """
    print("\n=== SUMO Connection Test ===")
    tested += 1
    result = test_sumo_connection()
    if result:
        passed += 1
        print("[SUMO Test] SUMO connection test completed successfully.\n")
    else:
        print("[SUMO Test] SUMO connection test failed.\n")
    return tested, passed
