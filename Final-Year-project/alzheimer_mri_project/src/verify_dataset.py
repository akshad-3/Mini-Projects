import os
from pathlib import Path
from collections import Counter
from PIL import Image

data_dir = Path("data")
valid_extensions = {".jpg", ".jpeg", ".png", ".bmp", ".tiff"}

print(f"Scanning local dataset directory: {data_dir.resolve()}\n")

if not data_dir.exists() or not any(data_dir.iterdir()):
    print("❌ Error: The 'data/' folder is empty or does not exist!")
    print("Please place your class folders inside ~/Desktop/alzheimer_mri_project/data/")
else:
    image_records = []
    folder_counts = Counter()
    corrupted_images = []

    for ext in valid_extensions:
        for img_path in data_dir.glob(f"**/*{ext}"):
            if img_path.is_file():
                class_name = img_path.parent.name
                folder_counts[class_name] += 1
                try:
                    with Image.open(img_path) as img:
                        img.verify()
                    image_records.append(img_path)
                except Exception as e:
                    corrupted_images.append((img_path, str(e)))

    print("=" * 50)
    print("LOCAL DATASET CLASS SUMMARY:")
    print("=" * 50)
    for cls, count in sorted(folder_counts.items()):
        print(f"📁 Class '{cls}': {count} images")

    print(f"\nTotal Valid Images: {len(image_records)}")
    
    if corrupted_images:
        print(f"⚠️ Corrupted images found: {len(corrupted_images)}")
    else:
        print("✅ All scanned images passed integrity checks!")
