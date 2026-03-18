"""
Flask API Server - Connects Next.js frontend to the real ML inference pipeline.
Run with: python api_server.py
"""
import os
import sys
import json
import base64
import io
import tempfile
import numpy as np
import cv2
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image as PILImage

# Add root to path
base_dir = os.path.dirname(os.path.abspath(__file__))
if base_dir not in sys.path:
    sys.path.insert(0, base_dir)

from business_logic.services.ml_inference import run_inference
from business_logic.services.document_verification import verify_and_anchor, is_hash_anchored
from data_access.crypto_utils import hash_document

# --- Admin Registry Persistence ---
ADMIN_REGISTRY_PATH = os.path.join(base_dir, "admin_registry.json")

def load_admin_registry() -> list:
    """Load the admin document registry from disk."""
    if os.path.exists(ADMIN_REGISTRY_PATH):
        try:
            with open(ADMIN_REGISTRY_PATH, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []
    return []

def save_admin_registry(registry: list):
    """Save the admin document registry to disk."""
    with open(ADMIN_REGISTRY_PATH, "w") as f:
        json.dump(registry, f, indent=2)

app = Flask(__name__)
CORS(app, origins=["http://localhost:3000", "http://127.0.0.1:3000"])


def draw_tamper_boxes_base64(original_path: str, mask_path: str) -> str:
    """Draw red bounding boxes around tampered regions on the original image."""
    # Load original image
    original = cv2.imread(original_path)
    if original is None:
        return ""
    
    # Resize original to match mask dimensions (512x512)
    original = cv2.resize(original, (512, 512))

    if not mask_path or not os.path.exists(mask_path):
        # If no mask, just return the resized original
        _, buffer = cv2.imencode('.png', original)
        return base64.b64encode(buffer).decode('utf-8')

    mask = np.load(mask_path)

    # Threshold the mask to find high-probability tamper regions
    # The mask contains probabilities from 0 to 1
    # We use a threshold of 0.5 (or slightly higher/lower based on tuning)
    threshold_value = 0.5
    binary_mask = (mask > threshold_value).astype(np.uint8) * 255

    # Find contours
    contours, _ = cv2.findContours(binary_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Draw red bounding boxes for each contour
    for contour in contours:
        # Ignore extremely small noise
        if cv2.contourArea(contour) > 50:
            x, y, w, h = cv2.boundingRect(contour)
            # Draw red box (BGR format) with thickness 2
            cv2.rectangle(original, (x, y), (x + w, y + h), (0, 0, 255), 2)

    _, buffer = cv2.imencode('.png', original)
    return base64.b64encode(buffer).decode('utf-8')


def image_file_to_base64(file_path: str) -> str:
    """Convert an image file to base64-encoded PNG."""
    img = cv2.imread(file_path)
    if img is None:
        return ""
    # Resize for consistent display
    img = cv2.resize(img, (512, 512))
    _, buffer = cv2.imencode('.png', img)
    return base64.b64encode(buffer).decode('utf-8')


@app.route('/api/analyze', methods=['POST'])
def analyze():
    """
    Accepts an image upload, runs ML inference, and returns:
    - is_tampered, confidence_score, detail scores
    - base64 PNG of the original image (resized)
    - base64 PNG of the tamper mask (contrast-enhanced)
    """
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "Empty filename"}), 400

    # Save to temp file
    temp_path = os.path.join(base_dir, "temp_api_upload_" + file.filename)
    file.save(temp_path)

    try:
        # Run real ML inference
        result = run_inference(temp_path)

        # Draw red bounding boxes around tampered regions on original image
        mask_path = result.get("mask_path", "")
        mask_b64 = draw_tamper_boxes_base64(temp_path, mask_path)

        # Convert original image to base64
        original_b64 = image_file_to_base64(temp_path)

        response = {
            "is_tampered": result.get("is_tampered", False),
            "confidence_score": result.get("confidence_score", 0),
            "details": result.get("details", {}),
            "model_loaded": result.get("model_loaded", False),
            "mask_image": mask_b64,
            "original_image": original_b64,
        }

        return jsonify(response)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        # Clean up temp files
        if os.path.exists(temp_path):
            os.remove(temp_path)


