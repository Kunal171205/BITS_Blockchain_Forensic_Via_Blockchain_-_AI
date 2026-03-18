"""
Quick deploy script: deploys DocumentRegistry to local Ganache and updates .env
"""
import json
import os
from web3 import Web3

RPC_URL = "http://127.0.0.1:7545"
# Ganache deterministic account 0
PRIVATE_KEY = "0x4f3edf983ac636a65a842ce7c78d9aa706d3b113bce9c46f30d7d21715b23b1d"

base_dir = os.path.dirname(os.path.abspath(__file__))
artifact_path = os.path.join(base_dir, "blockchain", "artifacts", "contracts",
                             "DocumentRegistry.sol", "DocumentRegistry.json")

with open(artifact_path) as f:
    artifact = json.load(f)

abi = artifact["abi"]
bytecode = artifact["bytecode"]

w3 = Web3(Web3.HTTPProvider(RPC_URL))
assert w3.is_connected(), "Cannot connect to Ganache"

account = w3.eth.account.from_key(PRIVATE_KEY)
print(f"Deploying from account: {account.address}")

Contract = w3.eth.contract(abi=abi, bytecode=bytecode)
nonce = w3.eth.get_transaction_count(account.address)

tx = Contract.constructor().build_transaction({
    "chainId": w3.eth.chain_id,
    "gasPrice": w3.eth.gas_price,
    "from": account.address,
    "nonce": nonce,
})

signed = w3.eth.account.sign_transaction(tx, private_key=PRIVATE_KEY)
tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
print(f"TX Hash: {tx_hash.hex()}")

receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
contract_address = receipt.contractAddress
print(f"Contract deployed at: {contract_address}")

# Update .env
env_path = os.path.join(base_dir, ".env")
lines = [
    f"RPC_PROVIDER_URL={RPC_URL}\n",
    f"PRIVATE_KEY={PRIVATE_KEY}\n",
    f"CONTRACT_ADDRESS={contract_address}\n",
]
with open(env_path, "w") as f:
    f.writelines(lines)

print(f".env updated with CONTRACT_ADDRESS={contract_address}")
