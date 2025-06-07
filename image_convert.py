import os
import shutil
import subprocess


def convert_heic_to_jpg(source_folder, jpg_folder):
    os.makedirs(jpg_folder, exist_ok=True)
    for filename in sorted(os.listdir(source_folder)):
        if os.path.isfile(os.path.join(source_folder, filename)):
          src_path = os.path.join(source_folder, filename)
          if filename.lower().endswith('.heic'):
              jpg_path = os.path.join(jpg_folder, os.path.splitext(filename)[0] + '.jpg')
              subprocess.run(['magick', src_path, jpg_path], check=True)
              print(f"Converted: {filename} -> {jpg_path}")
          else:
              dst_path = os.path.join(jpg_folder, filename)
              shutil.copy2(src_path, dst_path)
              print(f"Copied: {filename} -> {dst_path}")