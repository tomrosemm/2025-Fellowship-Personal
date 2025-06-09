"""
main.py

Purpose:
    Orchestrates the simulation of a privacy-preserving vehicle authentication protocol using Zero-Knowledge Proofs (ZKP) and blockchain logging.
    Demonstrates both a simulated and (optionally) real ZoKrates-based ZKP workflow, as well as a simulated blockchain verification and event logging.

Methodology:
    - Vehicles generate OTPs using a secret and timestamp.
    - OTPs are embedded in ZKPs, which are verified by RSUs.
    - Upon successful verification, authentication is simulated.
    - Optionally, the ZKP-OTP proof is submitted to a simulated blockchain smart contract for verification and event logging.
    - The workflow is modularized for easy extension to real ZKP and blockchain implementations.
"""

import hashlib
import secrets

from vehicle import Vehicle
from rsu import RSU
from zokrates_interface import generate_zkp_proof, run_zokrates_compile, run_zokrates_setup, run_zokrates_compute_witness, run_zokrates_generate_proof, run_zokrates_verify
from blockchain import simulate_blockchain_verification

# Part One

# 1. Vehicle generates an OTP using unique secret and timestamp

# 2. OTP is embedded into a ZKP, proving the OTP valid without revealing the secret

# 3. ZKP is sent to the RSU, where it is verified

# 4. Upon successful verification, the RSU sends a signal to the vehicle authenticating it and proceeding with session

# Part Two

# 1. ZKP-OTP proof is submitted to RSU

# 2. RSU invokes a smart contract on the blockchain, verifying the ZKP-OTP proof

# 3. The blockchain logs the event, including anonymized record of the vehicle’s identity and authentication status

# 4. The outcome is returned to the infrastructure, which grants or denies access.

if __name__ == "__main__":
    # Tests moved to preliminary_tests.py
    pass
