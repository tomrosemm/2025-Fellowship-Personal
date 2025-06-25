"""
main.py

Purpose:
    Orchestrates the simulation of a privacy-preserving vehicle authentication protocol using Zero-Knowledge Proofs (ZKP) and blockchain logging.
    Demonstrates both a simulated and (eventually) real ZoKrates-based ZKP workflow, as well as simulated and (eventually) real blockchain 
    verification and event logging.
"""

import preliminary_tests

# Breakdown of the workflow, based on the original paper's description:

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
    
    preliminary_tests.testAndScenarioRunner()  # Run preliminary tests and scenarios
