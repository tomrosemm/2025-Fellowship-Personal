##
# @file rsu.py
# @author Tom Rose
#
# @brief
#   Defines the RSU (Roadside Unit) class, which verifies zero-knowledge proofs (ZKPs) submitted by vehicles for authentication
#
# @details
#   - The RSU is initialized with a mapping of vehicle IDs to their secrets
#   - Upon receiving a ZKP, the RSU reconstructs the expected OTP and ZKP using the stored secret and provided timestamp
#   - The RSU compares the received ZKP to the expected value to determine authentication success
##

## Imports
# Libraries
import os
import hashlib

# Classes and Functions
# from otp import generate_otp  # Unused currently, but could be used for OTP generation on the RSU side to enable passing less/less final data between vehicle and RSU
from zkp import generate_zkp_proof_real
from vehicle import Vehicle


##
# @class RSU
# @brief Represents a roadside infrastructure unit responsible for authenticating vehicles using zero-knowledge proofs (ZKPs)
#
# @details
#   - Initialized with a mapping of vehicle IDs to their corresponding secrets
#   - Upon receiving a ZKP proof, reconstructs the expected OTP and ZKP using the stored secret and provided timestamp
#   - Compares the received ZKP to the expected value to determine authentication success
#
# Usage:
#   rsu = RSU(vehicle_secrets)
#   is_valid = rsu.verify_zkp(vehicle_id, zkp_proof, timestamp)
#
# @param vehicle_secrets Mapping from vehicle_id (str) to secret (str)
##
class RSU:
    
    
    ##
    # @brief Initialize an RSU instance
    #
    # @param vehicle_secrets Mapping from vehicle_id to secret
    # @param broadcast_range Distance in meters within which RSU can communicate with vehicles (default: 500)
    #
    # @details
    #   Steps:
    #     1. Store the mapping of vehicle IDs to secrets
    ##
    def __init__(self, vehicle_secrets, broadcast_range=500):
        
        # vehicle_secrets - a dict mapping vehicle_id to secret
        self.vehicle_secrets = vehicle_secrets
        
        # broadcast_range - distance in meters within which RSU can communicate with vehicles
        self.broadcast_range = broadcast_range


    ##
    # @brief Verify the ZKP proof from a vehicle using a ZoKrates circuit - used primarily by experiments ecosystem (I couldn't think of a better word, feel free to change)
    #
    # @param vehicle_id The vehicle's unique identifier
    # @param zkp_proof The ZKP proof to verify
    # @param timestamp The timestamp used in OTP generation
    # @param circuit_path Path to the ZoKrates .zok circuit file
    #
    # @return True if the proof is valid, False otherwise
    #
    # @details
    #   Steps:
    #     1. Retrieve the secret for the vehicle
    #     2. Determine circuit type and verify accordingly
    #     3. For auth.zok, check tuple values
    #     4. For dummy.zok, accept any digit string
    #     5. For other circuits, use real ZKP logic
    ##
    def verify_zkp(self, vehicle_id, zkp_proof, timestamp, circuit_path):
        
        # secret - the secret for the vehicle
        secret = self.vehicle_secrets.get(vehicle_id)
        
        # If no secret is found, return False
        if not secret:
            return False
        
        # Determine the circuit type based on the provided path, default to empty string if None
        if circuit_path:
            
            # circuit_name - the name of the circuit file
            circuit_name = os.path.basename(circuit_path)
        
        else:
            circuit_name = ""
        
        # Handle different circuit types
        # If circuit name is auth.zok, expect a tuple (secret, timestamp, otp)
        if circuit_name == "auth.zok":
            
            # Check if zkp_proof is a tuple with 3 elements
            if isinstance(zkp_proof, tuple) and len(zkp_proof) == 3:
                
                # Unpack the ZKP proof
                secret_val, ts_val, otp_val = zkp_proof
                
                # expected_otp - the expected OTP value based on the secret and timestamp
                # Convert values to strings for comparison
                expected_otp = str(int(secret_val) + int(ts_val))
                
                # Check if the provided OTP, secret, and timestamp match the expected values, return True if they do
                return (
                    str(otp_val) == expected_otp and
                    str(secret) == str(secret_val) and
                    int(ts_val) == int(timestamp)
                )
            
            # If zkp_proof is not a valid tuple, return False    
            return False
        
        # If circuit name is dummy.zok, accept any digit string as valid
        elif circuit_name == "dummy.zok":
            
            # For dummy.zok, zkp_proof is the sum (a + b) as a string; accept any sum as valid (since a and b are random and not known to RSU)
            # Optionally, we could pass a and b as part of the proof for stricter checking, but for this, we just check that it's a digit
            return str(zkp_proof).isdigit()
        
        # If circuit name is VtoI_test.zok, expect a tuple (sk, vid, commitment) where sk is the secret key, vid is the vehicle ID, and commitment is the computed value
        elif circuit_name == "VtoI_test.zok":
            
            # Check if zkp_proof is a tuple with 3 elements
            if isinstance(zkp_proof, tuple) and len(zkp_proof) == 3:
                
                # Unpack the ZKP proof
                sk_val, vid_val, commitment_val = zkp_proof
                
                # computed_commitment - compute the commitment using the secret key and vehicle ID
                # Verify the commitment matches
                computed_commitment = (int(sk_val) * int(sk_val)) + int(vid_val)
                
                # Return True if the computed commitment matches the provided commitment
                return str(computed_commitment) == str(commitment_val)
            
            return False
        
        # By default, use real ZKP logic
        else:
            
            # otp_input - the input for OTP generation, which is an encoded combination of the secret and timestamp
            otp_input = f"{secret}{timestamp}".encode()
            
            # otp - Generate the OTP using SHA-256 and hexdigest
            otp = hashlib.sha256(otp_input).hexdigest()
            
            # Generate and return the ZKP proof using the ZoKrates interface
            return generate_zkp_proof_real(circuit_path, otp, timestamp)

## Simple test for RSU class
if __name__ == "__main__":
    
    ## @var vehicle_id
    ## @brief Test vehicle ID
    ## @var secret
    ## @brief Test secret for the vehicle
    ## @var vehicle
    ## @brief Vehicle instance for testing
    vehicle_id = "TEST_VEHICLE"
    secret = "mysecret"
    vehicle = Vehicle(vehicle_id, secret)
    
    ## @var otp
    ## @brief OTP generated by the vehicle
    ## @var timestamp
    ## @brief Timestamp used for OTP generation
    otp, timestamp = vehicle.generate_otp()
    
    ## @var zkp
    ## @brief Zero-knowledge proof generated by the vehicle
    zkp = vehicle.create_zkp(otp, timestamp, "dummy.zok")
    
    ## @var rsu
    ## @brief RSU instance for testing with the vehicle's secret
    rsu = RSU({vehicle_id: secret})
    
    ## @var result
    ## @brief Result of the ZKP verification by the RSU
    result = rsu.verify_zkp(vehicle_id, zkp, timestamp, "dummy.zok")
    
    print(f"[RSU] Verification result: {result}")

