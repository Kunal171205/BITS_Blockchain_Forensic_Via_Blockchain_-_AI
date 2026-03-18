import os
import sys
import argparse
from pydantic import BaseModel, Field
from datetime import datetime

# Add root folder to path to import scripts
base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if base_dir not in sys.path:
    sys.path.append(base_dir)

from data_access.crypto_utils import hash_document
from data_access.blockchain_client import (
    get_web3_provider, 
    deploy_contract, 
    anchor_document, 
    verify_document_on_chain
)
from dotenv import load_dotenv

load_dotenv()

# Pydantic model for validation
class ConfigModel(BaseModel):
    rpc_url: str = Field(default_factory=lambda: os.getenv("RPC_PROVIDER_URL", "http://127.0.0.1:8545"))
    private_key: str = Field(default_factory=lambda: os.getenv("PRIVATE_KEY"))
    document_path: str
    contract_address: str | None = None

def main():
    parser = argparse.ArgumentParser(description="Document Integrity & Anchoring System")
    parser.add_argument("document_path", help="Path to the document to anchor or verify")
    parser.add_argument("--deploy", action="store_true", help="Deploy a new contract")
    parser.add_argument("--contract", type=str, help="Existing contract address")
    args = parser.parse_args()

    # Validate config
    try:
        config = ConfigModel(
            document_path=args.document_path,
            contract_address=args.contract
        )
    except Exception as e:
        print(f"Configuration Error: {e}")
        return

    if not os.path.exists(config.document_path):
        print(f"Error: Document not found at {config.document_path}")
        return

    w3 = get_web3_provider()
    account = w3.eth.account.from_key(config.private_key)
    print(f"Connected to Web3. Using account: {account.address}")
    
    contract_address = config.contract_address

    if args.deploy:
        try:
            print("Deploying new DocRegistry contract...")
            contract_address = deploy_contract(w3, account.address, config.private_key)
        except Exception as e:
            print(f"Error deploying contract: {e}")
            return
            
    if not contract_address:
         print("Error: No contract address provided. Use --deploy or --contract.")
         return

    print("--------------------------------------------------")
    print(f"Processing Document: {config.document_path}")
    
    # 1. Hash the document
    print("Hashing document...")
    doc_hash = hash_document(config.document_path)
    print(f"Document SHA-256 Hash: {doc_hash}")
    
    # 2. Check if already anchored
    try:
        timestamp = verify_document_on_chain(w3, contract_address, doc_hash)
        if timestamp > 0:
            dt = datetime.fromtimestamp(timestamp)
            print("--------------------------------------------------")
            print(f"VERIFIED: Document hash found on-chain!")
            print(f"Anchored Timestamp: {dt.strftime('%Y-%m-%d %H:%M:%S')} (Unix: {timestamp})")
            return
    except Exception as e:
        print(f"Error checking blockchain: {e}")
        return
        
    # 3. Anchor the document
    print("--------------------------------------------------")
    print("Document not found on-chain. Anchoring now...")
    try:
        tx_hash = anchor_document(w3, contract_address, doc_hash, account.address, config.private_key)
        print(f"Document anchored successfully! TX Hash: {tx_hash}")
    except Exception as e:
        print(f"Error anchoring document: {e}")
        return
        
    # 4. Verify again
    print("--------------------------------------------------")
    print("Verifying on-chain record...")
    try:
        timestamp = verify_document_on_chain(w3, contract_address, doc_hash)
        if timestamp > 0:
            dt = datetime.fromtimestamp(timestamp)
            print(f"VERIFICATION SUCCESSFUL!")
            print(f"Anchored Timestamp: {dt.strftime('%Y-%m-%d %H:%M:%S')} (Unix: {timestamp})")
        else:
            print("VERIFICATION FAILED: Could not find the hash on-chain after anchoring.")
    except Exception as e:
        print(f"Error during final verification: {e}")

if __name__ == "__main__":
    main()
