##
# @file zokrates_interface.py
# @author Tom Rose
#
# @brief
#   Provides an interface for generating and verifying zero-knowledge proofs (ZKPs) using ZoKrates, both in simulation and via CLI commands.
#
# @details
#   - Simulates ZKP generation by hashing OTP and timestamp.
#   - Provides wrapper functions to compile ZoKrates circuits, set up keys, compute witnesses, generate proofs, and verify proofs using the ZoKrates CLI.
#   - Designed to be used by Vehicle and RSU classes for proof generation and verification.
##

# Imports
import subprocess
import os

from settings import DEBUG_MODE as DEFAULT_DEBUG_MODE, ZOKRATES_CLEANUP_FILES

## @var DEBUG_MODE
## @brief Global variable to control debug output.
DEBUG_MODE = DEFAULT_DEBUG_MODE

##
# @brief Enable or disable debug mode for detailed output.
# @param enabled True to enable debug mode, False to disable.
##
def set_debug_mode(enabled):
    
    # Set the global DEBUG_MODE variable
    global DEBUG_MODE
    DEBUG_MODE = enabled

##
# @brief Remove ZoKrates-generated files from the current directory.
##
def cleanup_zokrates_files():
    
    # Use files list from settings
    files_to_remove = ZOKRATES_CLEANUP_FILES
    
    # Iterate through the list and remove each file if it exists
    for filename in files_to_remove:
        if os.path.exists(filename):
            os.remove(filename)
            
            # Print debug message with filename if DEBUG_MODE is enabled
            if DEBUG_MODE:
                print(f"Removed {filename}")


##
# @brief Compile a ZoKrates circuit file.
#
# @param circuit_path Path to the ZoKrates .zok circuit file.
# @return True if compilation succeeds, False otherwise.
#
# @details
#   Side Effects:
#     Prints ZoKrates CLI output or error message.
#
#   Steps:
#     1. Run the ZoKrates compile command with the given circuit file
#     2. Print the output from ZoKrates
#     3. Return True if successful, otherwise print error and return False
##
def run_zokrates_compile(circuit_path):
    
    # Try to run the ZoKrates compile command
    try:
        
        # Run the ZoKrates compile command using subprocess with the given circuit file and return True
        result = subprocess.run(
            ["zokrates", "compile", "-i", circuit_path],
            capture_output=True, text=True, check=True
        )
        
        # If DEBUG_MODE is enabled, print the output from ZoKrates
        if DEBUG_MODE:
            print("ZoKrates compile output:", result.stdout)
            
        return True
    
    # If an exception occurs, print the error message if DEBUG_MODE is enabled and return False
    except Exception as e:
        
        if DEBUG_MODE:
            print("ZoKrates compile failed:", e)
            
        return False


##
# @brief Run ZoKrates setup to generate proving and verification keys.
#
# @return True if setup succeeds, False otherwise.
#
# @details
#   Side Effects:
#     Prints ZoKrates CLI output or error message.
#
#   Steps:
#     1. Run the ZoKrates setup command
#     2. Print the output from ZoKrates
#     3. Return True if successful, otherwise print error and return False
##
def run_zokrates_setup():
    
    # Try to run the ZoKrates setup command
    try:
        
        # Run the ZoKrates setup command using subprocess and return True
        result = subprocess.run(
            ["zokrates", "setup"],
            capture_output=True, text=True, check=True
        )
        
        # If DEBUG_MODE is enabled, print the output from ZoKrates
        if DEBUG_MODE:
            print("ZoKrates setup output:", result.stdout)
            
        return True
    
    # If an exception occurs, print the error message if DEBUG_MODE is enabled and return False
    except Exception as e:
        
        if DEBUG_MODE:
            print("ZoKrates setup failed:", e)
            
        return False


##
# @brief Compute the witness for a ZoKrates circuit.
#
# @param args List of arguments to pass to the circuit (e.g., private/public inputs).
# @return True if witness computation succeeds, False otherwise.
#
# @details
#   Side Effects:
#     Prints ZoKrates CLI output or error message.
#
#   Steps:
#     1. Run the ZoKrates compute-witness command with arguments
#     2. Print the output from ZoKrates
#     3. Return True if successful, otherwise print error and return False
##
def run_zokrates_compute_witness(args):
    
    # Try to run the ZoKrates compute-witness command with the provided arguments
    try:
        
        # Run the ZoKrates compute-witness command with arguments via subprocess and return True
        result = subprocess.run(
            ["zokrates", "compute-witness", "-a"] + args,
            capture_output=True, text=True, check=True
        )
        
        # If DEBUG_MODE is enabled, print the output from ZoKrates
        if DEBUG_MODE:
            print("ZoKrates compute-witness output:", result.stdout)
            
        return True
    
    # If an exception occurs, print the error message if DEBUG_MODE is enabled and return False
    except Exception as e:
        
        # If DEBUG_MODE is enabled, print the error message
        if DEBUG_MODE:
            print("ZoKrates compute-witness failed:", e)
            
        return False


