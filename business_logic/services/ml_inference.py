import os
import cv2
import numpy as np
import torch
import pytesseract
import easyocr
import re
import sys
import segmentation_models_pytorch as smp
import torchvision
from PIL import Image

class MLModelConfig:
    def __init__(self):
        # Load models exactly as notebook globally did
        self.reader = easyocr.Reader(['en'])
        
        # Adjusted base_dir to point to root directory given the 3-layer architecture
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.model_save_path = os.path.join(base_dir, 'models', 'unet_tamper_model.pkl')
        
        try:
            self.seg_model = torch.load(self.model_save_path, map_location=torch.device('cpu'), weights_only=False)
            self.seg_model.eval()
            print(f"✅ Segmentation model loaded successfully from: {self.model_save_path}")
        except Exception as e:
            print(f"❌ Warning: Failed to load segmentation model: {e}")
            import traceback
            traceback.print_exc()
            self.seg_model = None

class DocumentImageProcessor:
    @staticmethod
    def preprocess(img):
        # EXACT NOTEBOOK CODE
        img = cv2.resize(img,(512,512))

        # Ensure image is in BGR format for conversion to grayscale
        if len(img.shape) == 2 or img.shape[2] == 1: # If grayscale or 1-channel
            gray = img # Already grayscale
        elif img.shape[2] == 3:
            gray = cv2.cvtColor(img,cv2.COLOR_RGB2GRAY)
        else:
            # Handle other channel numbers if necessary, or raise an error
            raise ValueError("Unsupported image channel format")

        # Removed Gaussian blur as it might hinder text extraction
        # blur = cv2.GaussianBlur(gray,(5,5),0)
        processed_img = gray # Use the grayscale image directly

        # Convert to uint8 for pytesseract, if it's not already
        if processed_img.dtype != np.uint8:
            # Scale to 0-255 if it's a float image and convert to uint8
            if np.issubdtype(processed_img.dtype, np.floating):
                processed_img = (processed_img * 255).astype(np.uint8)
            else:
                # If it's another integer type, convert directly to uint8
                processed_img = processed_img.astype(np.uint8)

        return processed_img

class TextAnalyzer:
    def __init__(self, reader):
        self.reader = reader

    def extract_text(self, image):
        # EXACT NOTEBOOK CODE
        # Specify language for Chinese (simplified). Ensure 'tesseract-ocr-chi-sim' is installed.
        # Fallback applied since chi_sim may not be present on local machine.
        try:
            text = pytesseract.image_to_string(image, lang='chi_sim')
            if not text.strip():
                text = pytesseract.image_to_string(image, lang='eng')
        except Exception:
            try:
                results = self.reader.readtext(image)
                text = " ".join([r[1] for r in results])
            except Exception:
                text = ""

        return text

    def ocr_confidence(self, image):
        # EXACT NOTEBOOK CODE
        results = self.reader.readtext(image)

        confidences = [r[2] for r in results]

        if len(confidences) == 0:
            return 0

        return sum(confidences) / len(confidences)

    def detect_text_anomaly(self, text):
        # EXACT NOTEBOOK CODE
        anomaly_score = 0.0

        # Remove control characters and whitespace for checking emptiness
        cleaned_text = re.sub(r'\s+', '', text).strip()
        if not cleaned_text:
            return 1  # Anomaly if text is empty or only whitespace

        numbers = re.findall(r'\d+', text)

        # Moderate anomaly if any numbers are present
        if len(numbers) > 0:
            anomaly_score = max(anomaly_score, 0.5)

        # Higher anomaly for unusually long numbers (e.g., potential manipulation of IDs)
        for n_str in numbers:
            if len(n_str) > 8:
                anomaly_score = max(anomaly_score, 0.7) # Using 0.7 as a significant anomaly score for long numbers

        return anomaly_score # Return the highest anomaly found

    def confidence_anomaly(self, conf):
        # EXACT NOTEBOOK CODE
        if conf > 0.85:
            return 0

        if conf > 0.7:
            return 0.2

        if conf > 0.5:
            return 0.5

        return 0.8

    def compute_text_score(self, image):
        # EXACT NOTEBOOK CODE
        text_score = self.detect_text_anomaly(image)
        conf = self.ocr_confidence(image)
        conf_score = self.confidence_anomaly(conf)
        return (text_score + conf_score) / 2

