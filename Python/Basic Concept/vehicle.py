"""
vehicle.py

Purpose:
    Defines the Vehicle class, which is responsible for generating one-time passwords (OTPs) and creating zero-knowledge proofs (ZKPs) for authentication.

Methodology:
    - Each Vehicle instance is initialized with a unique ID and secret.
    - The vehicle generates an OTP by hashing its secret with the current timestamp.
    - The vehicle creates a ZKP for the OTP and timestamp using a ZoKrates interface (currently simulated).
"""

from otp import generate_otp                                # Import OTP generator
from zkp import generate_zkp_proof                          # Import ZKP proof generator


"""
Vehicle Class

Represents a vehicle entity capable of generating one-time passwords (OTPs) and creating zero-knowledge proofs (ZKPs)
for authentication in a secure protocol.

Functionality:
    - Initialized with a unique vehicle ID and secret key.
    - Generates an OTP by hashing its secret with the current Unix timestamp.
    - Creates a ZKP for the OTP and timestamp using a ZoKrates interface (or a simulated function).
    
Usage:
    vehicle = Vehicle(vehicle_id, secret)
    otp, timestamp = vehicle.generate_otp()
    zkp_proof = vehicle.create_zkp(otp, timestamp)
    
Args:
    vehicle_id (str): Unique identifier for the vehicle.
    secret (str): Secret key unique to the vehicle.
"""
class Vehicle:

    """
    Function: __init__

    Initialize a Vehicle instance.
    
    Args:
        vehicle_id (str): Unique identifier for the vehicle.
        secret (str): Secret key unique to the vehicle.
        
    Steps:
    1. Store the vehicle's ID
    2. Store the vehicle's secret
    """
    def __init__(self, vehicle_id, secret):
        self.vehicle_id = vehicle_id                    # Store the vehicle's ID
        self.secret = secret                            # Store the vehicle's secret


    """
    Function: generate_otp

    Generate a one-time password (OTP) using the vehicle's secret and current timestamp.
    
    Returns:
        tuple: (otp (str), timestamp (int))
    
    Steps:
    1. Get current Unix timestamp as integer
    2. Concatenate secret and timestamp, encode to bytes
    3. Hash the input to create the OTP
    4. Return the OTP and timestamp
    """
    def generate_otp(self):
        return generate_otp(self.secret)


    """
    Function: create_zkp

    Create a zero-knowledge proof (ZKP) for the OTP and timestamp.
    
    Args:
        otp (str): The generated OTP.
        timestamp (int): The timestamp used for OTP.
        
    Returns:
        str: Simulated ZKP proof.
    """
    def create_zkp(self, otp, timestamp):
        return generate_zkp_proof(otp, timestamp)


if __name__ == "__main__":
    # Simple test for Vehicle class
    test_vehicle = Vehicle("TEST_VEHICLE", "mysecret")
    otp, timestamp = test_vehicle.generate_otp()
    print(f"[Vehicle] OTP: {otp}\nTimestamp: {timestamp}")
    zkp = test_vehicle.create_zkp(otp, timestamp)
    print(f"[Vehicle] ZKP: {zkp}")
