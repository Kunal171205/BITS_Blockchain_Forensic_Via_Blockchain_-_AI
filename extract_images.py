"""
Quick check: what fraction of DocTamper masks are non-zero?
Also save 20 images with lowest tamper ratio as "authentic" proxies.
"""
import os, lmdb, numpy as np
from PIL import Image
import io

DATASET_PATH = r"P:\BITS\DocTamperV1-SCD"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_REAL = os.path.join(BASE_DIR, "extracted_real_images")
OUTPUT_TAMPERED = os.path.join(BASE_DIR, "extracted_tampered_images")

env = lmdb.open(DATASET_PATH, readonly=True, lock=False)
total = env.stat()['entries']
print(f"Total LMDB entries: {total}")

# Collect tamper ratios for first 200 pairs
ratios = []
with env.begin() as txn:
    cursor = txn.cursor()
    keys = [k.decode('utf-8', errors='replace') for k, _ in cursor]

print(f"Total keys: {len(keys)}")
print(f"Sample keys: {keys[:10]}")

# Check for numeric pairs (image at even, mask at odd index)
with env.begin() as txn:
    checked = 0
    for i in range(0, min(len(keys), 400), 2):
        img_data = txn.get(keys[i].encode())
        mask_data = txn.get(keys[i+1].encode()) if i+1 < len(keys) else None
        
        if img_data is None or mask_data is None:
            continue
        
        # Try decode mask
        try:
            mask_img = Image.open(io.BytesIO(mask_data))
            mask_arr = np.array(mask_img.convert("L"))
            tamper_ratio = np.sum(mask_arr > 10) / mask_arr.size
            ratios.append((i, tamper_ratio))
            checked += 1
        except:
            pass

print(f"\nChecked {checked} image-mask pairs")
if ratios:
    tamper_ratios = [r for _, r in ratios]
    print(f"Min tamper ratio: {min(tamper_ratios):.6f}")
    print(f"Max tamper ratio: {max(tamper_ratios):.6f}")
    print(f"Mean tamper ratio: {np.mean(tamper_ratios):.6f}")
    zero_count = sum(1 for r in tamper_ratios if r == 0)
    print(f"Images with zero tamper (authentic): {zero_count}/{checked}")
    
    # Sort by tamper ratio
    ratios.sort(key=lambda x: x[1])
    
    # Save 20 with LOWEST tamper ratio as "authentic"
    real_saved = 0
    tampered_saved = 0
    
    with env.begin() as txn:
        # Authentic - lowest tamper ratio
        for idx, ratio in ratios:
            if real_saved >= 20:
                break
            if ratio < 0.01:  # Less than 1% tampered pixels = authentic
                img_data = txn.get(keys[idx].encode())
                try:
                    img = Image.open(io.BytesIO(img_data)).convert("RGB")
                    real_saved += 1
                    save_path = os.path.join(OUTPUT_REAL, f"real_dataset_{real_saved}.jpg")
                    img.save(save_path, "JPEG", quality=95)
                    print(f"  [AUTHENTIC {real_saved}/20] ratio={ratio:.6f} -> {save_path}")
                except:
                    pass
        
        # If not enough authentic found with strict threshold, relax it
        if real_saved < 20:
            print(f"\nOnly {real_saved} authentic found with <1% threshold. Relaxing...")
            for idx, ratio in ratios:
                if real_saved >= 20:
                    break
                img_data = txn.get(keys[idx].encode())
                try:
                    img = Image.open(io.BytesIO(img_data)).convert("RGB")
                    # Check if already saved
                    save_path = os.path.join(OUTPUT_REAL, f"real_dataset_{real_saved+1}.jpg")
                    if not os.path.exists(save_path):
                        real_saved += 1
                        save_path = os.path.join(OUTPUT_REAL, f"real_dataset_{real_saved}.jpg")
                        img.save(save_path, "JPEG", quality=95)
                        print(f"  [AUTHENTIC {real_saved}/20] ratio={ratio:.6f} -> {save_path}")
                except:
                    pass
        
        # Tampered - highest tamper ratio (already have 20 from before, skip if exists)
        existing_tampered = len([f for f in os.listdir(OUTPUT_TAMPERED) if f.startswith("tampered_dataset_")])
        if existing_tampered >= 20:
            print(f"\nAlready have {existing_tampered} tampered images, skipping.")
        else:
            ratios_desc = sorted(ratios, key=lambda x: -x[1])
            for idx, ratio in ratios_desc:
                if tampered_saved >= 20:
                    break
                img_data = txn.get(keys[idx].encode())
                try:
                    img = Image.open(io.BytesIO(img_data)).convert("RGB")
                    tampered_saved += 1
                    save_path = os.path.join(OUTPUT_TAMPERED, f"tampered_dataset_{tampered_saved}.jpg")
                    img.save(save_path, "JPEG", quality=95)
                    print(f"  [TAMPERED {tampered_saved}/20] ratio={ratio:.6f} -> {save_path}")
                except:
                    pass

    print(f"\nFinal: Authentic={real_saved}, Tampered={tampered_saved + existing_tampered}")

env.close()
