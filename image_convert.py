import os
import shutil
import rawpy
import imageio
from pillow_heif import register_heif_opener
register_heif_opener()
from PIL import Image

def convert_dng_to_jpg(src_path, output_path):
    with rawpy.imread(src_path) as raw:
        rgb = raw.postprocess()
    imageio.imwrite(output_path, rgb)

def convert_heic_dng_to_jpg(source_folder, jpg_folder):
    os.makedirs(jpg_folder, exist_ok=True)
    for filename in sorted(os.listdir(source_folder)):
        if os.path.isfile(os.path.join(source_folder, filename)):
          src_path = os.path.join(source_folder, filename)
          if filename.lower().endswith('.heic'):
              with Image.open(src_path) as im:
                  rgb_im = im.convert("RGB")
                  output_path = os.path.join(jpg_folder, f"{os.path.splitext(filename)[0]}.jpg")
                  rgb_im.save(output_path, "JPEG", quality=95)
                  print(f"Converted: {filename} -> {output_path}")

          elif filename.lower().endswith('.dng'):
            # DNG to JPG
            output_path = os.path.join(jpg_folder, f"{os.path.splitext(filename)[0]}.jpg")
            convert_dng_to_jpg(src_path, output_path)
            print(f"Converted DNG: {filename} -> {output_path}")


          else:
              dst_path = os.path.join(jpg_folder, filename)
              shutil.copy2(src_path, dst_path)
              print(f"Copied: {filename} -> {dst_path}")