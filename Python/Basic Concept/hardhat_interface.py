from web3 import Web3

class BlockchainInterface:
    def __init__(self, provider_url, contract_address, abi):
        self.web3 = Web3(Web3.HTTPProvider(provider_url))
        self.contract = self.web3.eth.contract(address=contract_address, abi=abi)

    def log_auth(self, vehicle_hash, timestamp, authenticated, from_address, private_key):
        tx = self.contract.functions.logAuth(vehicle_hash, timestamp, authenticated).build_transaction({
            'from': from_address,
            'nonce': self.web3.eth.get_transaction_count(from_address)
        })
        signed = self.web3.eth.account.sign_transaction(tx, private_key)
        tx_hash = self.web3.eth.send_raw_transaction(signed.rawTransaction)
        return tx_hash.hex()