import os
import shutil
import cv2
import rawpy
import imageio
from pillow_heif import register_heif_opener
register_heif_opener()
from PIL import Image

STANDARD_FORMATS = ('.jpg', '.jpeg', '.png', '.webp', '.bmp', '.tiff', '.tif', '.heic')
RAW_FORMATS = ('.dng', '.cr2', '.nef', '.arw', '.orf', '.rw2')
ALL_SUPPORTED_FORMATS = STANDARD_FORMATS + RAW_FORMATS


def convert_dng_to_jpg(src_path, output_path):
    with rawpy.imread(src_path) as raw:
        rgb = raw.postprocess()
    imageio.imwrite(output_path, rgb)

def convert_heic_dng_to_jpg(source_folder, jpg_folder):
    """puts all the pictures in the jpg_folder in the correct format"""
    os.makedirs(jpg_folder, exist_ok=True)
    for filename in sorted(os.listdir(source_folder)):
        if os.path.isfile(os.path.join(source_folder, filename)):
          src_path = os.path.join(source_folder, filename)
          ext = os.path.splitext(filename)[1].lower()

          if ext not in ALL_SUPPORTED_FORMATS:
              print(f"Skipping unsupported file: {filename}")
              continue
        
          if ext in STANDARD_FORMATS:
              with Image.open(src_path) as im:
                  rgb_im = im.convert("RGB")
                  output_path = os.path.join(jpg_folder, f"{os.path.splitext(filename)[0]}.jpg")
                  rgb_im.save(output_path, "JPEG", quality=95)
                  print(f"Converted: {filename} -> {output_path}")

          elif ext in RAW_FORMATS:
            # DNG to JPG

            output_path = os.path.join(jpg_folder, f"{os.path.splitext(filename)[0]}.jpg")
            convert_dng_to_jpg(src_path, output_path)
            print(f"Converted RAW format: {filename} -> {output_path}")


          else:
              dst_path = os.path.join(jpg_folder, filename)
              shutil.copy2(src_path, dst_path)
              print(f"Copied: {filename} -> {dst_path}")


def decrease_quality(input_folder, target_resolution):
    for filename in os.listdir(input_folder):
        file_path = os.path.join(input_folder, filename)
        img = cv2.imread(file_path)
        if img is None:
            print(f"Could not read image: {filename}, skipping.")
            continue
        h, w = img.shape[:2]
        scale = min(target_resolution[0] / w, 720 / h)
        if scale < 1:
            new_size = (int(w * scale), int(h * scale))
            resized_img = cv2.resize(img, new_size, interpolation=cv2.INTER_AREA), scale

        # Overwrite the original with reduced quality
        success = cv2.imwrite(file_path, resized_img, [cv2.IMWRITE_JPEG_QUALITY, 100])
        if success:
            print(f"Resized and saved: {filename}")
        else:
            print(f"Failed to write image: {filename}")