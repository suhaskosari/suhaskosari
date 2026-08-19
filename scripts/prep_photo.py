"""
Prepares a source photo for ASCII conversion:
1. Removes the background (rembg) so only the subject remains.
2. Boosts local contrast with CLAHE so a flat face gets real highlights/shadows.
3. Composites onto pure white so the background maps to blank space in the ASCII ramp.

Usage:
    python prep_photo.py path/to/source-photo.jpg
Output:
    scripts/source-prepped.png (grayscale)
"""
import sys
import os
import numpy as np
import cv2
from PIL import Image
from rembg import remove

OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "source-prepped.png")


def main():
    if len(sys.argv) != 2:
        print("Usage: python prep_photo.py path/to/source-photo.jpg")
        sys.exit(1)

    src_path = sys.argv[1]
    if not os.path.isfile(src_path):
        print(f"File not found: {src_path}")
        sys.exit(1)

    with open(src_path, "rb") as f:
        input_bytes = f.read()

    # Step 1: remove background -> RGBA image with transparent background
    result_bytes = remove(input_bytes)
    subject = Image.open(__import__("io").BytesIO(result_bytes)).convert("RGBA")

    # Step 2: composite onto pure white
    white_bg = Image.new("RGBA", subject.size, (255, 255, 255, 255))
    composited = Image.alpha_composite(white_bg, subject).convert("RGB")

    # Step 3: grayscale + CLAHE contrast boost
    gray = cv2.cvtColor(np.array(composited), cv2.COLOR_RGB2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)

    Image.fromarray(enhanced).save(OUTPUT_PATH)
    print(f"Wrote {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