##
# @brief Generate a ZoKrates proof using the computed witness and setup keys.
#
# @return True if proof generation succeeds, False otherwise.
#
# @details
#   Side Effects:
#     Prints ZoKrates CLI output or error message.
#
#   Steps:
#     1. Run the ZoKrates generate-proof command
#     2. Print the output from ZoKrates
#     3. Return True if successful, otherwise print error and return False
##
def run_zokrates_generate_proof():
    
    # Try to run the ZoKrates generate-proof command
    try:
        
        # Run the ZoKrates generate-proof command using subprocess and return True
        result = subprocess.run(
            ["zokrates", "generate-proof"],
            capture_output=True, text=True, check=True
        )
        
        # If DEBUG_MODE is enabled, print the output from ZoKrates
        if DEBUG_MODE:
            print("ZoKrates generate-proof output:", result.stdout)
            
        return True
    
    # If an exception occurs, print the error message if DEBUG_MODE is enabled and return False
    except Exception as e:
        
        if DEBUG_MODE:
            print("ZoKrates generate-proof failed:", e)
            
        return False


##
# @brief Verify a ZoKrates proof using the verification key.
#
# @return True if the proof is valid, False otherwise.
#
# @details
#   Side Effects:
#     Prints ZoKrates CLI output or error message.
#
#   Steps:
#     1. Run the ZoKrates verify command
#     2. Print the output from ZoKrates
#     3. Return True if the output contains the success message, otherwise print error and return False
##
def run_zokrates_verify():
    
    # Try to run the ZoKrates verify command
    try:
        
        # Run the ZoKrates verify command using subprocess and capture the output
        result = subprocess.run(
            ["zokrates", "verify"],
            capture_output=True, text=True, check=True
        )
        
        # If DEBUG_MODE is enabled, print the output from ZoKrates
        if DEBUG_MODE:
            print("ZoKrates verify output:", result.stdout)
            
        # Check if the output contains the success message
        return ("Proof is valid" in result.stdout) or ("PASSED" in result.stdout)
    
    # If an exception occurs, print the error message if DEBUG_MODE is enabled and return False
    except Exception as e:
        
        if DEBUG_MODE:
            print("ZoKrates verify failed:", e)
            
        return False


##
# @brief Convert a hex string to an array of 4 field elements (each 64 bits).
#
# @param hex_str Hexadecimal string to convert.
# @return List of 4 integers representing field elements.
##
def hex_to_field_array(hex_str):
    
    # Create an empty list to hold the field elements
    arr = []
    
    # Ensure the hex string is 32 bytes (64 hex characters) long
    padded_hex = hex_str.ljust(32, '0')[:32]
    
    # Convert each 8-character segment to an integer and append to the list
    for i in range(0, 32, 8):
        arr.append(int(padded_hex[i:i+8], 16))
    
    # Return the list of field elements
    return arr


##
# @brief Run complete ZoKrates workflow from compilation through verification
# @param circuit_path Path to ZoKrates circuit file
# @param args List of arguments for witness computation
# @return True if workflow succeeds, False otherwise
# @details
#   Runs complete ZoKrates workflow:
#   1. Compile circuit
#   2. Run setup
#   3. Compute witness
#   4. Generate proof 
#   5. Verify proof
#   6. Clean up artifacts
##
def run_zokrates_workflow(circuit_path, args):
    if not run_zokrates_compile(circuit_path):
        print("[ZoKrates] Compilation failed.")
        return False
    if not run_zokrates_setup():
        print("[ZoKrates] Setup failed.")
        cleanup_zokrates_files()
        return False
    if not run_zokrates_compute_witness(args):
        print("[ZoKrates] Compute witness failed.")
        cleanup_zokrates_files()
        return False
    if not run_zokrates_generate_proof():
        print("[ZoKrates] Proof generation failed.")
        cleanup_zokrates_files()
        return False
    verification_result = run_zokrates_verify()
    cleanup_zokrates_files()
    return verification_result


## Main function to test the ZoKrates interface functionality.
if __name__ == "__main__":
    
    ## @test Main test for ZoKrates interface functionality
    
    # Set debug mode to True for detailed output
    set_debug_mode(True)
    
    # Print initial message
    print("Compiling dummy.zok...")
    
    # Try to run ZoKrates compile command on a dummy circuit file, print error and exit if it fails
    if not run_zokrates_compile("dummy.zok"):
        print("Compilation failed.")
        exit(1)
    
    # Print setup message
    print("Running setup...")
    
    # Try to run ZoKrates setup command, print error and exit if it fails
    if not run_zokrates_setup():
        print("Setup failed.")
        exit(1)
    
    # Print witness computation message
    print("Computing witness...")
    
    # Try to run ZoKrates compute-witness command with example arguments, print error and exit if it fails
    if not run_zokrates_compute_witness(["3", "4"]):
        print("Compute witness failed.")
        exit(1)
        
    # Print proof generation message
    print("Generating proof...")
    
    # Try to run ZoKrates generate-proof command, print error and exit if it fails
    if not run_zokrates_generate_proof():
        print("Generate proof failed.")
        exit(1)
        
    # Print verification message
    print("Verifying proof...")
    
    # Try to run ZoKrates verify command, print success message if it passes, otherwise print error
    if run_zokrates_verify():
        print("Proof is valid! Communication with ZoKrates works.")
        cleanup_zokrates_files()
        
    else:
        print("Proof is invalid or verification failed.")

