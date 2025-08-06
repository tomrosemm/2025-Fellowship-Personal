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
import logging
import datetime
from pathlib import Path

from vehicle import Vehicle
from rsu import RSU
from blockchain import simulate_blockchain_verification
from settings import DEBUG_MODE as DEFAULT_DEBUG_MODE

from zokrates_interface import (
    run_zokrates_compile,
    run_zokrates_setup,
    run_zokrates_compute_witness,
    run_zokrates_generate_proof,
    run_zokrates_verify
    # hex_to_field_array,
)


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
    #   - Sets up logging for the experiment.
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
        
        # Set up logging
        self.setup_logging()

    ##
    # @brief Set up logging for the experiment.
    # @details
    #   - Creates a logs directory if it doesn't exist.
    #   - Configures a logger with a timestamped filename.
    #   - Sets up logging level and format.
    ##
    def setup_logging(self):
        # Create logs directory if it doesn't exist
        logs_dir = Path("logs")
        logs_dir.mkdir(exist_ok=True)
        
        # Create timestamped filename for this experiment's log
        timestamp_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        sanitized_name = self.name.replace(' ', '_').replace('/', '_')
        log_filename = f"{timestamp_str}_{sanitized_name}.log"
        log_filepath = logs_dir / log_filename
        
        # Configure logger
        self.logger = logging.getLogger(f"experiment.{self.name}")
        self.logger.setLevel(logging.DEBUG)
        
        # Clear any existing handlers
        if self.logger.hasHandlers():
            self.logger.handlers.clear()
        
        # Add file handler
        file_handler = logging.FileHandler(log_filepath)
        file_handler.setLevel(logging.DEBUG)
        
        # Add console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO if self.DEBUG_MODE else logging.WARNING)
        
        # Create formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Add handlers to the logger
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
        self.logger.info(f"Experiment {self.name} initialized")
        self.logger.debug(f"Vehicle ID: {self.vehicle_id}, RSU ID: {self.rsu_id}")
        self.logger.debug(f"ZoKrates circuit: {self.zokrates_circuit_path}")
        self.logger.debug(f"Using ZoKrates: {self.use_zokrates}, Using Blockchain: {self.use_blockchain}")


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
        
        self.logger.info("Starting ZoKrates workflow")
        
        # Check if ZoKrates circuit path is provided
        if not self.zokrates_circuit_path:
            
            # Print error and return None values if no circuit path is set
            error_msg = "No ZoKrates circuit path provided."
            self.logger.error(error_msg)
            print(error_msg)
            return False, None, None
        
        # Uses the basename of the circuit path to determine the circuit type
        circuit_name = os.path.basename(self.zokrates_circuit_path)
        self.logger.debug(f"Using circuit: {circuit_name}")
        
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
            
            self.logger.debug(f"dummy.zok arguments: a={a}, b={b}, otp={otp}, timestamp={timestamp}")
            
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
            
            self.logger.debug(f"auth.zok arguments: secret={secret_int}, timestamp={timestamp}, otp={otp_int}")
            
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
            
            self.logger.debug(f"VtoI_test.zok parameters: sk={sk}, vid={vid}, commitment={commitment}")
            
            # Prepare arguments
            args = [str(sk), str(vid), str(commitment)]
            
            # For blockchain verification
            # Use commitment as OTP for this circuit and set timestamp to current time
            otp = str(commitment)
            timestamp = int(time.time())
        
        # If the circuit is not recognized, print an error and return False, None, None        
        else:
            error_msg = f"Unsupported circuit: {circuit_name}"
            self.logger.error(error_msg)
            print(error_msg)
            return False, None, None
        
        # Run the ZoKrates workflow steps
        # Attempt to compile the ZoKrates circuit, printing an error and returning False, None, None if it fails
        self.logger.info("Compiling ZoKrates circuit")
        if not run_zokrates_compile(self.zokrates_circuit_path):
            error_msg = "ZoKrates compilation failed."
            self.logger.error(error_msg)
            print(error_msg)
            return False, None, None
        
        # Attempt to run the ZoKrates setup, printing an error and returning False, None, None if it fails
        self.logger.info("Running ZoKrates setup")
        if not run_zokrates_setup():
            error_msg = "ZoKrates setup failed."
            self.logger.error(error_msg)
            print(error_msg)
            return False, None, None
        
        # Attempt to compute the witness, printing an error and returning False, None, None if it fails
        self.logger.info(f"Computing witness with arguments: {args}")
        if not run_zokrates_compute_witness(args):
            error_msg = "Witness computation failed."
            self.logger.error(error_msg)
            print(error_msg)
            return False, None, None
        
        # Attempt to generate the proof, printing an error and returning False, None, None if it fails
        self.logger.info("Generating proof")
        if not run_zokrates_generate_proof():
            error_msg = "Proof generation failed."
            self.logger.error(error_msg)
            print(error_msg)
            return False, None, None
        
        # Attempt to verify the proof, printing an error and returning False, None, None if it fails
        self.logger.info("Verifying proof")
        if not run_zokrates_verify():
            error_msg = "Proof verification failed."
            self.logger.error(error_msg)
            print(error_msg)
            return False, None, None
        
        # If all steps succeeded, print success message and return True, otp, timestamp
        self.logger.info("ZoKrates workflow completed successfully")
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
        
        self.logger.info("Starting blockchain verification")
        
        # If a ZoKrates circuit path is not set, print error and return False, otherwise store the circuit basename
        circuit_name = os.path.basename(self.zokrates_circuit_path) if self.zokrates_circuit_path else ""
        
        # Based on the circuit, behave differently
        # For dummy.zok, we will use the sum (a + b = otp)
        if circuit_name == "dummy.zok":
            
            zkp_proof = otp
            self.logger.debug(f"Using dummy.zok proof: {zkp_proof}")
        
        # For auth.zok, we will use a tuple (secret, timestamp, otp)
        elif circuit_name == "auth.zok":
            
            zkp_proof = (vehicle.secret, timestamp, otp)
            rsu.vehicle_secrets[self.vehicle_id] = vehicle.secret
            self.logger.debug(f"Using auth.zok proof: secret={vehicle.secret}, timestamp={timestamp}, otp={otp}")
        
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
            self.logger.debug(f"Using VtoI_test.zok proof: sk={sk}, vid={vid}, commitment={commitment}")
        
        # If the circuit isn't recognized
        else:
            
            # Set zkp_proof to vehicle.create_zkp(otp, timestamp, self.zokrates_circuit_path)
            zkp_proof = vehicle.create_zkp(otp, timestamp, self.zokrates_circuit_path)
            self.logger.debug(f"Using generic proof: {zkp_proof}")
        
        # Set verification result by calling rsu.verify_zkp with vehicle_id, zkp_proof, timestamp, and zokrates_circuit_path
        self.logger.info(f"RSU verifying ZKP for vehicle {self.vehicle_id}")
        verification_result = rsu.verify_zkp(self.vehicle_id, zkp_proof, timestamp, self.zokrates_circuit_path)
        self.logger.debug(f"RSU verification result: {verification_result}")
        
        # Set the outcome of blockchain verification by calling simulate_blockchain_verification with vehicle_id, zkp_proof
        # (converted to string), timestamp, and verification_result, and then returning it
        self.logger.info("Simulating blockchain verification")
        outcome = simulate_blockchain_verification(self.vehicle_id, str(zkp_proof), timestamp, verification_result)
        self.logger.info(f"Blockchain verification outcome: {outcome}")
        
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
        self.logger.info(f"Running experiment: {self.name}")
        
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
        
        # For VtoI_test.zok, we'll use a random value within the allowed range
        elif circuit_name == "VtoI_test.zok":
            secret = str(random.randint(1, 999))  # sk should be > 0 and < 1000 as per circuit constraints
        
        # Handle any other circuit type with a default secret
        else:
            secret = str(random.randint(1, 1000))
    
        self.logger.debug(f"Initializing vehicle {self.vehicle_id} with secret {secret}")
        
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
            self.logger.info("Running ZoKrates workflow")
            success, otp, timestamp = self.run_zokrates_workflow(vehicle)
            
            # If the circuit is auth.zok and the ZoKrates workflow succeeded, store the vehicle secret in the RSU
            # This is done to ensure that the RSU has the vehicle's secret for future authentication
            if circuit_name == "auth.zok" and success:
                rsu.vehicle_secrets[self.vehicle_id] = vehicle.secret
                self.logger.debug(f"Stored vehicle secret {vehicle.secret} in RSU for vehicle {self.vehicle_id}")
            
            # If the ZoKrates workflow failed, print an error and set the result to False
            # This indicates that the experiment could not be completed successfully
            if not success:
                self.logger.error("ZoKrates workflow failed")
                self.result = False
                return
        
        # If blockchain verification is enabled and the ZoKrates workflow succeeded, run the blockchain verification
        # This step is only performed if the ZoKrates workflow was successful, as it relies on the OTP and timestamp generated by ZoKrates
        # If the ZoKrates workflow was not successful, this step is skipped
        if self.use_blockchain and otp is not None and timestamp is not None:
            
            # Run the blockchain verification and store the result and timestamp
            # This step simulates the verification of the ZKP proof on a blockchain
            self.logger.info("Running blockchain verification")
            self.result = self.run_blockchain_verification(vehicle, rsu, otp, timestamp)
            self.timestamp = timestamp
            
            # If the verification was successful, print a success message
            if self.result:
                success_msg = f"Experiment '{self.name}' completed successfully."
                self.logger.info(success_msg)
                print(success_msg)
            
            # If the verification failed, print an error message
            else:
                error_msg = f"Experiment '{self.name}' failed during blockchain verification."
                self.logger.error(error_msg)
                print(error_msg)
        
        # If blockchain verification is not enabled or the ZoKrates workflow did not succeed, set the result and timestamp
        else:
            self.result = success
            self.timestamp = timestamp
            
            msg = f"Experiment '{self.name}' completed with ZoKrates only."
            self.logger.info(msg)
            print(msg)


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
        report_msg = f"Experiment '{self.name}' result: {self.result}, timestamp: {self.timestamp}"
        self.logger.info(report_msg)
        print(report_msg)
        
        # Set the vehicle and RSU instances from the experiment
        vehicle = self.vehicle
        rsu = self.rsu
        
        # If a ZoKrates circuit path is not set, print error and return, otherwise store the circuit basename
        circuit_name = os.path.basename(self.zokrates_circuit_path) if self.zokrates_circuit_path else ""
        
        # If ZoKrates is enabled, rerun the ZoKrates workflow
        # This is done to ensure that the ZoKrates workflow is run again for reporting purposes
        if self.use_zokrates:
            
            # Run the ZoKrates workflow and store the success status, otp, and timestamp
            self.logger.info("Re-running ZoKrates workflow for report")
            success, otp, timestamp = self.run_zokrates_workflow(vehicle)
            
            # If the circuit is auth.zok and the ZoKrates workflow succeeded, store the vehicle secret in the RSU
            # This is done to ensure that the RSU has the vehicle's secret for future authentication
            if circuit_name == "auth.zok" and success:
                rsu.vehicle_secrets[self.vehicle_id] = vehicle.secret
                self.logger.debug(f"Stored vehicle secret {vehicle.secret} in RSU for vehicle {self.vehicle_id}")
            
            # If the ZoKrates workflow failed, print an error and set the result to False
            # This indicates that the experiment could not be completed successfully
            if not success:
                error_msg = "ZoKrates workflow failed during report generation"
                self.logger.error(error_msg)
                self.result = False
                return

        # If blockchain verification is enabled and otp and timestamp are not None, run the blockchain verification
        if self.use_blockchain and otp is not None and timestamp is not None:
            
            # Run the blockchain verification and store the result and timestamp
            self.logger.info("Re-running blockchain verification for report")
            self.result = self.run_blockchain_verification(vehicle, rsu, otp, timestamp)
            self.timestamp = timestamp
            
            # If the verification was successful, print a success message
            if self.result:
                success_msg = f"Experiment '{self.name}' completed successfully."
                self.logger.info(success_msg)
                print(success_msg)
                
            # If the verification failed, print an error message
            else:
                error_msg = f"Experiment '{self.name}' failed during blockchain verification."
                self.logger.error(error_msg)
                print(error_msg)
        
        # If blockchain verification is not enabled or otp or timestamp are None, set the result and timestamp to the success status and timestamp from the ZoKrates workflow
        else:
            
            self.result = success
            self.timestamp = timestamp
            
            # Print a message indicating that the experiment was completed with ZoKrates only
            msg = f"Experiment '{self.name}' completed with ZoKrates only."
            self.logger.info(msg)
            print(msg)

