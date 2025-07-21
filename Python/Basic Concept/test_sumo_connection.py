import sys
import os
import subprocess
import time

# Path to SUMO tools (adjust if your SUMO install is elsewhere)
SUMO_TOOLS_PATH = os.getenv("SUMO_TOOLS_PATH", "/home/admin/sumo/tools")
sys.path.append(SUMO_TOOLS_PATH)

try:
    import traci
except ImportError as e:
    print(f"[SUMO Test] Could not import traci: {e}")
    print(f"Check that SUMO_TOOLS_PATH is correct: {SUMO_TOOLS_PATH}")
    exit(1)

# Path to SUMO network file
SUMO_NET_FILE = "simple.net.xml"

def start_sumo():
    
    # Use "sumo-gui" for GUI
    sumo_binary = "sumo"  
    sumo_cmd = [sumo_binary, "-n", SUMO_NET_FILE, "--remote-port", "8813"]
    try:
        proc = subprocess.Popen(sumo_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Give SUMO time to start
        time.sleep(2)
        
        return proc, sumo_binary, SUMO_NET_FILE
    
    except Exception as e:
        print(f"[SUMO Test] Failed to start SUMO: {e}")
        return None, None, None

def test_sumo_connection():
    proc, sumo_binary, net_file = start_sumo()
    if not proc:
        print("[SUMO Test] Could not start SUMO process.")
        return
    try:
        traci.init(port=8813)
        print("[SUMO Test] Successfully connected to SUMO via traci!")
        print(f"  SUMO binary used: {sumo_binary}")
        print(f"  Network file: {net_file}")
        print(f"  SUMO process PID: {proc.pid}")
        print("  SUMO process started and connection established.")
        traci.close()
        print("  SUMO connection closed.")
    except Exception as e:
        print(f"[SUMO Test] Failed to connect to SUMO: {e}")
    finally:
        proc.terminate()
        proc.wait()
        print("  SUMO process terminated.")

if __name__ == "__main__":
    test_sumo_connection()
