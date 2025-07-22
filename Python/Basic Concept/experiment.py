from vehicle import Vehicle
from rsu import RSU

from zokrates_interface import (
    run_zokrates_compile,
    run_zokrates_setup,
    run_zokrates_compute_witness,
    run_zokrates_generate_proof,
    run_zokrates_verify,
    hex_to_field_array,  # <-- add this import
)

from blockchain import simulate_blockchain_verification
import random

class Experiment:
    DEBUG_MODE = False

    def __init__(self, name, vehicle_id, rsu_id, zokrates_circuit_path=None, use_zokrates=True, use_blockchain=True):
        self.name = name
        self.vehicle_id = vehicle_id
        self.rsu_id = rsu_id
        self.zokrates_circuit_path = zokrates_circuit_path
        self.use_zokrates = use_zokrates
        self.use_blockchain = use_blockchain
        self.result = None
        self.timestamp = None

    def run_zokrates_workflow(self, vehicle):
        if not self.zokrates_circuit_path:
            print("No ZoKrates circuit path provided.")
            return False, None, None
        otp, timestamp = vehicle.generate_otp()
        
        # Convert secret string to hex properly
        secret_bytes = vehicle.secret.encode('utf-8')  # Convert to bytes
        secret_hex = secret_bytes.hex().ljust(64, '0')[:64]  # Convert to hex, then pad
        
        secret_arr = hex_to_field_array(secret_hex)
        otp_arr = hex_to_field_array(otp)
        args = [str(x) for x in secret_arr] + [str(timestamp)] + [str(x) for x in otp_arr]
        
        if not run_zokrates_compile(self.zokrates_circuit_path):
            print("ZoKrates compilation failed.")
            return False, None, None
        if not run_zokrates_setup():
            print("ZoKrates setup failed.")
            return False, None, None
        if not run_zokrates_compute_witness(args):
            print("Witness computation failed.")
            return False, None, None
        if not run_zokrates_generate_proof():
            print("Proof generation failed.")
            return False, None, None
        if not run_zokrates_verify():
            print("Proof verification failed.")
            return False, None, None
        return True, otp, timestamp

    def run_blockchain_verification(self, vehicle, rsu, otp, timestamp):
        # Use the same simulated ZKP logic as preliminary_tests
        zkp_proof = vehicle.create_zkp(otp, timestamp)
        verification_result = rsu.verify_zkp(self.vehicle_id, zkp_proof, timestamp)
        outcome = simulate_blockchain_verification(self.vehicle_id, zkp_proof, timestamp, verification_result)
        return outcome

    def run(self):
        print(f"Running Experiment: {self.name}")
        # Use a random secret for each experiment, and ensure RSU uses the same secret
        secret = "mysecret"
        vehicle = Vehicle(self.vehicle_id, secret)
        rsu = RSU({self.vehicle_id: secret})

        otp, timestamp = None, None
        success = True

        if self.use_zokrates:
            success, otp, timestamp = self.run_zokrates_workflow(vehicle)
            if not success:
                self.result = False
                return

        if self.use_blockchain and otp is not None and timestamp is not None:
            self.result = self.run_blockchain_verification(vehicle, rsu, otp, timestamp)
            self.timestamp = timestamp
            if self.result:
                print(f"Experiment '{self.name}' completed successfully.")
            else:
                print(f"Experiment '{self.name}' failed during blockchain verification.")
        else:
            # If not using blockchain, just report ZoKrates result
            self.result = success
            self.timestamp = timestamp
            print(f"Experiment '{self.name}' completed with ZoKrates only.")

    def report(self):
        print(f"Experiment '{self.name}' result: {self.result}, timestamp: {self.timestamp}")
    def report(self):
        print(f"Experiment '{self.name}' result: {self.result}, timestamp: {self.timestamp}")