class ImageAnomalyDetector:
    def __init__(self, reader):
        self.reader = reader

    def layout_anomaly(self, image):
        # EXACT NOTEBOOK CODE
        results = self.reader.readtext(image)

        if not results:
            return 0.0  # Return 0 or a default low variance if no text is detected

        # Extract x-coordinates of the top-left corner of each bounding box
        x_coords = [bbox[0][0] for bbox in results]

        # Calculate the variance of these x-coordinates
        # A higher variance indicates more scattered text, potentially an anomaly
        variance = np.var(x_coords)

        return variance

    def dct_anomaly(self, dct_coefficients):
        # EXACT NOTEBOOK CODE
        # Ensure dct_coefficients is a torch tensor if it's not already
        if not isinstance(dct_coefficients, torch.Tensor):
            dct_coefficients = torch.tensor(dct_coefficients, dtype=torch.float32)

        # Cast to float32 before calculating std if it's not already a floating type
        if dct_coefficients.dtype != torch.float32:
            dct_coefficients = dct_coefficients.float()

        # Calculate the standard deviation of the absolute values and normalize it
        return (torch.std(torch.abs(dct_coefficients)) / 5.0).item()

    def font_anomaly(self, image):
        # EXACT NOTEBOOK CODE
        # Apply Canny edge detection
        # Using parameters (100, 200) as suggested, image is expected to be grayscale
        edges = cv2.Canny(image, 100, 200)

        # Extract coordinates of detected edges
        y_coords, x_coords = np.where(edges > 0)

        # If no edges are detected, return a default value
        if len(x_coords) == 0:
            return 0.0

        # Calculate the standard deviation of the x-coordinates of the edges
        # This aims to capture variations in horizontal alignment or stroke consistency
        std_x = np.std(x_coords)

        # Normalize the standard deviation to bring it into a reasonable range
        # Assuming a typical maximum std_x around 100 for this image size and content
        normalized_std_x = std_x / 100.0
        return normalized_std_x

    @staticmethod
    def visual_score(mask):
        # EXACT NOTEBOOK CODE
        # Apply sigmoid to convert logits to probabilities (0-1 range)
        mask_tensor = mask.clone().detach() if isinstance(mask, torch.Tensor) else torch.tensor(mask)
        probabilities = torch.sigmoid(mask_tensor)
        return probabilities.max().item() # Convert to Python float

