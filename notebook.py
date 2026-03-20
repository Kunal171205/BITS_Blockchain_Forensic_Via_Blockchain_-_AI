!nvidia-smi
!git clone https://github.com/qcf-568/DocTamper.git
%cd DocTamper
!pip install lmdb jpegio albumentations opencv-python tqdm
!pip install segmentation-models-pytorch
!pip install pytesseract easyocr
!pip install ultralytics

import os

dataloader_path = '/kaggle/working/DocTamper/dataloader.py'

with open(dataloader_path, 'r') as f:
    lines = f.readlines()

new_lines = []
os_imported = False
for i, line in enumerate(lines):
    if line.strip() == 'import os':
        os_imported = True
    # Correctly match the full problematic line
    if "with open('pks/'+roots+'_%d.pk'%minq,'rb') as f:" in line:
        new_lines.append(line.replace(
            "with open('pks/'+roots+'_%d.pk'%minq,'rb')",
            "with open('pks/'+os.path.basename(roots)+'_%d.pk'%minq,'rb')"
        ))
    else:
        new_lines.append(line)

# Ensure 'import os' is at the top
if not os_imported:
    new_lines.insert(0, 'import os\n')

with open(dataloader_path, 'w') as f:
    f.writelines(new_lines)

print('dataloader.py has been re-modified. Please re-run all cells from the beginning after this operation.')
from dataloader import DocTamperDataset
from torch.utils.data import DataLoader

dataset = DocTamperDataset(
    roots="/kaggle/input/datasets/kunalbiradar17/bits-goa-model-data/DocTamperV1-SCD",
    minq=75,
    max_nums=2000
)

loader = DataLoader(dataset, batch_size=4, shuffle=True)

for batch in loader:
    labels = batch['label']

    print("Label tensor shape:", labels.shape)
    print("Unique values:", labels.unique())

    break
import torch

total_zeros = 0
total_ones = 0

for batch in loader:

    masks = batch['label']

    total_zeros += torch.sum(masks == 0).item()
    total_ones += torch.sum(masks == 1).item()

print("Authentic pixels (0):", total_zeros)
print("Tampered pixels (1):", total_ones)
!nvidia-smi
import matplotlib.pyplot as plt

sample = dataset[0]

image = sample['image'].permute(1,2,0)
mask = sample['label'][0]

plt.figure(figsize=(10,4))

plt.subplot(1,2,1)
plt.title("Image")
plt.imshow(image)

plt.subplot(1,2,2)
plt.title("Tamper Mask")
plt.imshow(mask, cmap="gray")

plt.show()
len(dataset)
for batch in loader:
    print(batch['image'].shape)
    print(batch['label'].shape)
    print(batch['dct'].shape)
    break

import cv2
import numpy as np # Import numpy

def preprocess(img):

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
import torch
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(device)

import segmentation_models_pytorch as smp


model = smp.Unet(
    encoder_name="resnet34",
    encoder_weights="imagenet",
    in_channels=3,
    classes=1
)

model = model.to(device)

def compute_accuracy(preds, masks):

    preds = torch.sigmoid(preds)
    preds = (preds > 0.5).float()

    correct = (preds == masks).float().sum()

    total = torch.numel(preds)

    return correct / total
    
def compute_iou(preds, masks):

    preds = torch.sigmoid(preds)
    preds = (preds > 0.5).float()

    intersection = (preds * masks).sum()
    union = preds.sum() + masks.sum() - intersection

    if union == 0:
        return torch.tensor(1.0)

    return intersection / union
optimizer = torch.optim.Adam(model.parameters(), lr=1e-4)

for epoch in range(15):

    epoch_loss = 0
    epoch_acc = 0
    epoch_iou = 0
    batches = 0

    for batch in loader:

        images = batch['image'].to(device)
        masks = batch['label'].float().to(device)

        preds = model(images)

        loss = torch.nn.functional.binary_cross_entropy_with_logits(preds, masks)

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        acc = compute_accuracy(preds, masks)
        iou = compute_iou(preds, masks)

        epoch_loss += loss.item()
        epoch_acc += acc.item()
        epoch_iou += iou.item()
        batches += 1

    print(
        f"Epoch {epoch} | Loss: {epoch_loss/batches:.4f} | "
        f"Accuracy: {epoch_acc/batches:.4f} | IoU: {epoch_iou/batches:.4f}"
    )
import matplotlib.pyplot as plt

sample = dataset[1]

img = sample['image'].unsqueeze(0).to(device)

pred = model(img)

mask = pred.detach().cpu().numpy()[0][0]

plt.imshow(mask)
plt.title("Tampered Region")
import matplotlib.pyplot as plt
import numpy as np

# Get the original image tensor from the sample
original_img_tensor = sample['image']

# Convert to numpy array and transpose dimensions from (C, H, W) to (H, W, C)
original_img_np = original_img_tensor.permute(1, 2, 0).cpu().numpy()

# Normalize the image data to the [0, 1] range for proper display
min_val = original_img_np.min()
max_val = original_img_np.max()
if max_val > min_val:
    original_img_np = (original_img_np - min_val) / (max_val - min_val)
else:
    original_img_np = np.zeros_like(original_img_np) # Handle case where all pixels are the same

plt.figure(figsize=(6, 6))
plt.imshow(original_img_np)
plt.title("Original Image")
# plt.axis('off') # Hide axes for cleaner image display
plt.show()
!apt-get install tesseract-ocr

!apt-get install tesseract-ocr-chi-sim
import pytesseract

def extract_text(image):

    # Specify language for Chinese (simplified). Ensure 'tesseract-ocr-chi-sim' is installed.
    text = pytesseract.image_to_string(image, lang='chi_sim')

    return text

