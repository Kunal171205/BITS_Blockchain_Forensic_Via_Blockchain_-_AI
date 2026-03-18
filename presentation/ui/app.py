import streamlit as st
import os
import sys
import time

# Add root folder to path to import scripts
base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if base_dir not in sys.path:
    sys.path.append(base_dir)

from business_logic.services.document_verification import verify_and_anchor, is_hash_anchored
from data_access.crypto_utils import hash_document
from business_logic.services.ml_inference import run_inference
import numpy as np
import cv2
from PIL import Image
import matplotlib.pyplot as plt

st.set_page_config(page_title="Bridge Controller UI", layout="centered", page_icon="🔐")

st.title("🔐 Bridge Controller Dashboard")
st.write("Verifies ML outputs and anchors authentic documents to Ganache Blockchain.")

# Premium Styling
st.markdown("""
<style>
    .scroll-container {
        max-height: 600px;
        overflow-y: auto;
        overflow-x: hidden;
        border: 2px solid #f0f2f6;
        border-radius: 10px;
        padding: 10px;
        background-color: #fcfcfc;
    }
    .stImage > img {
        border-radius: 5px;
        transition: transform 0.2s;
    }
    .stImage > img:hover {
        transform: scale(1.02);
    }
</style>
""", unsafe_allow_html=True)

st.divider()

st.subheader("Simulate Document Verification Pipeline")

uploaded_file = st.file_uploader("Upload a document for processing", type=["png", "jpg", "jpeg"])

if st.button("Trigger Pipeline & Verify", type="primary"):
    if uploaded_file is None:
        st.error("Please upload a file to proceed.")
    else:
        # Save temp file
        temp_path = os.path.join(base_dir, "temp_upload_" + uploaded_file.name)
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        st.info("Analyzing document with local Multi-Model Pipeline...")
        
        with st.spinner("Running deep learning models (Unet, YOLO, OCR)..."):
            ai_verdict = run_inference(temp_path)
            
        st.write("### AI Analysis Results")
        if ai_verdict.get("error"):
            st.error(f"Inference Error: {ai_verdict['error']}")
        else:
            tampered_status = "TAMPERED" if ai_verdict["is_tampered"] else "AUTHENTIC"
            color = "red" if ai_verdict["is_tampered"] else "green"
            st.markdown(f"**Document Status:** :{color}[**{tampered_status}**]")
            st.markdown(f"**Forgery Probability / Score:** `{ai_verdict['confidence_score']}%`")
            
            # SIDE-BY-SIDE VISUALIZATION
            st.write("### Visual Forensic Analysis")
            
            # Debug: Show model status
            model_loaded = ai_verdict.get("model_loaded", False)
            if model_loaded:
                st.success("✅ UNet segmentation model is loaded")
            else:
                st.warning("⚠️ UNet segmentation model NOT loaded — mask will be empty")
            
            # Get original and mask
            original_img = Image.open(temp_path)
            
            # Load mask from saved .npy file (bypasses dict serialization issues)
            mask_path = ai_verdict.get("mask_path", "")
            if mask_path and os.path.exists(mask_path):
                mask_data = np.load(mask_path)
                st.caption(f"🔬 Mask loaded from file: shape={mask_data.shape}, min={mask_data.min():.6f}, max={mask_data.max():.6f}")
            else:
                mask_data = np.array([])
                st.warning(f"⚠️ Mask file not found at: {mask_path}")
            
            if mask_data.size > 0:
                mask_vis = np.array(mask_data, dtype=np.float32)
                
                # Debug: show actual probability range
                mask_min = float(mask_vis.min())
                mask_max = float(mask_vis.max())
                st.caption(f"🔬 Raw mask range: min={mask_min:.6f}, max={mask_max:.6f}")
                
                # Apply contrast stretching (min-max normalization)
                # This amplifies even tiny probability differences to fill 0-1 range
                if mask_max > mask_min:
                    mask_enhanced = (mask_vis - mask_min) / (mask_max - mask_min)
                else:
                    mask_enhanced = mask_vis
                
                # Also create a binary thresholded mask
                # Threshold at the mean + 1 std dev to highlight only the hottest spots
                threshold = mask_vis.mean() + mask_vis.std()
                mask_binary = (mask_vis > threshold).astype(np.float32)
                
                # Create Matplotlib Figure: 3 panels
                fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(15, 5))
                
                # Plot Original Image (resized to 512x512 to match mask)
                original_resized = original_img.resize((512, 512))
                ax1.imshow(original_resized)
                ax1.set_title("Image")
                
                # Plot Enhanced Tamper Mask (contrast stretched)
                ax2.imshow(mask_enhanced, cmap='gray')
                ax2.set_title("Tamper Mask (Enhanced)")
                
                # Plot Binary Detection Mask (thresholded)
                ax3.imshow(mask_binary, cmap='gray')
                ax3.set_title("Tamper Mask (Binary)")
                
                plt.tight_layout()
                
                # Scrollable container
                st.markdown('<div class="scroll-container" style="height: auto; max-height: 800px;">', unsafe_allow_html=True)
                st.pyplot(fig)
                plt.close(fig)
                st.markdown('</div>', unsafe_allow_html=True)
                
                st.info("**Enhanced**: Contrast-stretched to amplify subtle signals. **Binary**: Thresholded to show only the strongest detections (White = Potential Tampering).")
            
            with st.expander("📊 Detailed Model Scores (0.0 to 1.0)"):
                st.json(ai_verdict.get("details", {}))
                
        st.info("Initiating verify_and_anchor workflow...")
        
        with st.spinner("Processing transaction..."):
            result = verify_and_anchor(temp_path, ai_verdict)
        
        st.divider()
        st.subheader("Blockchain Integration Results")
        
        if result["status"] == "anchored":
            st.success(f"✅ Document successfully anchored!")
            st.write(f"**Transaction Hash:** `{result.get('tx_hash')}`")
            st.write(f"**Document Hash:** `{result.get('hash')}`")
            st.write(f"**Block Number:** `{result.get('block')}`")
        elif result["status"] == "blocked":
            st.error(f"🚨 BLOCKED: Transaction aborted due to AI Forgery Detection.")
            st.write(f"**Reason:** {result.get('reason')}")
            st.write(f"**Document Hash:** `{result.get('hash')}`")
        else:
            st.warning(f"⚠️ Error occurred: {result.get('reason')}")
        
        # Check blockchain status explicitly for the UI requirement
        st.markdown("### Blockchain Status")
        if is_hash_anchored(result.get("hash", "")):
            st.markdown("🟢 **VERIFIED:** Hash exists on Ganache.")
        else:
            st.markdown("🔴 **UNVERIFIED:** Hash is not on the blockchain.")
            
        # Clean up
        if os.path.exists(temp_path):
            os.remove(temp_path)