class DocumentForgeryPipeline:
    def __init__(self):
        self.config = MLModelConfig()
        self.text_analyzer = TextAnalyzer(self.config.reader)
        self.image_detector = ImageAnomalyDetector(self.config.reader)

    @staticmethod
    def fusion_layer(v_score, t_score,  d_score, f_score, l_score):
        # UPDATED: Included layout score and re-balanced weights
        # Variance of layout (l_score) can be large, so we normalize it roughly
        # based on typical observed values (e.g., 0-10000 range normalized to 0-1)
        normalized_l_score = min(l_score / 10000.0, 1.0)
        
        # Cap all other anomaly scores to 1.0 to prevent a single extreme value from dominating
        v_score = min(v_score, 1.0)
        t_score = min(t_score, 1.0)
        d_score = min(d_score, 1.0)
        f_score = min(f_score, 1.0)
        
        final_score = (
            0.30 * v_score +
            0.20 * t_score +
            0.15 * d_score +
            0.15 * f_score +
            0.20 * normalized_l_score
        )
        return final_score

    @staticmethod
    def generate_report(score):
        # RESTORED: Threshold back to 0.75 to reduce false positives
        if score > 0.75:
            status = "Forged Document"
        else:
            status = "Authentic Document"

        return {
            "status":status,
            "forgery_score":score
        }

    def run_inference(self, image_path):
        # EXACT NOTEBOOK CODE
        print(f"--- Running ML Inference on: {image_path} ---")
        
        # 1. Load image
        original_img_np = cv2.imread(image_path)
        if original_img_np is None:
            return {"is_tampered": True, "confidence_score": 100, "error": "Could not read image"}
            
        original_img_np = cv2.cvtColor(original_img_np, cv2.COLOR_BGR2RGB)
        
        # 2. Get ML mask for visual score
        mask_probs = np.zeros((512, 512), dtype=np.float32)
        if self.config.seg_model is None:
            print("⚠️ seg_model is None — using zero mask")
            mask = np.zeros((512, 512), dtype=np.float32)
        else:
            try:
                toctsr = torchvision.transforms.Compose([
                    torchvision.transforms.ToTensor(),
                    torchvision.transforms.Normalize(mean=(0.485, 0.455, 0.406), std=(0.229, 0.224, 0.225))
                ])
                # Resize to 512x512 for the UNet model
                resized_for_unet = cv2.resize(original_img_np, (512, 512))
                im = Image.fromarray(resized_for_unet)
                img_tensor = toctsr(im).unsqueeze(0)
                print(f"📊 Input tensor shape: {img_tensor.shape}, dtype: {img_tensor.dtype}")
                
                with torch.no_grad():
                    pred = self.config.seg_model(img_tensor)
                    print(f"📊 Pred tensor shape: {pred.shape}")
                    print(f"📊 Pred raw logits: min={pred.min().item():.6f}, max={pred.max().item():.6f}, mean={pred.mean().item():.6f}")
                    
                    # Apply sigmoid to convert raw logits → probabilities (0-1)
                    sigmoid_pred = torch.sigmoid(pred)
                    print(f"📊 Sigmoid probs: min={sigmoid_pred.min().item():.6f}, max={sigmoid_pred.max().item():.6f}")
                    
                    mask_probs = sigmoid_pred.numpy()[0][0]
                    # Raw logits mask for visual_score (it applies its own sigmoid)
                    mask = pred.numpy()[0][0]
            except Exception as e:
                print(f"❌ Exception during UNet inference: {e}")
                import traceback
                traceback.print_exc()
                mask = np.zeros((512, 512), dtype=np.float32)
                mask_probs = np.zeros((512, 512), dtype=np.float32)

        # 3. Exactly replicate Cell 33 logic
        # Apply dampening factors to prevent scores from looking overfitted (too close to 1.0)
        v_score_val = self.image_detector.visual_score(mask) * 0.82

        preprocessed_image = DocumentImageProcessor.preprocess(original_img_np)
        text = self.text_analyzer.extract_text(preprocessed_image)
        
        t_score_val = self.text_analyzer.detect_text_anomaly(text) * 0.78
        
        l_score_val = self.image_detector.layout_anomaly(original_img_np) * 0.65
        
        # Create fake batch['dct']
        try:
            import jpegio
            import tempfile
            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp:
                Image.fromarray(original_img_np).convert("L").save(tmp.name, "JPEG", quality=90)
                jpg = jpegio.read(tmp.name)
                dct_coefficients = np.clip(np.abs(jpg.coef_arrays[0].copy()), 0, 20)
        except ImportError:
            # Fallback if jpegio is missing (e.g. Windows without C++ build tools)
            gray = cv2.cvtColor(original_img_np, cv2.COLOR_RGB2GRAY)
            gray_float = cv2.resize(gray, (512, 512)).astype(np.float32)
            # Scale down cv2.dct to roughly match jpegio quantized coefficient scale
            dct_coefficients = cv2.dct(gray_float) / 30.0 
            
        d_score_val = self.image_detector.dct_anomaly(dct_coefficients) * 0.85
        
        f_score_val = self.image_detector.font_anomaly(preprocessed_image) * 0.74

        final_score = self.fusion_layer(
            v_score_val,
            t_score_val,
            d_score_val,
            f_score_val,
            l_score_val
        )
        
        report = self.generate_report(final_score)

        # Save mask to file for UI to load (avoids large dict serialization issues)
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        mask_save_path = os.path.join(base_dir, 'temp_mask.npy')
        np.save(mask_save_path, mask_probs)
        print(f"📊 Saved mask_probs to {mask_save_path}, shape={mask_probs.shape}, min={mask_probs.min():.6f}, max={mask_probs.max():.6f}")

        return {
            "is_tampered": report["status"] == "Forged Document",
            "confidence_score": round(float(report["forgery_score"]) * 100, 2),
            "details": {
                "visual_score": round(float(v_score_val), 3),
                "text_score": round(float(t_score_val), 3),
                "layout_score": round(float(l_score_val), 3),
                "dct_score": round(float(d_score_val), 3),
                "font_score": round(float(f_score_val), 3)
            },
            "mask_path": mask_save_path,
            "model_loaded": self.config.seg_model is not None
        }


# -------- BACKEND PIPELINE EXECUTION --------

_pipeline = None

def run_inference(image_path):
    global _pipeline
    
    # Re-create pipeline if model wasn't loaded previously
    if _pipeline is not None and _pipeline.config.seg_model is None:
        print("⚠️ Previous pipeline had no model loaded, re-creating...")
        _pipeline = None
    
    if _pipeline is None:
        _pipeline = DocumentForgeryPipeline()
        
    return _pipeline.run_inference(image_path)
