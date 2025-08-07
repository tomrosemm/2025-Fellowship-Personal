##
# @file blockchain_interface.py
# @author Tom Rose
#
# @brief
#   Provides a Python interface for interacting with a blockchain smart contract (e.g., for authentication event logging)
#   Uses web3.py to connect to an Ethereum-compatible blockchain and call contract methods
#
# @details
#   - Initializes a Web3 connection and contract instance using provided ABI and address
#   - Provides a method to log authentication attempts by calling the smart contract's logAuth function
#   - Handles transaction signing and sending using a provided private key
##

## Imports
# Libraries
from web3 import Web3
import json

# Classes and functions
from settings import DEBUG_MODE as DEFAULT_DEBUG_MODE, BLOCKCHAIN_PROVIDER_URL

## @var DEBUG_MODE
## @brief Global variable to control debug output.
DEBUG_MODE = DEFAULT_DEBUG_MODE


##
# @brief Enable or disable debug mode for detailed output
#
# @param enabled True to enable debug mode, False to disable
#
# @details
#   Steps:
#     1. Set the global DEBUG_MODE variable to the provided value
##
def set_debug_mode(enabled):
    
    # Set the global DEBUG_MODE variable
    global DEBUG_MODE
    DEBUG_MODE = enabled


##
# @class BlockchainInterface
# @brief Interface for interacting with a blockchain smart contract for authentication event logging
#
# @details
#   Initializes the BlockchainInterface with provider URL, contract address, and ABI
##
class BlockchainInterface:
    
    
    ##
    # @brief Initialize the BlockchainInterface with provider URL, contract address, and ABI
    #
    # @param provider_url The HTTP provider URL for the blockchain node
    # @param contract_address The deployed contract address
    # @param abi The contract ABI
    #
    # @details
    #   Steps:
    #     1. Create a Web3 instance using the provider URL
    #     2. Create a contract instance using the contract address and ABI
    #     3. Optionally print debug info if DEBUG_MODE is enabled
    ##
    def __init__(self, provider_url, contract_address, abi):
        
        # Create a Web3 instance using the provider URL
        self.web3 = Web3(Web3.HTTPProvider(provider_url))
        
        # Create a contract instance using the contract address and ABI
        self.contract = self.web3.eth.contract(address=contract_address, abi=abi)
        
        # If debug mode is enabled, print initialization/debug info
        if DEBUG_MODE:
            print(f"[BlockchainInterface] Initialized with provider_url={provider_url}, contract_address={contract_address}")


    ##
    # @brief Log an authentication attempt by calling the smart contract's logAuth function
    #
    # @param vehicle_hash The anonymized vehicle hash
    # @param timestamp The timestamp of the authentication attempt
    # @param authenticated Whether authentication succeeded
    # @param from_address The sender's blockchain address
    # @param private_key The sender's private key for signing
    #
    # @return The transaction hash.
    #
    # @details
    #   Steps:
    #     1. Build the transaction for logAuth with the provided arguments
    #     2. Sign the transaction using the provided private key
    #     3. Send the raw transaction to the blockchain
    #     4. Optionally print debug info if DEBUG_MODE is enabled
    #     5. Return the transaction hash as a hex string
    ##
    def log_auth(self, vehicle_hash, timestamp, authenticated, from_address, private_key):
        
        # If debug mode is enabled, print the provided parameters being logged
        if DEBUG_MODE:
            print(f"[BlockchainInterface] Logging auth: vehicle_hash={vehicle_hash}, timestamp={timestamp}, authenticated={authenticated}")
        
        # Build the transaction for logAuth with the provided arguments
        tx = self.contract.functions.logAuth(vehicle_hash, timestamp, authenticated).build_transaction({
            'from': from_address,
            'nonce': self.web3.eth.get_transaction_count(from_address)
        })
        
        # Sign the transaction using the provided private key
        signed = self.web3.eth.account.sign_transaction(tx, private_key)
        
        # Hash the transaction and send it to the blockchain
        tx_hash = self.web3.eth.send_raw_transaction(signed.rawTransaction)
        
        # If debug mode is enabled, print the transaction hash
        if DEBUG_MODE:
            print(f"[BlockchainInterface] Sent transaction, hash={tx_hash.hex()}")
        
        # Return the transaction hash as a hex string    
        return tx_hash.hex()


## Example usage after deployment
if __name__ == "__main__":
    
    # After deploying, update these variables with our blockchain details
    # Use provider URL from settings
    provider_url = BLOCKCHAIN_PROVIDER_URL
    
    # contract_address = "0x..."  # Use the address from deployment output
    contract_address = "0x..."
    
    # Load the ABI from the compiled contract JSON file
    with open("path/to/AuthLogger.json") as f:
        abi = json.load(f)["abi"]
    
    # Set debug mode
    set_debug_mode(True)
    
    # Instantiate the BlockchainInterface
    interface = BlockchainInterface(provider_url, contract_address, abi)
    
    # Print a message indicating successful instantiation
    print("[BlockchainInterface] Instantiated successfully (no real call made).")

