##
# @file experiment.py
# @author Tom Rose
#
# @brief
#   Provides the Experiment class and logic for running, logging, and reporting ZKP/blockchain experiments
#   involving vehicles, RSUs, ZoKrates circuits, and blockchain verification.
#
# @details
#   - Supports both simulated and ZoKrates-based ZKP workflows
#   - Integrates with vehicle and RSU classes for authentication
#   - Optionally performs blockchain verification and logging
#   - Designed for flexible experiment setup and reporting
##

## Imports
# Libraries
# import secrets
import random
import os
import time
import logging
import datetime
from pathlib import Path

# Classes and functions
from vehicle import Vehicle
from rsu import RSU
from blockchain import simulate_blockchain_verification
from settings import DEBUG_MODE as DEFAULT_DEBUG_MODE

from zokrates_interface import (
    # hex_to_field_array,
    run_zokrates_compile,
    run_zokrates_setup,
    run_zokrates_compute_witness,
    run_zokrates_generate_proof,
    run_zokrates_verify
)


##
# @class Experiment
# @brief Encapsulates logic for running and reporting ZKP/blockchain experiments
##
class Experiment:
    
    ## @var DEBUG_MODE
    ## @brief Control debug output
    DEBUG_MODE = DEFAULT_DEBUG_MODE


    ##
    # @brief Initialize an Experiment instance
    # @param name Name of the experiment
    # @param vehicle_id Vehicle identifier
    # @param rsu_id RSU identifier
    # @param zokrates_circuit_path Path to ZoKrates circuit file (optional)
    # @param use_zokrates Whether to use ZoKrates workflow
    # @param use_blockchain Whether to use blockchain verification
    # @details
    #   - Stores all provided parameters as instance attributes
    #   - Initializes result, timestamp, vehicle, and rsu to None
    #   - Sets up logging for the experiment
    ##
    def __init__(self, name, vehicle_id, rsu_id, zokrates_circuit_path=None, use_zokrates=True, use_blockchain=True):
        
        # Initialize experiment parameters with any provided values
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
    # @brief Set up logging for the experiment
    # @details
    #   - Creates a logs directory if it doesn't exist
    #   - Configures a logger with a timestamped filename
    #   - Sets up logging level and format
    ##
    def setup_logging(self):
        
        # logs_dir - the directory where logs are/will be stored
        logs_dir = Path("logs")
        logs_dir.mkdir(exist_ok=True)
        
        # timestamp_str - formatted string of the current date and time
        timestamp_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # sanitized_name - replaces spaces and slashes in the experiment name to create a valid filename
        sanitized_name = self.name.replace(' ', '_').replace('/', '_')
        
        # log_filename - combines the timestamp and sanitized name to create a unique log filename
        log_filename = f"{timestamp_str}_{sanitized_name}.log"
        
        # log_filepath - the full path to the log file
        log_filepath = logs_dir / log_filename
        
        # Configure logger with the experiment name and set the logging level to DEBUG
        self.logger = logging.getLogger(f"experiment.{self.name}")
        self.logger.setLevel(logging.DEBUG)
        
        # Clear any existing handlers
        if self.logger.hasHandlers():
            self.logger.handlers.clear()
        
        # file_handler - creates a file handler to write logs to the log file and sets its level to DEBUG
        file_handler = logging.FileHandler(log_filepath)
        file_handler.setLevel(logging.DEBUG)
        
        # console_handler - creates a console handler to output logs to the console and sets its level based on DEBUG_MODE
        console_handler = logging.StreamHandler()
        
        # Set console handler level based on DEBUG_MODE
        if self.DEBUG_MODE:
            console_handler.setLevel(logging.INFO)
        else:
            console_handler.setLevel(logging.WARNING)
        
        # formatter - defines the format for log messages, including timestamp, logger name, log level, and message
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        
        # Set the formatter for both file and console handlers
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Add handlers to the logger
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
        # Base log messages
        self.logger.info(f"Experiment {self.name} initialized")
        self.logger.debug(f"Vehicle ID: {self.vehicle_id}, RSU ID: {self.rsu_id}")
        self.logger.debug(f"ZoKrates circuit: {self.zokrates_circuit_path}")
        self.logger.debug(f"Using ZoKrates: {self.use_zokrates}, Using Blockchain: {self.use_blockchain}")


    ##
    # @brief Run the ZoKrates workflow for the experiment
    # @param vehicle Vehicle instance to use for the workflow
    # @return tuple (success (bool), otp (str), timestamp (int))
    # @details
    #   Steps:
    #     1. Determine circuit type and prepare arguments
    #     2. Compile, setup, compute witness, generate proof, and verify using ZoKrates CLI
    #     3. Return success status, OTP, and timestamp
    ##
    def run_zokrates_workflow(self, vehicle):
        
        # Log the start of the ZoKrates workflow
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
        
        # Log the circuit being used
        self.logger.debug(f"Using circuit: {circuit_name}")
        
        ## Based on the circuit, behave differently
        # For dummy.zok, we will use a simple addition circuit
        if circuit_name == "dummy.zok":
            
            # Generate two random integers a and b
            a = random.randint(1, 100)
            b = random.randint(1, 100)
            
            # a + b = otp
            
            # otp - the one-time password generated by the circuit
            otp = str(a + b)
            
            # timestamp - the current time in seconds since epoch
            timestamp = int(time.time())
            
            # args - the arguments to be passed to the ZoKrates circuit
            args = [str(a), str(b)]
            
            # Log the arguments used for the dummy circuit
            self.logger.debug(f"dummy.zok arguments: a={a}, b={b}, otp={otp}, timestamp={timestamp}")
            
            # Print debug information if DEBUG_MODE is enabled
            if self.DEBUG_MODE:
                print(f"[Experiment] Dummy.zok arguments: {args}, otp: {otp}, timestamp: {timestamp}")
        
        # For auth.zok, we will use a more complex authentication circuit; secret, timestamp, otp (all fields, as sum)        
        elif circuit_name == "auth.zok":

            # secret_int - a random integer between 1 and 100000
            secret_int = random.randint(1, 100000)
            
            # Set the vehicle's secret to the generated integer
            vehicle.secret = str(secret_int)
            
            # timestamp - the current time in seconds since epoch
            timestamp = int(time.time())
            
            # otp_int - the one-time password computed as the sum of secret_int and timestamp
            otp_int = secret_int + timestamp
            
            # args - the arguments to be passed to the ZoKrates circuit
            args = [str(secret_int), str(timestamp), str(otp_int)]
            
            # Log the arguments used for the auth circuit
            self.logger.debug(f"auth.zok arguments: secret={secret_int}, timestamp={timestamp}, otp={otp_int}")
            
            # otp - the one-time password as a string
            otp = str(otp_int)
            
            # Print debug information if DEBUG_MODE is enabled
            if self.DEBUG_MODE:
                print(f"[Experiment] Auth.zok arguments: {args}")
        
        # For VtoI_test.zok, we will use a circuit that tests vehicle to infrastructure communication
        elif circuit_name == "VtoI_test.zok":
            
            # sk - a random secret key (sk) for the vehicle, should be > 0 and < 1000
            sk = random.randint(1, 999)
            
            # vid - a random vehicle identifier (vid), should be > 0 and < 1000000000
            vid = random.randint(1, 999999999)
            
            # commitment - the commitment value computed as sk^2 + vid
            commitment = (sk * sk) + vid
            
            # Log the parameters used for the VtoI_test circuit
            self.logger.debug(f"VtoI_test.zok parameters: sk={sk}, vid={vid}, commitment={commitment}")
            
            # args - the arguments to be passed to the ZoKrates circuit
            args = [str(sk), str(vid), str(commitment)]
            
            ## For blockchain verification
            # otp - the one-time password as a string, which is the commitment value
            otp = str(commitment)
            # timestamp - the current time in seconds since epoch
            timestamp = int(time.time())
        
        # If the circuit is not recognized, print an error and return False, None, None        
        else:
            error_msg = f"Unsupported circuit: {circuit_name}"
            self.logger.error(error_msg)
            print(error_msg)
            return False, None, None
        
        ## Run the ZoKrates workflow steps
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
    # @brief Run blockchain verification and logging for the experiment
    # @param vehicle Vehicle instance
    # @param rsu RSU instance
    # @param otp One-time password
    # @param timestamp Timestamp used for OTP
    # @return Outcome of blockchain verification (bool)
    # @details
    #   Steps:
    #     1. Prepare ZKP proof based on circuit type
    #     2. RSU verifies ZKP
    #     3. Simulate blockchain verification and logging
    #     4. Return outcome
    ##
    def run_blockchain_verification(self, vehicle, rsu, otp, timestamp):
        
        # Log the start of blockchain verification
        self.logger.info("Starting blockchain verification")
        
        # If a ZoKrates circuit path is not set, print error and return False, otherwise store the circuit basename
        if self.zokrates_circuit_path:
            
            # circuit_name - the basename of the ZoKrates circuit path, used to determine the circuit type
            circuit_name = os.path.basename(self.zokrates_circuit_path)
            
        else:
            circuit_name = ""
        
        ## Based on the circuit, behave differently
        # For dummy.zok, we will use the sum (a + b = otp)
        if circuit_name == "dummy.zok":
            
            # zkp_proof - the one-time password (otp) generated by the dummy circuit
            zkp_proof = otp
            
            # Log the proof used for the dummy circuit
            self.logger.debug(f"Using dummy.zok proof: {zkp_proof}")
        
        # For auth.zok, we will use a tuple (secret, timestamp, otp)
        elif circuit_name == "auth.zok":
            
            # zkp_proof - a tuple containing the vehicle's secret, timestamp, and otp
            zkp_proof = (vehicle.secret, timestamp, otp)
            
            # Store the vehicle's secret in the RSU for future authentication
            rsu.vehicle_secrets[self.vehicle_id] = vehicle.secret
            
            # Log the arguments used for the auth circuit
            self.logger.debug(f"Using auth.zok proof: secret={vehicle.secret}, timestamp={timestamp}, otp={otp}")
        
        # For VtoI_test.zok, we'll use a tuple (sk, vid, commitment)
        elif circuit_name == "VtoI_test.zok":
        
            # commitment - the commitment value provided by the vehicle, which is used to verify the ZKP
            commitment = int(otp)
            
            # Generate random values for testing; in a real implementation, these would come from the vehicle
            
            # sk - a random secret key (sk) for the vehicle, should be > 0 and < 1000
            sk = random.randint(1, 999)
            
            # commitment = (sk * sk) + vid, so
            # vid - commitment - (sk * sk)
            vid = commitment - (sk * sk)
            
            # zkp_proof - a tuple containing the secret key (sk), vehicle identifier (vid), and commitment
            zkp_proof = (sk, vid, commitment)
            
            # Log the parameters used for the VtoI_test circuit
            self.logger.debug(f"Using VtoI_test.zok proof: sk={sk}, vid={vid}, commitment={commitment}")
        
        # If the circuit isn't recognized
        else:
            
            # zkp_proof - create a generic proof using the vehicle's create_zkp method
            zkp_proof = vehicle.create_zkp(otp, timestamp, self.zokrates_circuit_path)
            
            # Log the generic proof used for unrecognized circuits
            self.logger.debug(f"Using generic proof: {zkp_proof}")
        
        # Log the vehicle ID the ZKP proof is being verified for
        self.logger.info(f"RSU verifying ZKP for vehicle {self.vehicle_id}")
        
        # verification_result - the result of the RSU verifying the ZKP proof using the vehicle ID, zkp_proof, timestamp, and ZoKrates circuit path
        verification_result = rsu.verify_zkp(self.vehicle_id, zkp_proof, timestamp, self.zokrates_circuit_path)
        
        # Log the verification result
        self.logger.debug(f"RSU verification result: {verification_result}")
        
        # Log the simulation of blockchain verification
        self.logger.info("Simulating blockchain verification")
        
        # outcome - the result of simulating the blockchain verification using the vehicle ID, zkp_proof, timestamp, and verification_result
        outcome = simulate_blockchain_verification(self.vehicle_id, str(zkp_proof), timestamp, verification_result)
        
        # Log the outcome of the blockchain verification
        self.logger.info(f"Blockchain verification outcome: {outcome}")
        
        # Return the outcome of the blockchain verification
        return outcome


    ##
    # @brief Run the experiment workflow
    # @details
    #   Steps:
    #     1. Set up vehicle and RSU instances
    #     2. Run ZoKrates workflow if enabled
    #     3. Run blockchain verification if enabled and ZoKrates succeeded
    #     4. Store and print results
    ##
    def run(self):
        
        # Print the experiment name to indicate it is running
        print(f"Running Experiment: {self.name}")
        
        # Log the start of the experiment
        self.logger.info(f"Running experiment: {self.name}")
        
        # If a ZoKrates circuit path is not set, print error and return False, otherwise store the circuit basename
        if self.zokrates_circuit_path:
            
            # circuit_name - the basename of the ZoKrates circuit path, used to determine the circuit type
            circuit_name = os.path.basename(self.zokrates_circuit_path)
            
        else:
            circuit_name = ""
        
        # Based on the circuit, behave differently
        # For dummy.zok, we will use a simple addition circuit and set a secret
        # (This is a dummy circuit for testing purposes)
        if circuit_name == "dummy.zok":
            
            # secret - a dummy secret for the vehicle, can be any value
            secret = "mysecret"
        
        # For auth.zok, we will use a more complex authentication circuit and set a random secret
        # (This is a more complex circuit for authentication purposes)
        elif circuit_name == "auth.zok":
            
            # secret - a random integer between 1 and 100000, simulating a vehicle secret
            secret = str(random.randint(1, 100000))
        
        # For VtoI_test.zok, we'll use a random value within the allowed range
        elif circuit_name == "VtoI_test.zok":
            
            # secret - a random integer between 1 and 999, per constraints of the VtoI_test circuit
            secret = str(random.randint(1, 999))
        
        # Handle any other circuit type with a default secret
        else:
            
            # secret - a random integer between 1 and 1000, simulating a default vehicle secret
            secret = str(random.randint(1, 1000))

        # Log the initialization of the vehicle with the secret
        self.logger.debug(f"Initializing vehicle {self.vehicle_id} with secret {secret}")
        
        # vehicle - an instance of the Vehicle class with the vehicle_id and secret
        vehicle = Vehicle(self.vehicle_id, secret)
        
        # rsu - an instance of the RSU class with the vehicle_id and secret
        rsu = RSU({self.vehicle_id: secret})
        
        # Set the vehicle and RSU instances in the experiment
        self.vehicle = vehicle
        self.rsu = rsu
        
        # otp and timestamp - initialize to None, these will be used to store the results of the ZoKrates workflow
        otp, timestamp = None, None
        
        # success - a boolean to track the success of the ZoKrates workflow
        success = True
        
        # If ZoKrates is enabled, run the ZoKrates workflow
        if self.use_zokrates:
            
            # Log the start of the ZoKrates workflow
            self.logger.info("Running ZoKrates workflow")
            
            # success - the result of running the ZoKrates workflow, which returns a tuple (success, otp, timestamp)
            # otp - the one-time password generated by the ZoKrates workflow
            # timestamp - the timrestamp returned by the ZoKrates workflow
            success, otp, timestamp = self.run_zokrates_workflow(vehicle)
            
            # If the circuit is auth.zok and the ZoKrates workflow succeeded, store the vehicle secret in the RSU
            # This is done to ensure that the RSU has the vehicle's secret for future authentication
            if circuit_name == "auth.zok" and success:
                rsu.vehicle_secrets[self.vehicle_id] = vehicle.secret
                
                # Log the storage of the vehicle secret in the RSU
                self.logger.debug(f"Stored vehicle secret {vehicle.secret} in RSU for vehicle {self.vehicle_id}")
            
            # If the ZoKrates workflow failed, print an error and set the result to False
            # This indicates that the experiment could not be completed successfully
            if not success:
                
                # Log the failure of the ZoKrates workflow
                self.logger.error("ZoKrates workflow failed")
                self.result = False
                
                return
        
        # If blockchain verification is enabled and the ZoKrates workflow succeeded, run the blockchain verification
        # This step is only performed if the ZoKrates workflow was successful, as it relies on the OTP and timestamp generated by ZoKrates
        # If the ZoKrates workflow was not successful, this step is skipped
        if self.use_blockchain and otp is not None and timestamp is not None:
            
            # Log the start of blockchain verification
            self.logger.info("Running blockchain verification")
            
            # Run the blockchain verification and store the result and timestamp
            # This step simulates the verification of the ZKP proof on a blockchain
            self.result = self.run_blockchain_verification(vehicle, rsu, otp, timestamp)
            self.timestamp = timestamp
            
            # If the verification was successful, print a success message
            if self.result:
                
                success_msg = f"Experiment '{self.name}' completed successfully."
                
                # Log the success of the experiment
                self.logger.info(success_msg)
                
                print(success_msg)
            
            # If the verification failed, print an error message
            else:
                
                error_msg = f"Experiment '{self.name}' failed during blockchain verification."
                
                # Log the failure of the experiment
                self.logger.error(error_msg)
                
                print(error_msg)
        
        # If blockchain verification is not enabled or the ZoKrates workflow did not succeed, set the result and timestamp
        else:
            
            self.result = success
            self.timestamp = timestamp
            
            msg = f"Experiment '{self.name}' completed with ZoKrates only."
            
            # Log the completion of the experiment with ZoKrates only
            self.logger.info(msg)
            print(msg)


    ##
    # @brief Print a report of the experiment results
    # @details
    #   Steps:
    #     1. Print experiment result and timestamp
    #     2. Optionally rerun ZoKrates and blockchain workflows for reporting
    #     3. Print completion status
    ##
    def report(self):
        
        # report_msg - a message summarizing the experiment result and timestamp
        report_msg = f"Experiment '{self.name}' result: {self.result}, timestamp: {self.timestamp}"
        
        # Log the report message
        self.logger.info(report_msg)
        
        print(report_msg)
        
        # vehicle - the vehicle instance associated with the experiment
        vehicle = self.vehicle
        
        # rsu - the RSU instance associated with the experiment
        rsu = self.rsu
        
        # If a ZoKrates circuit path is not set, print error and return False, otherwise store the circuit basename
        if self.zokrates_circuit_path:
            
            # circuit_name - the basename of the ZoKrates circuit path, used to determine the circuit type
            circuit_name = os.path.basename(self.zokrates_circuit_path)
            
        else:
            circuit_name = ""
        
        # If ZoKrates is enabled, rerun the ZoKrates workflow
        # This is done to ensure that the ZoKrates workflow is run again for reporting purposes; might not be best implementation long term
        if self.use_zokrates:
            
            # Log the re-running of the ZoKrates workflow for report
            self.logger.info("Re-running ZoKrates workflow for report")
            
            # success, otp, timestamp - the result of running the ZoKrates workflow again
            success, otp, timestamp = self.run_zokrates_workflow(vehicle)
            
            # If the circuit is auth.zok and the ZoKrates workflow succeeded, store the vehicle secret in the RSU
            # This is done to ensure that the RSU has the vehicle's secret for future authentication
            if circuit_name == "auth.zok" and success:
                rsu.vehicle_secrets[self.vehicle_id] = vehicle.secret
                
                # Log the storage of the vehicle secret in the RSU
                self.logger.debug(f"Stored vehicle secret {vehicle.secret} in RSU for vehicle {self.vehicle_id}")
            
            # If the ZoKrates workflow failed, print an error and set the result to False
            # This indicates that the experiment could not be completed successfully
            if not success:
                error_msg = "ZoKrates workflow failed during report generation"
                
                # Log the failure of the ZoKrates workflow
                self.logger.error(error_msg)
                self.result = False
                
                return

        # If blockchain verification is enabled and otp and timestamp are not None, run the blockchain verification
        if self.use_blockchain and otp is not None and timestamp is not None:
            
            # Log the re-running of blockchain verification for report
            self.logger.info("Re-running blockchain verification for report")
            
            # Run the blockchain verification and store the result and timestamp
            self.result = self.run_blockchain_verification(vehicle, rsu, otp, timestamp)
            self.timestamp = timestamp
            
            # If the verification was successful, print a success message
            if self.result:
                success_msg = f"Experiment '{self.name}' completed successfully."
                
                # Log the success of the experiment
                self.logger.info(success_msg)
                print(success_msg)
                
            # If the verification failed, print an error message
            else:
                error_msg = f"Experiment '{self.name}' failed during blockchain verification."
                
                # Log the failure of the experiment
                self.logger.error(error_msg)
                print(error_msg)
        
        # If blockchain verification is not enabled or otp or timestamp are None, set the result and timestamp to the success status and timestamp from the ZoKrates workflow
        else:
            
            self.result = success
            self.timestamp = timestamp
            
            # Print a message indicating that the experiment was completed with ZoKrates only
            msg = f"Experiment '{self.name}' completed with ZoKrates only."
            
            # Log the completion of the experiment with ZoKrates only
            self.logger.info(msg)
            print(msg)

