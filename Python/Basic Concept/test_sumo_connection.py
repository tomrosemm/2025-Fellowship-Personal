import sys
import os
import subprocess
import time

# Path to SUMO tools (adjust if your SUMO install is elsewhere)
SUMO_TOOLS_PATH = os.getenv("SUMO_TOOLS_PATH", "/usr/share/sumo/tools")
sys.path.append(SUMO_TOOLS_PATH)

try:
    import traci
except ImportError as e:
    print(f"[SUMO Test] Could not import traci: {e}")
    print(f"Check that SUMO_TOOLS_PATH is correct: {SUMO_TOOLS_PATH}")
    exit(1)

# Path to your SUMO network file (must exist in current directory or provide full path)
SUMO_NET_FILE = "simple.net.xml"  # Change if needed

def start_sumo():
    sumo_binary = "sumo"  # Use "sumo-gui" for GUI
    sumo_cmd = [sumo_binary, "-n", SUMO_NET_FILE, "--remote-port", "8813"]
    try:
        proc = subprocess.Popen(sumo_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        time.sleep(2)  # Give SUMO time to start
        return proc
    except Exception as e:
        print(f"[SUMO Test] Failed to start SUMO: {e}")
        return None

def test_sumo_connection():
    proc = start_sumo()
    if not proc:
        print("[SUMO Test] Could not start SUMO process.")
        return
    try:
        traci.init(port=8813)
        print("[SUMO Test] Successfully connected to SUMO via traci!")
        traci.close()
    except Exception as e:
        print(f"[SUMO Test] Failed to connect to SUMO: {e}")
    finally:
        proc.terminate()
        proc.wait()

if __name__ == "__main__":
    test_sumo_connection()
