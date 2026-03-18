import os
import json
from web3 import Web3
from web3.exceptions import ContractLogicError
from dotenv import load_dotenv
from src.crypto.hasher import hash_document

# Load env variables for local bridge execution
load_dotenv()

RPC_URL = os.getenv("RPC_PROVIDER_URL", "http://127.0.0.1:7545")
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS")

def get_ganache_provider() -> Web3:
    """Initialize and return a Web3 instance for Ganache."""
    w3 = Web3(Web3.HTTPProvider(RPC_URL))
    if not w3.is_connected():
        raise ConnectionError(f"Failed to connect to Ganache at {RPC_URL}. Is it running?")
    return w3

def load_contract_artifact():
    """Load the compiled Hardhat artifact for the DocumentRegistry contract."""
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    artifact_path = os.path.join(base_dir, "blockchain", "artifacts", "contracts", "DocumentRegistry.sol", "DocumentRegistry.json")
    
    if not os.path.exists(artifact_path):
        raise FileNotFoundError(f"Contract artifact not found at {artifact_path}. Compile it first.")
        
    with open(artifact_path, "r") as f:
        artifact = json.load(f)
        
    return artifact["abi"]

def process_colab_result(ai_output: dict, file_path: str):
    """
    Called by the Google Colab integration cell. 
    Hashes the document and registers it on Ganache if authentic.
    
    Args:
        ai_output (dict): e.g. {"status": "authentic", "confidence": 98}
        file_path (str): The local path to the analyzed file.
    """
    print(f"--- Local Bridge Processing ---")
    print(f"File: {file_path}")
    print(f"AI Verdict: {ai_output}")

    if ai_output.get("status") != "authentic":
        print("❌ Document is NOT authentic (or status missing). Skipping blockchain registration.")
        return {"success": False, "reason": "AI determined document is not authentic."}

    if not PRIVATE_KEY or not CONTRACT_ADDRESS:
        print("❌ Cannot anchor: PRIVATE_KEY or CONTRACT_ADDRESS missing in .env")
        return {"success": False, "reason": "Missing environment configuration."}

    # 1. Hash the local file
    print("Hashing document...")
    doc_hash = hash_document(file_path)
    print(f"SHA-256 Hash: {doc_hash}")

    # 2. Connect to Blockchain
    w3 = get_ganache_provider()
    account = w3.eth.account.from_key(PRIVATE_KEY)
    
    abi = load_contract_artifact()
    contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=abi)

    doc_hash_bytes = Web3.to_bytes(hexstr="0x" + doc_hash if not doc_hash.startswith("0x") else doc_hash)
    confidence = int(ai_output.get("confidence", 0))

    # 3. Submit Transaction
    print("Anchoring to Ganache...")
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
        print(f"✅ Success! Document anchored in block {receipt.blockNumber}")
        
        return {
            "success": True, 
            "tx_hash": tx_hash.hex(), 
            "hash": doc_hash,
            "block": receipt.blockNumber
        }

    except ContractLogicError as e:
        print(f"❌ Transaction Reverted: {e}")
        return {"success": False, "reason": f"Reverted: {e}"}
    except Exception as e:
        print(f"❌ Execution Error: {e}")
        return {"success": False, "reason": str(e)}
