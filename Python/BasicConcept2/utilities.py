##
# @file utilities.py
# @author Tom Rose
#
# @brief
#   Utility functions for port management, debugging, and console operations.
#   Used by various modules to manage ports, debug output, and perform system-level tasks.
#
# @details
#   - Enable/disable debug mode.
#   - Kill processes using a specific port.
#   - Check port availability and wait for ports to become free.
#   - Clear the console screen.
#   - Check for file existence with descriptive error output.
##

import psutil
import socket
import time
import os

from settings import DEBUG_MODE as DEFAULT_DEBUG_MODE

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
    
    # Initialize killed_any flag as False to track if any processes were killed
    killed_any = False

    # Try to iterate over all running processes
    try:
        
        # Iterate over all running processes, requesting pid, name, and connections info
        for proc in psutil.process_iter(['pid', 'name', 'connections']):
            
            try:
                
                # Get the list of connections for this process
                connections = proc.info['connections']

                # If the process has any connections
                if connections:
                    
                    # Iterate over each connection
                    for conn in connections:
                        
                        # Check if the connection has a local address and the port matches
                        if hasattr(conn, 'laddr') and conn.laddr and conn.laddr.port == port:
                            
                            # If debug mode, print which process is being killed
                            if DEBUG_MODE:
                                print(f"[Port Cleanup] Killing process {proc.info['pid']} ({proc.info['name']}) using port {port}")
                                
                            # Kill the process and set killed_any to True
                            proc.kill()
                            killed_any = True
                            
            # Structure to handle exceptions for processes that may have ended or are inaccessible
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
            
    # Structure to handle any unexpected exceptions during process iteration
    except Exception as e:
        
        # If debug mode is enabled, print the error message
        if DEBUG_MODE:
            print(f"[Port Cleanup] Error during port cleanup: {e}")

    # If any processes were killed, wait for the OS to release the port
    if killed_any:
        print("Wait time begins for processes to die and OS to release port")
        time.sleep(10)
        print("Wait time ends for processes to die and OS to release port")

    # Return True if any processes were killed, False otherwise
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
    
    # Try to create a socket to check if the port is available
    try:
        
        # Create a TCP socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            
            # Attempt to bind to localhost:port
            s.bind(('localhost', port))
            
            # If bind succeeds, port is available; return True
            return True
        
    # If binding fails, port is in use; return False
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
    
    # Record the start time for timeout calculation and initialize attempt counter
    start_time = time.time()
    attempts = 0

    # Loop until timeout expires
    while time.time() - start_time < timeout:
        
        # Check if port is available
        if is_port_available(port):
            
            # If available, return True
            return True

        # Increment attempt counter
        attempts += 1

        # After 3 failed attempts, try to kill processes using the port
        if attempts == 3:
            
            # If debug mode is enabled, print debug info
            if DEBUG_MODE:
                print(f"[Port Management] Port {port} still busy, attempting to kill processes")
            
            # Attempt to kill processes on the port
            killed = kill_processes_on_port(port)
            
            # If processes were killed and debug mode is enabled, print debug info
            if killed and DEBUG_MODE:
                print(f"[Port Management] Killed processes on port {port}")

        # Wait 1 second before next attempt
        time.sleep(1)

    # If timeout expires and port is still not available, return False
    return False


##
# @brief Clears the console screen based on the operating system.
# @details
#   Clears the console using the appropriate command for the OS.
#
# Steps:
#   1. If Windows, use 'cls'.
#   2. Otherwise, use 'clear'.
##
def clear_console():
    
    if os.name == 'nt':
        os.system('cls')
        
    else:
        os.system('clear')


def check_file_exists(filepath, description):
    if not os.path.exists(filepath):
        print(f"[Error] {description} not found: {filepath}")
        return False
    return True

