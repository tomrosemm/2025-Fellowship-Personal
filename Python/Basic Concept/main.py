import hashlib
import secrets

from vehicle import Vehicle
from rsu import RSU
from zokrates_interface import generate_zkp_proof, run_zokrates_compile, run_zokrates_setup, run_zokrates_compute_witness, run_zokrates_generate_proof, run_zokrates_verify

# Part One

# 1. Vehicle generates an OTP using unique secret and timestamp

# 2. OTP is embedded into a ZKP, proving the OTP valid without revealing the secret

# 3. ZKP is sent to the RSU, where it is verified

# 4. Upon successful verification, the RSU sends a signal to the vehicle authenticating it and proceeding with session

def test_vehicle_rsu_interaction():
    
    # Setup
    vehicle_id = "VEH123"
    vehicle_secret = secrets.token_hex(16)
    vehicle = Vehicle(vehicle_id, vehicle_secret)
    rsu = RSU({vehicle_id: vehicle_secret})

    # Vehicle generates OTP
    otp, timestamp = vehicle.generate_otp()
    print(f"\nOTP: {otp}\n\nTimestamp: {timestamp}\n")

    # Vehicle creates ZKP using ZoKrates interface
    zkp_proof = vehicle.create_zkp(otp, timestamp)
    print(f"ZKP Proof: {zkp_proof}\n")

    # RSU verifies ZKP
    verification_result = rsu.verify_zkp(vehicle_id, zkp_proof, timestamp)
    print(f"Verification result: {verification_result}\n")

    # Simulate RSU authentication signal
    if verification_result:
        print("Vehicle authenticated. Session started.\n")
    else:
        print("Authentication failed.\n")

def test_vehicle_rsu_interaction_simulated():
    """
    Test the workflow using the simulated ZKP (hash-based).
    """
    vehicle_id = "VEH123"
    vehicle_secret = secrets.token_hex(16)
    vehicle = Vehicle(vehicle_id, vehicle_secret)
    rsu = RSU({vehicle_id: vehicle_secret})

    otp, timestamp = vehicle.generate_otp()
    print(f"\n[Simulated] OTP: {otp}\nTimestamp: {timestamp}\n")

    zkp_proof = vehicle.create_zkp(otp, timestamp)
    print(f"[Simulated] ZKP Proof: {zkp_proof}\n")

    verification_result = rsu.verify_zkp(vehicle_id, zkp_proof, timestamp)
    print(f"[Simulated] Verification result: {verification_result}\n")

    if verification_result:
        print("[Simulated] Vehicle authenticated. Session started.\n")
    else:
        print("[Simulated] Authentication failed.\n")

def test_vehicle_rsu_interaction_real():
    """
    Test the workflow using the real ZoKrates CLI (if available).
    """
    vehicle_id = "VEH123"
    vehicle_secret = secrets.token_hex(16)
    vehicle = Vehicle(vehicle_id, vehicle_secret)
    rsu = RSU({vehicle_id: vehicle_secret})

    otp, timestamp = vehicle.generate_otp()
    print(f"\n[Real ZKP] OTP: {otp}\nTimestamp: {timestamp}\n")

    # --- ZoKrates workflow ---
    circuit_path = "otp.zok"  # Path to your ZoKrates circuit file
    # 1. Compile circuit
    if not run_zokrates_compile(circuit_path):
        print("[Real ZKP] Compilation failed.")
        return
    # 2. Setup
    if not run_zokrates_setup():
        print("[Real ZKP] Setup failed.")
        return
    # 3. Compute witness (inputs must match your circuit)
    # Example: args = [otp, timestamp] as strings
    args = [str(otp), str(timestamp)]
    if not run_zokrates_compute_witness(args):
        print("[Real ZKP] Compute witness failed.")
        return
    # 4. Generate proof
    if not run_zokrates_generate_proof():
        print("[Real ZKP] Proof generation failed.")
        return
    # 5. Verify proof
    verification_result = run_zokrates_verify()
    print(f"[Real ZKP] Verification result: {verification_result}\n")

    if verification_result:
        print("[Real ZKP] Vehicle authenticated. Session started.\n")
    else:
        print("[Real ZKP] Authentication failed.\n")

if __name__ == "__main__":
    print("=== Simulated ZKP Test ===")
    test_vehicle_rsu_interaction_simulated()
    # Uncomment the next line to run the real ZoKrates workflow (requires ZoKrates and a valid circuit)
    # print("=== Real ZKP Test ===")
    # test_vehicle_rsu_interaction_real()

# Part Two

# 1. ZKP-OTP proof is submitted to RSU

# 2. RSU invokes a smart contract on the blockchain, verifying the ZKP-OTP proof

# 3. The blockchain logs the event, including anonymized record of the vehicle’s identity and authentication status

# 4. The outcome is returned to the infrastructure, which grants or denies access.