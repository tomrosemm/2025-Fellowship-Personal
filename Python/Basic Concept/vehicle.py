"""
vehicle.py

Purpose:
    Defines the Vehicle class, which is responsible for generating one-time passwords (OTPs) and creating zero-knowledge proofs (ZKPs) for authentication.

Methodology:
    - Each Vehicle instance is initialized with a unique ID and secret.
    - The vehicle generates an OTP by hashing its secret with the current timestamp.
    - The vehicle creates a ZKP for the OTP and timestamp using a ZoKrates interface (simulated or real).
"""

import time  # For generating timestamps
import hashlib  # For hashing secrets and timestamps
from zokrates_interface import generate_zkp_proof  # Import ZKP proof generator

class Vehicle:
    def __init__(self, vehicle_id, secret):
        """
        Initialize a Vehicle instance.

        Args:
            vehicle_id (str): Unique identifier for the vehicle.
            secret (str): Secret key unique to the vehicle.
        """
        self.vehicle_id = vehicle_id  # Store the vehicle's ID
        self.secret = secret  # Store the vehicle's secret

    def generate_otp(self):
        """
        Generate a one-time password (OTP) using the vehicle's secret and current timestamp.

        Returns:
            tuple: (otp (str), timestamp (int))
        """
        timestamp = int(time.time())  # Get current Unix timestamp as integer
        otp_input = f"{self.secret}{timestamp}".encode()  # Concatenate secret and timestamp, encode to bytes
        otp = hashlib.sha256(otp_input).hexdigest()  # Hash the input to create the OTP
        return otp, timestamp  # Return the OTP and timestamp

    def create_zkp(self, otp, timestamp):
        """
        Create a zero-knowledge proof (ZKP) for the OTP and timestamp.

        Args:
            otp (str): The generated OTP.
            timestamp (int): The timestamp used for OTP.

        Returns:
            str: Simulated ZKP proof.
        """
        # Use ZoKrates interface to generate ZKP
        return generate_zkp_proof(otp, timestamp)
