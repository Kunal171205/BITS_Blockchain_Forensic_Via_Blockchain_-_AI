import os
import sys
import cv2
import numpy as np

# Add root to path
base_dir = os.path.dirname(os.path.abspath(__file__))
if base_dir not in sys.path:
    sys.path.append(base_dir)

from business_logic.services.ml_inference import run_inference

def test_inference():
    # Create a dummy image or use an existing one if available
    # For now, let's just try to run it on the "real image" if we can find it, 
    # but I don't have the path to the user's uploaded images.
    # I'll create a dummy 1000x1000 image.
    dummy_path = "dummy_receipt.jpg"
    img = np.ones((1000, 1000, 3), dtype=np.uint8) * 255
    cv2.putText(img, "Receipt 12345", (100, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
    cv2.imwrite(dummy_path, img)

    print(f"Running inference on {dummy_path}...")
    try:
        result = run_inference(dummy_path)
        print("Inference Result:")
        print(result)
    except Exception as e:
        print(f"Error during inference: {e}")
    finally:
        if os.path.exists(dummy_path):
            os.remove(dummy_path)

if __name__ == "__main__":
    test_inference()
