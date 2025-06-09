"""
rsu.py

Purpose:
    Defines the RSU (Roadside Unit) class, which verifies zero-knowledge proofs (ZKPs) submitted by vehicles for authentication.

Methodology:
    - The RSU is initialized with a mapping of vehicle IDs to their secrets.
    - Upon receiving a ZKP, the RSU reconstructs the expected OTP and ZKP using the stored secret and provided timestamp.
    - The RSU compares the received ZKP to the expected value to determine authentication success.
"""

import hashlib  # For hashing secrets and timestamps

class RSU:
    def __init__(self, vehicle_secrets):
        """
        Initialize an RSU instance.

        Args:
            vehicle_secrets (dict): Mapping from vehicle_id to secret.
        """
        # vehicle_secrets: dict mapping vehicle_id to secret
        self.vehicle_secrets = vehicle_secrets  # Store the mapping

    def verify_zkp(self, vehicle_id, zkp_proof, timestamp):
        """
        Verify the ZKP proof from a vehicle.

        Args:
            vehicle_id (str): The vehicle's unique identifier.
            zkp_proof (str): The ZKP proof to verify.
            timestamp (int): The timestamp used in OTP generation.

        Returns:
            bool: True if the proof is valid, False otherwise.
        """
        secret = self.vehicle_secrets.get(vehicle_id)  # Retrieve the secret for the vehicle
        if not secret:
            return False  # Return False if vehicle_id is unknown
        otp_input = f"{secret}{timestamp}".encode()  # Recreate the OTP input
        otp = hashlib.sha256(otp_input).hexdigest()  # Hash to get the OTP
        expected_zkp = hashlib.sha256(f"{otp}{timestamp}".encode()).hexdigest()  # Simulate expected ZKP
        return zkp_proof == expected_zkp  # Return True if proof matches expected
