# Blockchain Document Forensic & AI Forgery Detection

A powerful end-to-end system for verifying document authenticity using Deep Learning and Blockchain technology.

## 🚀 Overview

This project detects document tampering and forgery using a multi-model AI pipeline and provides immutable proof of authenticity by anchoring hashes to a local Ganache blockchain.

## ✨ Core Features

- **AI Forgery Detection**: Uses a U-Net segmentation model and structural analysis to identify tampered regions in images.
- **Blockchain Anchoring**: Authentic documents are hashed (SHA-256) and recorded on an Ethereum-based ledger for permanent verification.
- **Unified Dashboard**: A premium Next.js interface for both regular Users (analysis) and Admins (registry management).
- **Secure Authentication**: Role-based access control with JWT and encrypted passwords.

## 🌟 Beyond the Basics: Extraordinary Features

What makes this project stand out compared to standard verification systems:

1. **Multi-Model Forensic Pipeline**: The AI doesn't just look for "edits." It uses a **U-Net Segmentation** model to find pixel-level anomalies, **EasyOCR** to detect text inconsistencies, and **JPEG DCT Structural Analysis** to find hidden artifacts left behind by Photoshop or digital editing tools.
2. **AI-Blockchain Interlock**: We've implemented a "Security Gate" where the system **automatically rejects** any document for anchoring if the AI confidence score falls below a threshold. This ensures only 100% authentic data ever touches the immutable ledger.
3. **Visual "Digital X-Ray"**: Instead of a simple "Pass/Fail," the system generates a **Tamper Heatmap**. This allows investigators to see exactly which parts of a document (like a date, signature, or name) were digitally altered.
4. **Cryptographic Fingerprinting**: By using SHA-256 hashing tied to Smart Contract events, the system creates a "Permanent Birth Certificate" for documents. Even a single pixel change in the original doc will cause a verification failure against the blockchain record.

## 🏗️ Technology Stack

- **Frontend**: Next.js 14, React, Tailwind CSS, Lucide Icons, ethers.js.
- **Backend**: Flask API, Web3.py, PyTorch, EasyOCR, OpenCV.
- **Blockchain**: Ganache (Local RPC), Solidity (Smart Contracts).
- **Database**: MongoDB (User management and audit logs).

## 🛠️ Quick Start

### 1. Prerequisites
- **Python 3.10+** & **Node.js 18+**
- **Ganache** running on `http://localhost:7545`
- **MongoDB** instance (Local or Atlas)

### 2. Installation
```bash
# Install Python dependencies
pip install -r requirements.txt

# Install Frontend dependencies
cd frontend
npm install
```

### 3. Setup
1. Start **Ganache**.
2. Deploy the Smart Contract:
   ```bash
   python deploy_local.py
   ```
3. Update `.env` and `frontend/.env.local` with your database and contract details.

### 4. Running the Project
- **Start Backend**: `python api_server.py`
- **Start Frontend**: `cd frontend && npm run dev`

## 📂 Project Structure
For a detailed breakdown of all files and their roles, see **[FILE_CATEGORIZATION.md](FILE_CATEGORIZATION.md)**.
