import time
import hashlib

def generate_otp(secret):
    """
    Generate a one-time password (OTP) using the provided secret and current timestamp.

    Args:
        secret (str): Secret key unique to the vehicle.

    Returns:
        tuple: (otp (str), timestamp (int))
    """
    timestamp = int(time.time())
    otp_input = f"{secret}{timestamp}".encode()
    otp = hashlib.sha256(otp_input).hexdigest()
    return otp, timestamp