preprocessed_image = preprocess(original_img_np)
text = extract_text(preprocessed_image)
print(text)

import matplotlib.pyplot as plt

plt.figure(figsize=(6, 6))
plt.imshow(preprocessed_image, cmap='gray')
plt.title("Image after Preprocessing for Text Extraction")
plt.axis('off')
plt.show()
import easyocr

reader = easyocr.Reader(['en'])

def ocr_confidence(image):

    results = reader.readtext(image)

    confidences = [r[2] for r in results]

    if len(confidences) == 0:
        return 0

    return sum(confidences) / len(confidences)

import pytesseract
import re

def detect_text_anomaly(image):

    text = pytesseract.image_to_string(image)

    score = 0

    # 1️⃣ empty text
    if len(text.strip()) == 0:
        score += 0.4

    # 2️⃣ unusual characters
    special_chars = re.findall(r'[^\w\s]', text)
    if len(special_chars) > 5:
        score += 0.3

    # 3️⃣ suspicious numeric patterns
    numbers = re.findall(r'\d+', text)
    for n in numbers:
        if len(n) > 8:   # extremely long number
            score += 0.3

    return min(score,1.0)

import re

def detect_text_anomaly(text):
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
def confidence_anomaly(conf):

    if conf > 0.85:
        return 0

    if conf > 0.7:
        return 0.2

    if conf > 0.5:
        return 0.5

    return 0.8

def compute_text_score(image):

    text_score = detect_text_anomaly(image)

    conf = ocr_confidence(image)

    conf_score = confidence_anomaly(conf)

    return (text_score + conf_score) / 2


from ultralytics import YOLO
import torch # Import torch for tensor operations

model_yolo = YOLO("yolov8n.pt")

results = model_yolo(original_img_np)

# Check if there are any detections before calculating mean confidence
if len(results[0].boxes.conf) > 0:
    signature_score = results[0].boxes.conf.mean()
else:
    # Assign a default score if no signatures are detected
    # For example, 0 means no signature found, or 0.5 for a neutral stance
    signature_score = torch.tensor(0.0, device='cuda:0') # Default to 0 if no detections

print(signature_score)
import numpy as np
import torch # Import torch for sigmoid function

def visual_score(mask):
    # Apply sigmoid to convert logits to probabilities (0-1 range)
    probabilities = torch.sigmoid(torch.tensor(mask))
    return probabilities.max().item() # Convert to Python float
import numpy as np

def layout_anomaly(image):
    # The 'reader' object from easyocr is already initialized in cell 'munHZSuaDY0p'
    # We will use it directly.
    results = reader.readtext(image)

    if not results:
        return 0.0  # Return 0 or a default low variance if no text is detected

    # Extract x-coordinates of the top-left corner of each bounding box
    x_coords = [bbox[0][0] for bbox in results]

    # Calculate the variance of these x-coordinates
    # A higher variance indicates more scattered text, potentially an anomaly
    variance = np.var(x_coords)

    return variance

print("layout_anomaly function defined.")
import torch

def dct_anomaly(dct_coefficients):
    # The DCT coefficients are expected to be a tensor or numpy array
    # We calculate the standard deviation of the absolute values of the coefficients
    # to get a measure of their spread and potential inconsistencies.

    # Ensure dct_coefficients is a torch tensor if it's not already
    if not isinstance(dct_coefficients, torch.Tensor):
        dct_coefficients = torch.tensor(dct_coefficients, dtype=torch.float32)

    # Cast to float32 before calculating std if it's not already a floating type
    if dct_coefficients.dtype != torch.float32:
        dct_coefficients = dct_coefficients.float()

    # Calculate the standard deviation of the absolute values and normalize it
    return (torch.std(torch.abs(dct_coefficients)) / 5.0).item()

print("dct_anomaly function defined with normalized standard deviation.")
import cv2
import numpy as np

def font_anomaly(image):
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

print("font_anomaly function defined with normalization.")
import numpy as np
import torch # Import torch for sigmoid function

def visual_score(mask):
    # Apply sigmoid to convert logits to probabilities (0-1 range)
    probabilities = torch.sigmoid(torch.tensor(mask))
    return probabilities.max().item() # Convert to Python float

def fusion_layer(v_score, t_score,  d_score, f_score):

    final_score = (
        0.35 * v_score +
        0.25 * t_score +
        0.2 * d_score +
        0.2 * f_score
    )

    return final_score

v_score_val = visual_score(mask)
print("Visual Score (v_score_val):")
print(v_score_val)

t_score_val = detect_text_anomaly(text)
print("Text Anomaly Score (t_score_val):")
print(t_score_val)

l_score_val = layout_anomaly(original_img_np)
print("Layout Anomaly Score (l_score_val):")
print(l_score_val)

d_score_val = dct_anomaly(batch['dct'])
print("DCT Anomaly Score (d_score_val):")
print(d_score_val)

f_score_val = font_anomaly(preprocessed_image)
print("Font Anomaly Score (f_score_val):")
print(f_score_val)

final_score = fusion_layer(
    v_score_val,
    t_score_val,
    d_score_val,
    f_score_val
)
print("Final Score:")
print(final_score)
def generate_report(score):

    if score > 0.75:
        status = "Forged Document"
    else:
        status = "Authentic Document"

    return {
        "status":status,
        "forgery_score":score
    }

report = generate_report(final_score)
print(report)
import torch
from IPython.display import FileLink

# Save the entire model (architecture + weights)
model_save_path = '/kaggle/working/unet_tamper_model.pkl'
torch.save(model, model_save_path)
print(f"Model saved successfully to {model_save_path}")

# Display a download link so you can download it to your computer
FileLink('unet_tamper_model.pkl')
