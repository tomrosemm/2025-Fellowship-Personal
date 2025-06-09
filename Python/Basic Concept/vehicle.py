import time
import hashlib
from zokrates_interface import generate_zkp_proof

class Vehicle:
    def __init__(self, vehicle_id, secret):
        self.vehicle_id = vehicle_id
        self.secret = secret

    def generate_otp(self):
        timestamp = int(time.time())
        otp_input = f"{self.secret}{timestamp}".encode()
        otp = hashlib.sha256(otp_input).hexdigest()
        return otp, timestamp

    def create_zkp(self, otp, timestamp):
        # Use ZoKrates interface to generate ZKP
        return generate_zkp_proof(otp, timestamp)
