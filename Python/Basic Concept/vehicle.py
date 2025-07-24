##
# @file vehicle.py
# @author Tom Rose
#
# @brief
#   Defines the Vehicle class, which is responsible for generating one-time passwords (OTPs) and creating zero-knowledge proofs (ZKPs) for authentication.
#
# @details
#   - Each Vehicle instance is initialized with a unique ID and secret.
#   - The vehicle generates an OTP by hashing its secret with the current timestamp.
#   - The vehicle creates a ZKP for the OTP and timestamp using a ZoKrates interface (currently simulated).
##

from otp import generate_otp
from zkp import generate_zkp_proof_real


##
# @class Vehicle
# @brief Represents a vehicle entity capable of generating one-time passwords (OTPs) and creating zero-knowledge proofs (ZKPs)
#   for authentication in a secure protocol.
#
# @details
#   - Initialized with a unique vehicle ID and secret key.
#   - Generates an OTP by hashing its secret with the current Unix timestamp.
#   - Creates a ZKP for the OTP and timestamp using a ZoKrates interface (or a simulated function).
#
# @usage
#   vehicle = Vehicle(vehicle_id, secret)
#   otp, timestamp = vehicle.generate_otp()
#   zkp_proof = vehicle.create_zkp(otp, timestamp)
#
# @param vehicle_id Unique identifier for the vehicle.
# @param secret Secret key unique to the vehicle.
##
class Vehicle:


    ##
    # @brief Initialize a Vehicle instance.
    #
    # @param vehicle_id Unique identifier for the vehicle.
    # @param secret Secret key unique to the vehicle.
    #
    # @details
    #   1. Store the vehicle's ID
    #   2. Store the vehicle's secret
    ##
    def __init__(self, vehicle_id, secret):
        self.vehicle_id = vehicle_id                    # Store the vehicle's ID
        self.secret = secret                            # Store the vehicle's secret


    ##
    # @brief Generate a one-time password (OTP) using the vehicle's secret and current timestamp.
    #
    # @return tuple (otp (str), timestamp (int))
    #
    # @details
    #   1. Get current Unix timestamp as integer
    #   2. Concatenate secret and timestamp, encode to bytes
    #   3. Hash the input to create the OTP
    #   4. Return the OTP and timestamp
    ##
    def generate_otp(self):
        return generate_otp(self.secret)


    ##
    # @brief Create a zero-knowledge proof (ZKP) for the OTP and timestamp using a ZoKrates circuit.
    #
    # @param otp The generated OTP.
    # @param timestamp The timestamp used for OTP.
    # @param circuit_path Path to the ZoKrates .zok circuit file.
    #
    # @return True if proof is valid, False otherwise.
    ##
    def create_zkp(self, otp, timestamp, circuit_path):
        return generate_zkp_proof_real(circuit_path, otp, timestamp)


    ##
    # @brief Generate an OTP as a simple sum for auth.zok experiments.
    #
    # @param timestamp The timestamp to use for OTP. Defaults to None.
    # @return tuple (otp (str), timestamp (int))
    #
    # @details
    #   1. If no timestamp is provided, get the current Unix timestamp as integer
    #   2. Calculate the OTP as the sum of secret and timestamp
    #   3. Return the OTP and timestamp
    ##
    def generate_otp_sum(self, timestamp=None):
        # For auth.zok: otp = int(secret) + timestamp
        if timestamp is None:
            import time
            timestamp = int(time.time())
        otp = str(int(self.secret) + int(timestamp))
        return otp, timestamp


if __name__ == "__main__":
    ## @test Simple test for Vehicle class
    test_vehicle = Vehicle("TEST_VEHICLE", "mysecret")
    otp, timestamp = test_vehicle.generate_otp()
    print(f"[Vehicle] OTP: {otp}\nTimestamp: {timestamp}")
    # Example: use dummy.zok for demonstration
    zkp = test_vehicle.create_zkp(otp, timestamp, "dummy.zok")
    print(f"[Vehicle] ZKP: {zkp}")
