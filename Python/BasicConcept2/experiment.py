##
# @file experiment.py
# @author Tom Rose
#
# @brief
#   Provides the Experiment class and logic for running and reporting ZKP/blockchain experiments
#   involving vehicles, RSUs, ZoKrates circuits, and blockchain verification.
#
# @details
#   - Supports both simulated and ZoKrates-based ZKP workflows.
#   - Integrates with vehicle and RSU classes for authentication.
#   - Optionally performs blockchain verification and logging.
#   - Designed for flexible experiment setup and reporting.
##

# Imports
import random
import os
import secrets
import time

from vehicle import Vehicle
from rsu import RSU

from zokrates_interface import (
    run_zokrates_compile,
    run_zokrates_setup,
    run_zokrates_compute_witness,
    run_zokrates_generate_proof,
    run_zokrates_verify,
    hex_to_field_array,
)

from blockchain import simulate_blockchain_verification
from settings import DEBUG_MODE as DEFAULT_DEBUG_MODE


##
# @class Experiment
# @brief Encapsulates logic for running and reporting ZKP/blockchain experiments.
##
class Experiment:
    
    ## @var DEBUG_MODE
    ## @brief Control debug output.
    DEBUG_MODE = DEFAULT_DEBUG_MODE


    ##
    # @brief Initialize an Experiment instance.
    # @param name Name of the experiment.
    # @param vehicle_id Vehicle identifier.
    # @param rsu_id RSU identifier.
    # @param zokrates_circuit_path Path to ZoKrates circuit file (optional).
    # @param use_zokrates Whether to use ZoKrates workflow.
    # @param use_blockchain Whether to use blockchain verification.
    # @details
    #   - Stores all provided parameters as instance attributes.
    #   - Initializes result, timestamp, vehicle, and rsu to None.
    ##
    def __init__(self, name, vehicle_id, rsu_id, zokrates_circuit_path=None, use_zokrates=True, use_blockchain=True):
        
        # Initialize experiment parameters with provided values
        self.name = name
        self.vehicle_id = vehicle_id
        self.rsu_id = rsu_id
        self.zokrates_circuit_path = zokrates_circuit_path
        self.use_zokrates = use_zokrates
        self.use_blockchain = use_blockchain
        
        # Initialize results and instances to None
        self.result = None
        self.timestamp = None
        self.vehicle = None
        self.rsu = None


    ##
    # @brief Run the ZoKrates workflow for the experiment.
    # @param vehicle Vehicle instance to use for the workflow.
    # @return tuple (success (bool), otp (str), timestamp (int))
    # @details
    #   Steps:
    #     1. Determine circuit type and prepare arguments.
    #     2. Compile, setup, compute witness, generate proof, and verify using ZoKrates CLI.
    #     3. Return success status, OTP, and timestamp.
    ##
    def run_zokrates_workflow(self, vehicle):
        
        # Check if ZoKrates circuit path is provided
        if not self.zokrates_circuit_path:
            
            # Print error and return None values if no circuit path is set
            print("No ZoKrates circuit path provided.")
            return False, None, None
        
        # Uses the basename of the circuit path to determine the circuit type
        circuit_name = os.path.basename(self.zokrates_circuit_path)
        
        # Based on the circuit, behave differently
        # For dummy.zok, we will use a simple addition circuit
        if circuit_name == "dummy.zok":
            
            # Generate two random integers a and b
            a = random.randint(1, 100)
            b = random.randint(1, 100)
            
            # a + b = otp
            # Generates and stores the otp and timestamp
            otp = str(a + b)
            timestamp = int(time.time())
            args = [str(a), str(b)]
            
            # Print debug information if DEBUG_MODE is enabled
            if self.DEBUG_MODE:
                print(f"[Experiment] Dummy.zok arguments: {args}, otp: {otp}, timestamp: {timestamp}")
        
        # For auth.zok, we will use a more complex authentication circuit        
        elif circuit_name == "auth.zok":
            
            # For auth.zok: secret, timestamp, otp (all fields, as sum)
            
            # Generate a random secret integer to use as vehicle secret and a timestamp
            secret_int = random.randint(1, 100000)
            vehicle.secret = str(secret_int)
            timestamp = int(time.time())
            
            # Compute the OTP as a sum of secret and timestamp
            otp_int = secret_int + timestamp
            
            # Prepare the arguments for ZoKrates
            args = [str(secret_int), str(timestamp), str(otp_int)]
            
            # Convert the OTP to a string for output
            otp = str(otp_int)
            
            # Print debug information if DEBUG_MODE is enabled
            if self.DEBUG_MODE:
                print(f"[Experiment] Auth.zok arguments: {args}")
        
        # For VtoI_test.zok, we will use a circuit that tests vehicle to infrastructure communication
        elif circuit_name == "VtoI_test.zok":
            
            # Generate random secret key within range
            sk = random.randint(1, 999)
            
            # Generate random vehicle ID within range
            vid = random.randint(1, 999999999)
            
            # Calculate commitment
            commitment = (sk * sk) + vid
            
            # Prepare arguments
            args = [str(sk), str(vid), str(commitment)]
            
            # For blockchain verification
            # Use commitment as OTP for this circuit and set timestamp to current time
            otp = str(commitment)
            timestamp = int(time.time())
        
        # If the circuit is not recognized, print an error and return False, None, None        
        else:
            print(f"Unsupported circuit: {circuit_name}")
            return False, None, None
        
        # Run the ZoKrates workflow steps
        # Attempt to compile the ZoKrates circuit, printing an error and returning False, None, None if it fails
        if not run_zokrates_compile(self.zokrates_circuit_path):
            print("ZoKrates compilation failed.")
            return False, None, None
        
        # Attempt to run the ZoKrates setup, printing an error and returning False, None, None if it fails
        if not run_zokrates_setup():
            print("ZoKrates setup failed.")
            return False, None, None
        
        # Attempt to compute the witness, printing an error and returning False, None, None if it fails
        if not run_zokrates_compute_witness(args):
            print("Witness computation failed.")
            return False, None, None
        
        # Attempt to generate the proof, printing an error and returning False, None, None if it fails
        if not run_zokrates_generate_proof():
            print("Proof generation failed.")
            return False, None, None
        
        # Attempt to verify the proof, printing an error and returning False, None, None if it fails
        if not run_zokrates_verify():
            print("Proof verification failed.")
            return False, None, None
        
        # If all steps succeeded, print success message and return True, otp, timestamp
        return True, otp, timestamp


    ##
    # @brief Run blockchain verification and logging for the experiment.
    # @param vehicle Vehicle instance.
    # @param rsu RSU instance.
    # @param otp One-time password.
    # @param timestamp Timestamp used for OTP.
    # @return Outcome of blockchain verification (bool).
    # @details
    #   Steps:
    #     1. Prepare ZKP proof based on circuit type.
    #     2. RSU verifies ZKP.
    #     3. Simulate blockchain verification and logging.
    #     4. Return outcome.
    ##
    def run_blockchain_verification(self, vehicle, rsu, otp, timestamp):
        
        # If a ZoKrates circuit path is not set, print error and return False, otherwise store the circuit basename
        circuit_name = os.path.basename(self.zokrates_circuit_path) if self.zokrates_circuit_path else ""
        
        # Based on the circuit, behave differently
        # For dummy.zok, we will use the sum (a + b = otp)
        if circuit_name == "dummy.zok":
            
            zkp_proof = otp
        
        # For auth.zok, we will use a tuple (secret, timestamp, otp)
        elif circuit_name == "auth.zok":
            
            zkp_proof = (vehicle.secret, timestamp, otp)
            rsu.vehicle_secrets[self.vehicle_id] = vehicle.secret
        
        # For VtoI_test.zok, we'll use a tuple (sk, vid, commitment)
        elif circuit_name == "VtoI_test.zok":
        
            # Parse the otp which contains our commitment value
            commitment = int(otp)
            
            # Generate random values for testing
            # In a real implementation, these would come from the vehicle
            sk = random.randint(1, 999)
            vid = commitment - (sk * sk)  # Solve for vid: commitment = (sk * sk) + vid
            
            # Create ZKP proof as tuple
            zkp_proof = (sk, vid, commitment)
        
        # If the circuit isn't recognized
        else:
            
            # Set zkp_proof to vehicle.create_zkp(otp, timestamp, self.zokrates_circuit_path)
            zkp_proof = vehicle.create_zkp(otp, timestamp, self.zokrates_circuit_path)
        
        # Set verification result by calling rsu.verify_zkp with vehicle_id, zkp_proof, timestamp, and zokrates_circuit_path
        verification_result = rsu.verify_zkp(self.vehicle_id, zkp_proof, timestamp, self.zokrates_circuit_path)
        
        # Set the outcome of blockchain verification by calling simulate_blockchain_verification with vehicle_id, zkp_proof
        # (converted to string), timestamp, and verification_result, and then returning it
        outcome = simulate_blockchain_verification(self.vehicle_id, str(zkp_proof), timestamp, verification_result)
        
        # Return the outcome of the blockchain verification
        return outcome


    ##
    # @brief Run the experiment workflow.
    # @details
    #   Steps:
    #     1. Set up vehicle and RSU instances.
    #     2. Run ZoKrates workflow if enabled.
    #     3. Run blockchain verification if enabled and ZoKrates succeeded.
    #     4. Store and print results.
    ##
    def run(self):
        
        # Print the experiment name to indicate it is running
        print(f"Running Experiment: {self.name}")
        
        # If a ZoKrates circuit path is not set, print error and return False, otherwise store the circuit basename
        circuit_name = os.path.basename(self.zokrates_circuit_path) if self.zokrates_circuit_path else ""
        
        # Based on the circuit, behave differently
        # For dummy.zok, we will use a simple addition circuit and set a secret
        # (This is a dummy circuit for testing purposes)
        if circuit_name == "dummy.zok":
            secret = "mysecret"
        
        # For auth.zok, we will use a more complex authentication circuit and set a random secret
        # (This is a more complex circuit for authentication purposes)
        elif circuit_name == "auth.zok":
            secret = str(random.randint(1, 100000))
        
        # Initialize the vehicle and RSU instances with the provided vehicle_id and secret
        vehicle = Vehicle(self.vehicle_id, secret)
        rsu = RSU({self.vehicle_id: secret})
        self.vehicle = vehicle
        self.rsu = rsu
        
        # Initialize otp and timestamp to None, and success to True
        # These will be used to store the results of the ZoKrates workflow and blockchain verification
        otp, timestamp = None, None
        success = True
        
        # If ZoKrates is enabled, run the ZoKrates workflow
        if self.use_zokrates:
            
            # Run the ZoKrates workflow and store the success status, otp, and timestamp
            success, otp, timestamp = self.run_zokrates_workflow(vehicle)
            
            # If the circuit is auth.zok and the ZoKrates workflow succeeded, store the vehicle secret in the RSU
            # This is done to ensure that the RSU has the vehicle's secret for future authentication
            if circuit_name == "auth.zok" and success:
                rsu.vehicle_secrets[self.vehicle_id] = vehicle.secret
            
            # If the ZoKrates workflow failed, print an error and set the result to False
            # This indicates that the experiment could not be completed successfully
            if not success:
                self.result = False
                return
        
        # If blockchain verification is enabled and the ZoKrates workflow succeeded, run the blockchain verification
        # This step is only performed if the ZoKrates workflow was successful, as it relies on the OTP and timestamp generated by ZoKrates
        # If the ZoKrates workflow was not successful, this step is skipped
        if self.use_blockchain and otp is not None and timestamp is not None:
            
            # Run the blockchain verification and store the result and timestamp
            # This step simulates the verification of the ZKP proof on a blockchain
            self.result = self.run_blockchain_verification(vehicle, rsu, otp, timestamp)
            self.timestamp = timestamp
            
            # If the verification was successful, print a success message
            if self.result:
                print(f"Experiment '{self.name}' completed successfully.")
            
            # If the verification failed, print an error message
            else:
                print(f"Experiment '{self.name}' failed during blockchain verification.")
        
        # If blockchain verification is not enabled or the ZoKrates workflow did not succeed, set the result and timestamp
        else:
            self.result = success
            self.timestamp = timestamp
            
            print(f"Experiment '{self.name}' completed with ZoKrates only.")


    ##
    # @brief Print a report of the experiment results.
    # @details
    #   Steps:
    #     1. Print experiment result and timestamp.
    #     2. Optionally rerun ZoKrates and blockchain workflows for reporting.
    #     3. Print completion status.
    ##
    def report(self):
        
        # Print the experiment name, result, and timestamp
        print(f"Experiment '{self.name}' result: {self.result}, timestamp: {self.timestamp}")
        
        # Set the vehicle and RSU instances from the experiment
        vehicle = self.vehicle
        rsu = self.rsu
        
        # If a ZoKrates circuit path is not set, print error and return, otherwise store the circuit basename
        circuit_name = os.path.basename(self.zokrates_circuit_path) if self.zokrates_circuit_path else ""
        
        # If ZoKrates is enabled, rerun the ZoKrates workflow
        # This is done to ensure that the ZoKrates workflow is run again for reporting purposes
        if self.use_zokrates:
            
            # Run the ZoKrates workflow and store the success status, otp, and timestamp
            success, otp, timestamp = self.run_zokrates_workflow(vehicle)
            
            # If the circuit is auth.zok and the ZoKrates workflow succeeded, store the vehicle secret in the RSU
            # This is done to ensure that the RSU has the vehicle's secret for future authentication
            if circuit_name == "auth.zok" and success:
                rsu.vehicle_secrets[self.vehicle_id] = vehicle.secret
            
            # If the ZoKrates workflow failed, print an error and set the result to False
            # This indicates that the experiment could not be completed successfully
            if not success:
                self.result = False
                return

        # If blockchain verification is enabled and otp and timestamp are not None, run the blockchain verification
        if self.use_blockchain and otp is not None and timestamp is not None:
            
            # Run the blockchain verification and store the result and timestamp
            self.result = self.run_blockchain_verification(vehicle, rsu, otp, timestamp)
            self.timestamp = timestamp
            
            # If the verification was successful, print a success message
            if self.result:
                print(f"Experiment '{self.name}' completed successfully.")
                
            # If the verification failed, print an error message
            else:
                print(f"Experiment '{self.name}' failed during blockchain verification.")
        
        # If blockchain verification is not enabled or otp or timestamp are None, set the result and timestamp to the success status and timestamp from the ZoKrates workflow
        else:
            
            self.result = success
            self.timestamp = timestamp
            
            # Print a message indicating that the experiment was completed with ZoKrates only
            print(f"Experiment '{self.name}' completed with ZoKrates only.")

