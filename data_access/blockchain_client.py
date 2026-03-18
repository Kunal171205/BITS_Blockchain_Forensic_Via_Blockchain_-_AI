import os
import json
from web3 import Web3
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

RPC_URL = os.getenv("RPC_PROVIDER_URL", "http://127.0.0.1:8545")
PRIVATE_KEY = os.getenv("PRIVATE_KEY")

def get_web3_provider() -> Web3:
    """Initialize and return a Web3 instance."""
    w3 = Web3(Web3.HTTPProvider(RPC_URL))
    if not w3.is_connected():
        raise ConnectionError(f"Failed to connect to the Web3 network at {RPC_URL}")
    return w3

def load_contract_artifact():
    """Load the compiled Hardhat artifact for the DocRegistry contract."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    artifact_path = os.path.join(base_dir, "blockchain", "artifacts", "contracts", "DocRegistry.sol", "DocRegistry.json")
    
    if not os.path.exists(artifact_path):
        raise FileNotFoundError(f"Contract artifact not found at {artifact_path}. Did you run 'npx hardhat compile'?")

    with open(artifact_path, "r") as f:
        artifact = json.load(f)

    return artifact["abi"], artifact["bytecode"]

def deploy_contract(w3: Web3, account_address: str, private_key: str) -> str:
    """
    Deploys the DocRegistry contract to the network.
    
    Returns:
        str: The deployed contract address.
    """
    abi, bytecode = load_contract_artifact()
    DocRegistry = w3.eth.contract(abi=abi, bytecode=bytecode)

    # Build transaction
    nonce = w3.eth.get_transaction_count(account_address)
    tx = DocRegistry.constructor().build_transaction({
        'chainId': w3.eth.chain_id,
        'gasPrice': w3.eth.gas_price,
        'from': account_address,
        'nonce': nonce,
    })
    
    # Sign and send transaction
    signed_tx = w3.eth.account.sign_transaction(tx, private_key=private_key)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction) # Changed to rawTransaction
    
    # Wait for receipt
    print(f"Deploying contract... TX Hash: {tx_hash.hex()}")
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    
    print(f"Contract deployed at {tx_receipt.contractAddress}")
    return tx_receipt.contractAddress

def anchor_document(w3: Web3, contract_address: str, doc_hash_hex: str, account_address: str, private_key: str) -> str:
    """
    Anchors a document hash in the deployed DocRegistry contract.
    
    Args:
        w3: Web3 instance
        contract_address: Address of the deployed contract
        doc_hash_hex: The SHA-256 hash of the document (hex string)
        account_address: The sender address
        private_key: The sender private key
        
    Returns:
        str: Transaction hash of the anchor execution.
    """
    abi, _ = load_contract_artifact()
    contract = w3.eth.contract(address=contract_address, abi=abi)
    
    # Convert hex string to bytes32, ensure it has 0x prefix for web3 to decode properly or handle directly as bytes
    if not doc_hash_hex.startswith("0x"):
        doc_hash_hex = "0x" + doc_hash_hex
    
    doc_hash_bytes = Web3.to_bytes(hexstr=doc_hash_hex)
    
    nonce = w3.eth.get_transaction_count(account_address)
    
    # Build anchor transaction
    tx = contract.functions.anchorDocument(doc_hash_bytes).build_transaction({
        'chainId': w3.eth.chain_id,
        'gasPrice': w3.eth.gas_price,
        'from': account_address,
        'nonce': nonce,
    })
    
    signed_tx = w3.eth.account.sign_transaction(tx, private_key=private_key)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction) # Changed to raw_transaction
    
    print(f"Anchoring document... TX Hash: {tx_hash.hex()}")
    w3.eth.wait_for_transaction_receipt(tx_hash)
    
    return tx_hash.hex()

def verify_document_on_chain(w3: Web3, contract_address: str, doc_hash_hex: str) -> int:
    """
    Verifies if a document has been anchored by querying the contract.
    Returns the timestamp (0 if not anchored).
    """
    abi, _ = load_contract_artifact()
    contract = w3.eth.contract(address=contract_address, abi=abi)
    
    if not doc_hash_hex.startswith("0x"):
        doc_hash_hex = "0x" + doc_hash_hex
        
    doc_hash_bytes = Web3.to_bytes(hexstr=doc_hash_hex)
    
    timestamp = contract.functions.verifyDocument(doc_hash_bytes).call()
    return timestamp
