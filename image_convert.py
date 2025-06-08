import os
import shutil
import subprocess
from pillow_heif import register_heif_opener
register_heif_opener()
from PIL import Image



def convert_heic_to_jpg(source_folder, jpg_folder):
    os.makedirs(jpg_folder, exist_ok=True)
    for filename in sorted(os.listdir(source_folder)):
        if os.path.isfile(os.path.join(source_folder, filename)):
          src_path = os.path.join(source_folder, filename)
          if filename.lower().endswith('.heic'):
              with Image.open(src_path) as im:
                  rgb_im = im.convert("RGB")
                  output_path = os.path.join(jpg_folder, os.path.splitext(filename)[0])
                  rgb_im.save(output_path, "JPEG", quality=95)
                  print(f"Converted: {filename} -> {output_path}")

          else:
              dst_path = os.path.join(jpg_folder, filename)
              shutil.copy2(src_path, dst_path)
              print(f"Copied: {filename} -> {dst_path}")