@app.route('/api/anchor', methods=['POST'])
def anchor():
    """
    Accepts an image upload + AI verdict, runs verify_and_anchor.
    """
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    temp_path = os.path.join(base_dir, "temp_api_anchor_" + file.filename)
    file.save(temp_path)

    try:
        ai_verdict = {
            "is_tampered": request.form.get("is_tampered", "false").lower() == "true",
            "confidence_score": float(request.form.get("confidence_score", 0)),
        }

        result = verify_and_anchor(temp_path, ai_verdict)
        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({"status": "ok", "message": "API server is running"})


# ============================================================
#                    ADMIN ENDPOINTS
# ============================================================

@app.route('/api/admin/upload', methods=['POST'])
def admin_upload():
    """
    Admin uploads a document to register it on the blockchain.
    The document hash (SHA-256) is computed and anchored on-chain.
    """
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "Empty filename"}), 400

    # Save to temp file
    temp_path = os.path.join(base_dir, "temp_admin_upload_" + file.filename)
    file.save(temp_path)

    try:
        # 1. Hash the document
        doc_hash = hash_document(temp_path)

        # 2. Check if already anchored
        if is_hash_anchored(doc_hash):
            return jsonify({
                "success": False,
                "status": "duplicate",
                "reason": "Document hash is already anchored on the blockchain.",
                "hash": doc_hash,
                "filename": file.filename,
            })

        # 3. Anchor on blockchain (force is_tampered=False so it anchors)
        ai_verdict = {"is_tampered": False, "confidence_score": 0}
        result = verify_and_anchor(temp_path, ai_verdict)

        if result.get("success"):
            # 4. Persist to admin registry
            registry = load_admin_registry()
            entry = {
                "filename": file.filename,
                "hash": doc_hash,
                "tx_hash": result.get("tx_hash", ""),
                "block_number": result.get("block", 0),
                "timestamp": datetime.now().isoformat(),
            }
            registry.append(entry)
            save_admin_registry(registry)

            return jsonify({
                "success": True,
                "status": "anchored",
                "hash": doc_hash,
                "tx_hash": result.get("tx_hash", ""),
                "block_number": result.get("block", 0),
                "filename": file.filename,
                "timestamp": entry["timestamp"],
            })
        else:
            return jsonify({
                "success": False,
                "status": result.get("status", "error"),
                "reason": result.get("reason", "Unknown error"),
                "hash": doc_hash,
            })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


@app.route('/api/admin/documents', methods=['GET'])
def admin_documents():
    """Returns the list of all admin-registered documents."""
    registry = load_admin_registry()
    return jsonify({"documents": registry})


@app.route('/api/admin/verify', methods=['POST'])
def admin_verify():
    """Verify a hash directly against the blockchain."""
    data = request.get_json()
    if not data or 'hash' not in data:
        return jsonify({"error": "Missing 'hash' in request body"}), 400

    doc_hash = data['hash']
    anchored = is_hash_anchored(doc_hash)
    return jsonify({"hash": doc_hash, "anchored": anchored})


if __name__ == '__main__':
    print("🚀 Starting Flask API server on http://localhost:5000")
    print("   Endpoints:")
    print("   POST /api/analyze          - Upload image for ML analysis")
    print("   POST /api/anchor           - Anchor document to blockchain")
    print("   POST /api/admin/upload     - Admin: register document on chain")
    print("   GET  /api/admin/documents  - Admin: list registered documents")
    print("   POST /api/admin/verify     - Admin: verify a hash on chain")
    print("   GET  /api/health           - Health check")
    app.run(host='0.0.0.0', port=5000, debug=True)
