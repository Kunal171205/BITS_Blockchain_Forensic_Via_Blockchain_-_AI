import os
import sys
import json
from web3 import Web3
from dotenv import load_dotenv

load_dotenv()

RPC_URL = os.getenv("RPC_PROVIDER_URL", "http://127.0.0.1:7545")

def load_contract_artifact():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    artifact_path = os.path.join(base_dir, "blockchain", "artifacts", "contracts", "DocumentRegistry.sol", "DocumentRegistry.json")
    
    if not os.path.exists(artifact_path):
        raise FileNotFoundError(f"Contract artifact not found at {artifact_path}. Compile it first.")
        
    with open(artifact_path, "r") as f:
        artifact = json.load(f)
        
    return artifact["abi"], artifact["bytecode"]

def deploy():
    w3 = Web3(Web3.HTTPProvider(RPC_URL))
    if not w3.is_connected():
        print(f"Failed to connect to Ganache at {RPC_URL}")
        return

    # Use the first ganache account if private key not in env, else use private key
    # Ganache default exposes unlocked accounts
    account_address = w3.eth.accounts[0]
    
    # Save the private key for the bridge controller if we need it
    # We will just print instructions to update .env
    print("Using Ganache primary account:", account_address)
    
    abi, bytecode = load_contract_artifact()
    DocumentRegistry = w3.eth.contract(abi=abi, bytecode=bytecode)
    
    tx_hash = DocumentRegistry.constructor().transact({'from': account_address})
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    
    print(f"Contract Deployed to: {tx_receipt.contractAddress}")
    print("--------------------------------------------------")
    print("UPDATE YOUR .env FILE: ")
    print(f"CONTRACT_ADDRESS={tx_receipt.contractAddress}")

if __name__ == "__main__":
    deploy()
