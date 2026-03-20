import os
import torch
import sys

# Add the project root to sys.path
base_dir = r"c:\Users\user\Downloads\BITS_Document_Forensic\blockchain"
sys.path.insert(0, base_dir)

model_path = os.path.join(base_dir, 'models', 'unet_tamper_model.pkl')

print(f"Checking model path: {model_path}")
if not os.path.exists(model_path):
    print("❌ Model file does NOT exist!")
    sys.exit(1)

print("Attempting to load model with torch...")
try:
    # We might need to import segmentation_models_pytorch first
    import segmentation_models_pytorch as smp
    model = torch.load(model_path, map_location=torch.device('cpu'), weights_only=False)
    model.eval()
    print("✅ Model loaded successfully!")
except Exception as e:
    print(f"❌ Failed to load model: {e}")
    import traceback
    traceback.print_exc()
