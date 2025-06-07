import os
from pathlib import Path
from PIL import Image
from pillow_heif import register_heif_opener

register_heif_opener()

def convert_heic_to_jpg(source_folder, jpg_folder, quality=95):
    source = Path(source_folder)
    target = Path(jpg_folder)
    target.mkdir(parents=True, exist_ok=True)
    for heic in source.rglob("*.[hH][eE][iI][cC]"):
        rel = heic.relative_to(source)
        out_jpg = (target / rel).with_suffix('.jpg')
        out_jpg.parent.mkdir(parents=True, exist_ok=True)
        with Image.open(heic) as img:
            img.convert('RGB').save(out_jpg, 'JPEG', quality=quality)
        print(f"Converted: {heic} → {out_jpg}")