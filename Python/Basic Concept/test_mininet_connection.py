import sys
import os

try:
    from mininet.net import Mininet
    from mininet.topo import MinimalTopo
    from mininet.node import OVSController
    from mininet.log import setLogLevel
except ImportError as e:
    print(f"[Mininet Test] Could not import Mininet modules: {e}")
    sys.exit(1)

if os.geteuid() != 0:
    print("** Mininet must run as root. Please run with sudo or as administrator. **")
    sys.exit(1)

def test_mininet_import():
    print("\n=== Mininet Import Test ===")
    try:
        import mininet
        print("[Mininet Test] Mininet imported successfully.")
    except ImportError as e:
        print(f"[Mininet Test] Import failed: {e}")

def test_mininet_network_start_stop():
    print("\n=== Mininet Network Start/Stop Test ===")
    setLogLevel('info')
    try:
        net = Mininet(topo=MinimalTopo(), controller=OVSController)
        net.start()
        print("[Mininet Test] Network started.")
        net.stop()
        print("[Mininet Test] Network stopped.")
    except Exception as e:
        print(f"[Mininet Test] Network start/stop failed: {e}")

def test_mininet_host_ping():
    print("\n=== Mininet Host Ping Test ===")
    setLogLevel('info')
    try:
        net = Mininet(topo=MinimalTopo(), controller=OVSController)
        net.start()
        h1, h2 = net.get('h1'), net.get('h2')
        result = h1.cmd('ping -c1 %s' % h2.IP())
        print(f"[Mininet Test] Ping result:\n{result}")
        net.stop()
    except Exception as e:
        print(f"[Mininet Test] Host ping failed: {e}")

if __name__ == "__main__":
    test_mininet_import()
    test_mininet_network_start_stop()
    test_mininet_host_ping()
