##
# @file otp.py
# @author Tom Rose
#
# @brief
#   Provides functionality to generate a one-time password (OTP) from a secret and the current timestamp
#   Used by vehicle and authentication modules to create time-based OTPs for secure authentication workflows
#
# @details
#   - Concatenates the provided secret with the current Unix timestamp
#   - Hashes the result using SHA-256 to produce a unique OTP for each time interval
#   - Returns both the OTP and the timestamp used for generation, so that same OTP can be verified later elsewhere
##

## Imports
# Libraries
import time
import hashlib


##
# @brief Generate a one-time password (OTP) using the provided secret and current timestamp
#
# @param secret Secret key unique to the vehicle
# @return tuple (otp (str), timestamp (int))
#
# @details
#   Steps:
#     1. Get current Unix timestamp as an integer
#     2. Concatenate secret and timestamp, then encode to bytes
#     3. Hash the bytes using SHA-256 and get the hex digest as OTP
#     4. Return the OTP and timestamp
##
def generate_otp(secret):
    
    # timestamp - Get current Unix timestamp as an integer (seconds since epoch)
    timestamp = int(time.time())
    
    # otp_input - Concatenate secret and timestamp, then encode as bytes
    otp_input = f"{secret}{timestamp}".encode()
    
    # otp - Hash the bytes using SHA-256 and get the hex digest as OTP
    otp = hashlib.sha256(otp_input).hexdigest()
    
    # Return the OTP and the timestamp used
    return otp, timestamp


## Simple test for OTP generation
if __name__ == "__main__":
    
    ## @var secret
    ## @brief Test secret key for OTP generation
    secret = "mysecret"
    
    ## @var otp
    ## @brief Generate OTP using the test secret
    ## @var timestamp
    ## @brief Get the current timestamp used for OTP generation
    otp, timestamp = generate_otp(secret)
    
    # Print the generated OTP and timestamp
    print(f"[OTP] Generated OTP: {otp}\nTimestamp: {timestamp}")

