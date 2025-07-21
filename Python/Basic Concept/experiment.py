from vehicle import Vehicle
from rsu import RSU

from zokrates_interface import (
    run_zokrates_compile,
    run_zokrates_setup,
    run_zokrates_compute_witness,
    run_zokrates_generate_proof,
    run_zokrates_verify,
)

from blockchain import simulate_blockchain_verification

class Experiment:
    DEBUG_MODE = False

    def __init__(self, name, vehicle_id, rsu_id, zokrates_circuit_path):
        self.name = name
        self.vehicle_id = vehicle_id
        self.rsu_id = rsu_id
        self.zokrates_circuit_path = zokrates_circuit_path
        self.result = None
        self.timestamp = None

    def run(self):
        print(f"Running Experiment: {self.name}")
        vehicle = Vehicle(self.vehicle_id, "mysecret")
        rsu = RSU({self.vehicle_id: "mysecret"})

        # ZoKrates workflow
        if not run_zokrates_compile(self.zokrates_circuit_path):
            print("ZoKrates compilation failed.")
            self.result = False
            return
        
        if not run_zokrates_setup():
            print("ZoKrates setup failed.")
            self.result = False
            return
        
        otp, timestamp = vehicle.generate_otp()
        args = [otp, str(timestamp)]
        
        if not run_zokrates_compute_witness(args):
            print("Witness computation failed.")
            self.result = False
            return
        
        if not run_zokrates_generate_proof():
            print("Proof generation failed.")
            self.result = False
            return
        
        if not run_zokrates_verify():
            print("Proof verification failed.")
            self.result = False
            return

        # Simulate blockchain verification
        zkp_proof = vehicle.create_zkp(otp, timestamp)
        verification_result = rsu.verify_zkp(self.vehicle_id, zkp_proof, timestamp)
        outcome = simulate_blockchain_verification(self.vehicle_id, zkp_proof, timestamp, verification_result)
        self.result = outcome
        self.timestamp = timestamp
        
        if outcome:
            print(f"Experiment '{self.name}' completed successfully.")
            
        else:
            print(f"Experiment '{self.name}' failed during blockchain verification.")

    def report(self):
        print(f"Experiment '{self.name}' result: {self.result}, timestamp: {self.timestamp}")
