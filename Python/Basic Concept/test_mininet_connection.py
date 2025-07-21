import sys
import subprocess
import time
import os

try:
    from mininet.net import Mininet
    from mininet.topo import MinimalTopo
    from mininet.node import OVSController
    from mininet.log import setLogLevel
except ImportError as e:
    print(f"[Mininet Test] Could not import Mininet modules: {e}")
    print("Make sure Mininet is installed and available in your Python environment.")
    sys.exit(1)

if os.geteuid() != 0:
    print("** Mininet must run as root. Please run with sudo or as administrator. **")
    sys.exit(1)

def test_mininet_connection():
    print("\n=== Mininet Connection Test ===")
    setLogLevel('info')
    try:
        # Use OVSController instead of default Controller
        net = Mininet(topo=MinimalTopo(), controller=OVSController)
        net.start()
        print("[Mininet Test] Mininet network started.")
        h1, h2 = net.get('h1'), net.get('h2')
        print(f"[Mininet Test] Hosts: {h1.name}, {h2.name}")
        # Test connectivity
        result = h1.cmd('ping -c1 %s' % h2.IP())
        print(f"[Mininet Test] Ping result from {h1.name} to {h2.name}:\n{result}")
        net.stop()
        print("[Mininet Test] Mininet network stopped.")
        print("[Mininet Test] Connection test completed successfully.\n")
    except Exception as e:
        print(f"[Mininet Test] Mininet connection test failed: {e}\n")

if __name__ == "__main__":
    test_mininet_connection()
