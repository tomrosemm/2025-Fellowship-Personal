"""
zokrates_interface.py

Purpose:
    Provides an interface for generating and verifying zero-knowledge proofs (ZKPs) using ZoKrates, both in simulation and via CLI commands.

Methodology:
    - Simulates ZKP generation by hashing OTP and timestamp.
    - Provides wrapper functions to compile ZoKrates circuits, set up keys, compute witnesses, generate proofs, and verify proofs using the ZoKrates CLI.
    - Designed to be used by Vehicle and RSU classes for proof generation and verification.
"""

import subprocess       # For running ZoKrates CLI commands
import os               # For file path operations (if needed)


def cleanup_zokrates_files():
    files_to_remove = [
        "out",
        "out.r1cs",
        "out.wtns",
        "proving.key",
        "verification.key",
        "witness",
        "proof.json",
        "abi.json"
    ]
    for filename in files_to_remove:
        if os.path.exists(filename):
            os.remove(filename)
            print(f"Removed {filename}")
            

"""
Function: run_zokrates_compile

Compile a ZoKrates circuit file.

Args:
    circuit_path (str): Path to the ZoKrates .zok circuit file.
    
Returns:
    bool: True if compilation succeeds, False otherwise.
    
Side Effects:
    Prints ZoKrates CLI output or error message.
    
Steps:
1. Run the ZoKrates compile command with the given circuit file
2. Print the output from ZoKrates
3. Return True if successful, otherwise print error and return False
"""
def run_zokrates_compile(circuit_path):
    try:
        # Run the ZoKrates compile command with the given circuit file
        result = subprocess.run(
            ["zokrates", "compile", "-i", circuit_path],
            capture_output=True, text=True, check=True
        )
        # Print the output from ZoKrates
        print("ZoKrates compile output:", result.stdout)
        return True
    except Exception as e:
        # Print error if compilation fails
        print("ZoKrates compile failed:", e)
        return False


"""
Function: run_zokrates_setup

Run ZoKrates setup to generate proving and verification keys.

Returns:
    bool: True if setup succeeds, False otherwise.
    
Side Effects:
    Prints ZoKrates CLI output or error message.
    
Steps:
1. Run the ZoKrates setup command
2. Print the output from ZoKrates
3. Return True if successful, otherwise print error and return False
"""
def run_zokrates_setup():
    try:
        # Run the ZoKrates setup command
        result = subprocess.run(
            ["zokrates", "setup"],
            capture_output=True, text=True, check=True
        )
        # Print the output from ZoKrates
        print("ZoKrates setup output:", result.stdout)
        return True
    except Exception as e:
        # Print error if setup fails
        print("ZoKrates setup failed:", e)
        return False


"""
Function: run_zokrates_compute_witness

Compute the witness for a ZoKrates circuit.

Args:
    args (list of str): Arguments to pass to the circuit (e.g., private/public inputs).
    
Returns:
    bool: True if witness computation succeeds, False otherwise.
    
Side Effects:
    Prints ZoKrates CLI output or error message.
Steps:
1. Run the ZoKrates compute-witness command with arguments
2. Print the output from ZoKrates
3. Return True if successful, otherwise print error and return False
"""
def run_zokrates_compute_witness(args):
    try:
        # Run the ZoKrates compute-witness command with arguments
        result = subprocess.run(
            ["zokrates", "compute-witness", "-a"] + args,
            capture_output=True, text=True, check=True
        )
        # Print the output from ZoKrates
        print("ZoKrates compute-witness output:", result.stdout)
        return True
    except Exception as e:
        # Print error if witness computation fails
        print("ZoKrates compute-witness failed:", e)
        return False


"""
Function: run_zokrates_generate_proof

Generate a ZoKrates proof using the computed witness and setup keys.

Returns:
    bool: True if proof generation succeeds, False otherwise.
    
Side Effects:
    Prints ZoKrates CLI output or error message.
    
Steps:
1. Run the ZoKrates generate-proof command
2. Print the output from ZoKrates
3. Return True if successful, otherwise print error and return False
"""
def run_zokrates_generate_proof():
    try:
        # Run the ZoKrates generate-proof command
        result = subprocess.run(
            ["zokrates", "generate-proof"],
            capture_output=True, text=True, check=True
        )
        # Print the output from ZoKrates
        print("ZoKrates generate-proof output:", result.stdout)
        return True
    except Exception as e:
        # Print error if proof generation fails
        print("ZoKrates generate-proof failed:", e)
        return False


"""
Function: run_zokrates_verify

Verify a ZoKrates proof using the verification key.

Returns:
    bool: True if the proof is valid, False otherwise.
    
Side Effects:
    Prints ZoKrates CLI output or error message.
    
Steps:
1. Run the ZoKrates verify command
2. Print the output from ZoKrates
3. Return True if the output contains the success message, otherwise print error and return False
"""
def run_zokrates_verify():
    try:
        # Run the ZoKrates verify command
        result = subprocess.run(
            ["zokrates", "verify"],
            capture_output=True, text=True, check=True
        )
        # Print the output from ZoKrates
        print("ZoKrates verify output:", result.stdout)
        # Check if the output contains the success message
        return ("Proof is valid" in result.stdout) or ("PASSED" in result.stdout)
    except Exception as e:
        # Print error if verification fails
        print("ZoKrates verify failed:", e)
        return False


if __name__ == "__main__":
    # Step 1: Compile the dummy circuit
    print("Compiling dummy.zok...")
    if not run_zokrates_compile("dummy.zok"):
        print("Compilation failed.")
        exit(1)

    # Step 2: Setup
    print("Running setup...")
    if not run_zokrates_setup():
        print("Setup failed.")
        exit(1)

    # Step 3: Compute witness (inputs: a=3, b=4)
    print("Computing witness...")
    if not run_zokrates_compute_witness(["3", "4"]):
        print("Compute witness failed.")
        exit(1)

    # Step 4: Generate proof
    print("Generating proof...")
    if not run_zokrates_generate_proof():
        print("Generate proof failed.")
        exit(1)

    # Step 5: Verify proof
    print("Verifying proof...")
    if run_zokrates_verify():
        print("Proof is valid! Communication with ZoKrates works.")
        cleanup_zokrates_files()
    else:
        print("Proof is invalid or verification failed.")
