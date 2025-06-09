import hashlib

class RSU:
    def __init__(self, vehicle_secrets):
        # vehicle_secrets: dict mapping vehicle_id to secret
        self.vehicle_secrets = vehicle_secrets

    def verify_zkp(self, vehicle_id, zkp_proof, timestamp):
        secret = self.vehicle_secrets.get(vehicle_id)
        if not secret:
            return False
        otp_input = f"{secret}{timestamp}".encode()
        otp = hashlib.sha256(otp_input).hexdigest()
        expected_zkp = hashlib.sha256(f"{otp}{timestamp}".encode()).hexdigest()
        return zkp_proof == expected_zkp
