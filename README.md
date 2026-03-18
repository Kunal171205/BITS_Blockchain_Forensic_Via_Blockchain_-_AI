# Blockchain Document Verification & AI Forgery Detection

This project provides a comprehensive end-to-end system for verifying the authenticity of documents using deep learning models (forgery detection) and anchoring authentic documents immutably to an Ethereum-based blockchain (Ganache).

## 🏗️ Architecture

The codebase strictly follows a **Three-Layer Architecture** to ensure clean separation of concerns, modularity, and maintainability:

1. **Presentation Layer (`presentation/`)**
   - Handles all user interactions and acts as the entry point to the application.
   - `presentation/ui/app.py`: A Streamlit web dashboard for interactive document verification and status checking.
   - `presentation/cli/main_verifier.py`: A command-line interface for deploying contracts and verifying/anchoring documents directly from the terminal.

2. **Business Logic Layer (`business_logic/`)**
   - Contains the core logic and intelligence of the application.
   - `business_logic/services/ml_inference.py`: Orchestrates multiple ML models (Unet, EasyOCR, PyTesseract, structural analysis via OpenCV/JPEG DCT) to generate a comprehensive document tampering and forgery score.
   - `business_logic/services/document_verification.py`: The bridging controller that securely evaluates the AI's verdict and dictates whether a document is allowed to be transmitted to the blockchain layer.

3. **Data Access Layer (`data_access/`)**
   - Manages all external, stateful interactions and infrastructure dependencies.
   - `data_access/blockchain_client.py`: Facilitates Web3 connections locally, handles Smart Contract (DocRegistry) deployments, and anchors SHA-256 hashes to Ganache.
   - `data_access/crypto_utils.py`: Contains cryptographic utilities for securely hashing local files.

## 🚀 Setup & Installation

### Prerequisites
- **Python 3.10+**
- **Node.js** (for hardhat/solidity compilation if necessary)
- **Ganache** (Local blockchain node instance running on `http://127.0.0.1:8545` or `7545`)

### Environment Variables
Create a `.env` file in the root directory (or use `presentation/ui/.env` if inherited) with the following structure:

```env
RPC_PROVIDER_URL=http://127.0.0.1:8545
PRIVATE_KEY=your_ganache_private_key_here
CONTRACT_ADDRESS=deployed_doc_registry_address_here
```

*Note: You can easily deploy a new contract using the CLI verifier below if you don't have a `CONTRACT_ADDRESS` yet.*

## 💻 Usage

### 1. Streamlit Dashboard (UI)
Provide a visual, user-friendly interface to upload documents and trace the live execution of the ML pipeline followed by the blockchain transaction.

```bash
streamlit run presentation/ui/app.py
```

### 2. Command Line Interface (CLI)
The CLI allows power users to deploy new instances of the Smart Contract or process individual files rapidly.

**To deploy a new DocRegistry contract:**
```bash
python presentation/cli/main_verifier.py --deploy "path/to/any/dummy/doc.pdf"
```

**To verify or anchor a document to an existing contract:**
```bash
python presentation/cli/main_verifier.py --contract <0xYourContractAddress> "path/to/document.pdf"
```

## 📓 Notebook Reference
For detailed history and experimental cell execution regarding the initial modeling of the Deep Learning pipeline, refer to the original comprehensive Jupyter Notebook preserved in the root directory: `notebook393b7c93af.ipynb`.
