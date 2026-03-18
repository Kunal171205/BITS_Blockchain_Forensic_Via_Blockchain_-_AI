import os
import json
import hashlib
from web3 import Web3
from web3.exceptions import ContractLogicError
from dotenv import load_dotenv
from data_access.crypto_utils import hash_document

# Load env variables
load_dotenv()

RPC_URL = os.getenv("RPC_PROVIDER_URL", "http://127.0.0.1:7545")
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS")

def get_ganache_provider() -> Web3:
    w3 = Web3(Web3.HTTPProvider(RPC_URL))
    if not w3.is_connected():
        raise ConnectionError(f"Failed to connect to Ganache at {RPC_URL}. Is it running?")
    return w3

def load_contract_artifact():
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    artifact_path = os.path.join(base_dir, "blockchain", "artifacts", "contracts", "DocumentRegistry.sol", "DocumentRegistry.json")
    
    if not os.path.exists(artifact_path):
        raise FileNotFoundError(f"Contract artifact not found at {artifact_path}. Compile it first.")
        
    with open(artifact_path, "r") as f:
        artifact = json.load(f)
        
    return artifact["abi"]



def verify_and_anchor(file_path: str, ai_verdict: dict) -> dict:
    """
    Called by the UI or Colab integration.
    Hashes the document and registers it on Ganache only if is_tampered is False.
    
    Args:
        file_path (str): The local path to the analyzed file.
        ai_verdict (dict): e.g. {"is_tampered": False, "confidence_score": 98.5}
    """
    print(f"--- Verify and Anchor ---")
    print(f"File: {file_path}")
    print(f"AI Verdict: {ai_verdict}")

    is_tampered = ai_verdict.get("is_tampered", True)
    
    # 1. Hash the local file
    print("Hashing document...")
    doc_hash = hash_document(file_path)
    print(f"SHA-256 Hash: {doc_hash}")

    if is_tampered:
        print("🚨 FORENSIC ALERT: Document is tampered. Blocking blockchain transaction. Logging event locally.")
        return {
            "success": False, 
            "status": "blocked",
            "reason": "Document tampered",
            "hash": doc_hash
        }

    if not PRIVATE_KEY or not CONTRACT_ADDRESS:
        return {
            "success": False, 
            "status": "error",
            "reason": "Missing environment configuration (PRIVATE_KEY or CONTRACT_ADDRESS).",
            "hash": doc_hash
        }

    # 2. Connect to Blockchain
    try:
        w3 = get_ganache_provider()
    except Exception as e:
        return {"success": False, "status": "error", "reason": str(e), "hash": doc_hash}

    account = w3.eth.account.from_key(PRIVATE_KEY)
    abi = load_contract_artifact()
    contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=abi)

    doc_hash_bytes = Web3.to_bytes(hexstr="0x" + doc_hash if not doc_hash.startswith("0x") else doc_hash)

    # 3. Submit Transaction
    print("Authentic document confirmed. Anchoring to Ganache...")
    try:
        nonce = w3.eth.get_transaction_count(account.address)
        
        # Build transaction: anchorDocument(bytes32 docHash)
        tx = contract.functions.anchorDocument(doc_hash_bytes).build_transaction({
            'chainId': w3.eth.chain_id,
            'gasPrice': w3.eth.gas_price,
            'from': account.address,
            'nonce': nonce,
        })
        
        signed_tx = w3.eth.account.sign_transaction(tx, private_key=PRIVATE_KEY)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        
        print(f"Transaction sent! TX Hash: {tx_hash.hex()}")
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        
        if receipt.status == 1:
            print(f"✅ Success! Document anchored in block {receipt.blockNumber}")
            return {
                "success": True, 
                "status": "anchored",
                "tx_hash": tx_hash.hex(), 
                "hash": doc_hash,
                "block": receipt.blockNumber
            }
        else:
            print("❌ Transaction Reverted during execution.")
            return {"success": False, "status": "error", "reason": "Transaction Reverted", "hash": doc_hash}

    except ContractLogicError as e:
        print(f"❌ Transaction Reverted: {e}")
        return {"success": False, "status": "error", "reason": f"Reverted: {e}", "hash": doc_hash}
    except Exception as e:
        print(f"❌ Execution Error: {e}")
        return {"success": False, "status": "error", "reason": str(e), "hash": doc_hash}

def is_hash_anchored(doc_hash: str) -> bool:
    try:
        w3 = get_ganache_provider()
        abi = load_contract_artifact()
        contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=abi)
        doc_hash_bytes = Web3.to_bytes(hexstr="0x" + doc_hash if not doc_hash.startswith("0x") else doc_hash)
        
        timestamp, issuerAddress, isAuthentic = contract.functions.verifyDocument(doc_hash_bytes).call()
        return timestamp > 0
    except:
        return False
