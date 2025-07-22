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
import os
import secrets  # <-- add this import
import time  # <-- add this import

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
        self.vehicle = None  # <-- add
        self.rsu = None      # <-- add

    def run_zokrates_workflow(self, vehicle):
        if not self.zokrates_circuit_path:
            print("No ZoKrates circuit path provided.")
            return False, None, None
        circuit_name = os.path.basename(self.zokrates_circuit_path)
        if circuit_name == "dummy.zok":
            otp, timestamp = vehicle.generate_otp()
            args = [str(timestamp), str(int(otp[:2], 16))]
        elif circuit_name == "auth.zok":
            # For auth.zok: secret, timestamp, otp (all fields, as sum)
            secret_int = random.randint(1, 100000)
            vehicle.secret = str(secret_int)
            timestamp = int(time.time())
            otp_int = secret_int + timestamp
            args = [str(secret_int), str(timestamp), str(otp_int)]
            otp = str(otp_int)
            if self.DEBUG_MODE:
                print(f"[Experiment] Auth.zok arguments: {args}")
        else:
            print(f"Unsupported circuit: {circuit_name}")
            return False, None, None
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
        circuit_name = os.path.basename(self.zokrates_circuit_path) if self.zokrates_circuit_path else ""
        if circuit_name == "auth.zok":
            # For auth.zok, ZKP is just the tuple (secret, timestamp, otp)
            zkp_proof = (vehicle.secret, timestamp, otp)
            rsu.vehicle_secrets[self.vehicle_id] = vehicle.secret
        else:
            zkp_proof = vehicle.create_zkp(otp, timestamp)
        verification_result = rsu.verify_zkp(self.vehicle_id, zkp_proof, timestamp)
        outcome = simulate_blockchain_verification(self.vehicle_id, str(zkp_proof), timestamp, verification_result)
        return outcome

    def run(self):
        print(f"Running Experiment: {self.name}")
        circuit_name = os.path.basename(self.zokrates_circuit_path) if self.zokrates_circuit_path else ""
        if circuit_name == "auth.zok":
            secret = str(random.randint(1, 100000))
        else:
            secret = "mysecret"
        vehicle = Vehicle(self.vehicle_id, secret)
        rsu = RSU({self.vehicle_id: secret})
        self.vehicle = vehicle
        self.rsu = rsu
        otp, timestamp = None, None
        success = True
        if self.use_zokrates:
            success, otp, timestamp = self.run_zokrates_workflow(vehicle)
            if circuit_name == "auth.zok" and success:
                rsu.vehicle_secrets[self.vehicle_id] = vehicle.secret
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
            self.result = success
            self.timestamp = timestamp
            print(f"Experiment '{self.name}' completed with ZoKrates only.")

    def report(self):
        print(f"Experiment '{self.name}' result: {self.result}, timestamp: {self.timestamp}")
        vehicle = self.vehicle
        rsu = self.rsu
        circuit_name = os.path.basename(self.zokrates_circuit_path) if self.zokrates_circuit_path else ""
        if self.use_zokrates:
            success, otp, timestamp = self.run_zokrates_workflow(vehicle)
            if circuit_name == "auth.zok" and success:
                rsu.vehicle_secrets[self.vehicle_id] = vehicle.secret
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
            self.result = success
            self.timestamp = timestamp
            print(f"Experiment '{self.name}' completed with ZoKrates only.")
            self.timestamp = timestamp
            print(f"Experiment '{self.name}' completed with ZoKrates only.")
