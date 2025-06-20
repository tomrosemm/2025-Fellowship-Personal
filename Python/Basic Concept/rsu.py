"""
rsu.py

Purpose:
    Defines the RSU (Roadside Unit) class, which verifies zero-knowledge proofs (ZKPs) submitted by vehicles for authentication.

Methodology:
    - The RSU is initialized with a mapping of vehicle IDs to their secrets.
    - Upon receiving a ZKP, the RSU reconstructs the expected OTP and ZKP using the stored secret and provided timestamp.
    - The RSU compares the received ZKP to the expected value to determine authentication success.
"""

from otp import generate_otp
from zkp import generate_zkp_proof


"""
RSU (Roadside Unit) Class

Function: RSU

Represents a roadside infrastructure unit responsible for authenticating vehicles using zero-knowledge proofs (ZKPs).

Functionality:
    - Initialized with a mapping of vehicle IDs to their corresponding secrets.
    - Upon receiving a ZKP proof, reconstructs the expected OTP and ZKP using the stored secret and provided timestamp.
    - Compares the received ZKP to the expected value to determine authentication success.
    
Usage:
    rsu = RSU(vehicle_secrets)
    is_valid = rsu.verify_zkp(vehicle_id, zkp_proof, timestamp)
    
Args:
    vehicle_secrets (dict): Mapping from vehicle_id (str) to secret (str).
"""
class RSU:
    
    """
    Function: __init__

    Initialize an RSU instance.
    
    Args:
        vehicle_secrets (dict): Mapping from vehicle_id to secret.
    """
    def __init__(self, vehicle_secrets):
        # vehicle_secrets: dict mapping vehicle_id to secret
        self.vehicle_secrets = vehicle_secrets      # Store the mapping


    """
    Function: verify_zkp

    Verify the ZKP proof from a vehicle.
    
    Args:
        vehicle_id (str): The vehicle's unique identifier.
        zkp_proof (str): The ZKP proof to verify.
        timestamp (int): The timestamp used in OTP generation.
    Returns:
        bool: True if the proof is valid, False otherwise.
        
    Steps:
    1. Retrieve the secret for the vehicle
    2. Return False if vehicle_id is unknown
    3. Recreate the OTP input
    4. Hash to get the OTP
    5. Simulate expected ZKP
    6. Return True if proof matches expected
    """
    def verify_zkp(self, vehicle_id, zkp_proof, timestamp):
        secret = self.vehicle_secrets.get(vehicle_id)
        if not secret:
            return False
        otp, _ = generate_otp(secret)
        expected_zkp = generate_zkp_proof(otp, timestamp)
        return zkp_proof == expected_zkp

if __name__ == "__main__":
    # Simple test for RSU class
    vehicle_id = "TEST_VEHICLE"
    secret = "mysecret"
    from vehicle import Vehicle
    vehicle = Vehicle(vehicle_id, secret)
    otp, timestamp = vehicle.generate_otp()
    zkp = vehicle.create_zkp(otp, timestamp)
    rsu = RSU({vehicle_id: secret})
    result = rsu.verify_zkp(vehicle_id, zkp, timestamp)
    print(f"[RSU] Verification result: {result}")

