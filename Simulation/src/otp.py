"""
otp.py

Purpose:
    Provides a function to generate a one-time password (OTP) using a secret and the current timestamp.
    Used by vehicle and authentication modules to create time-based OTPs for secure authentication workflows.

Methodology:
    - Concatenates the provided secret with the current Unix timestamp.
    - Hashes the result using SHA-256 to produce a unique OTP for each time interval.
    - Returns both the OTP and the timestamp used for generation.
"""

import time
import hashlib

"""
Generate a one-time password (OTP) using the provided secret and current timestamp.
Args:
    secret (str): Secret key unique to the vehicle.
Returns:
    tuple: (otp (str), timestamp (int))
"""
def generate_otp(secret):

    timestamp = int(time.time())                    # Get current Unix timestamp as an integer (seconds since epoch)
    otp_input = f"{secret}{timestamp}".encode()     # Concatenate secret and timestamp, then encode as bytes
    otp = hashlib.sha256(otp_input).hexdigest()     # Hash the bytes using SHA-256 and get the hex digest as OTP
    return otp, timestamp                           # Return the OTP and the timestamp used

if __name__ == "__main__":
    # Simple test for OTP generation
    secret = "mysecret"
    otp, timestamp = generate_otp(secret)
    print(f"[OTP] Generated OTP: {otp}\nTimestamp: {timestamp}")
