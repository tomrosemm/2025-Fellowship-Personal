"""
blockchain_interface.py

Purpose:
    Provides a Python interface for interacting with a blockchain smart contract (e.g., for authentication event logging).
    Uses web3.py to connect to an Ethereum-compatible blockchain and call contract methods.

Methodology:
    - Initializes a Web3 connection and contract instance using provided ABI and address.
    - Provides a method to log authentication attempts by calling the smart contract's logAuth function.
    - Handles transaction signing and sending using a provided private key.
"""

from web3 import Web3

class BlockchainInterface:
    """
    Initialize the BlockchainInterface with provider URL, contract address, and ABI.
    Args:
        provider_url (str): The HTTP provider URL for the blockchain node.
        contract_address (str): The deployed contract address.
        abi (list): The contract ABI.
    """
    def __init__(self, provider_url, contract_address, abi):
        self.web3 = Web3(Web3.HTTPProvider(provider_url))
        self.contract = self.web3.eth.contract(address=contract_address, abi=abi)

    """
    Log an authentication attempt by calling the smart contract's logAuth function.
    Args:
        vehicle_hash (str): The anonymized vehicle hash.
        timestamp (int): The timestamp of the authentication attempt.
        authenticated (bool): Whether authentication succeeded.
        from_address (str): The sender's blockchain address.
        private_key (str): The sender's private key for signing.
    Returns:
        str: The transaction hash.
    """
    def log_auth(self, vehicle_hash, timestamp, authenticated, from_address, private_key):
        tx = self.contract.functions.logAuth(vehicle_hash, timestamp, authenticated).build_transaction({
            'from': from_address,
            'nonce': self.web3.eth.get_transaction_count(from_address)
        })
        signed = self.web3.eth.account.sign_transaction(tx, private_key)
        tx_hash = self.web3.eth.send_raw_transaction(signed.rawTransaction)
        return tx_hash.hex()

if __name__ == "__main__":
    # Simple test for BlockchainInterface instantiation (does not make a real blockchain call)
    provider_url = "http://localhost:8545"
    contract_address = "0x0000000000000000000000000000000000000000"
    abi = []
    try:
        interface = BlockchainInterface(provider_url, contract_address, abi)
        print("[BlockchainInterface] Instantiated successfully (no real call made).")
    except Exception as e:
        print(f"[BlockchainInterface] Instantiation failed: {e}")