import os
import subprocess
from pathlib import Path

def convert_heic_to_jpg(source_dir, output_dir, quality=90):
    src = Path(source_dir)
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    for heic in sorted(src.rglob("*.HEIC")):
        jpg = out / heic.with_suffix('.jpg').name
        subprocess.run([
            "convert", str(heic),
            "-quality", str(quality),
            str(jpg)
        ], check=True)
        print(f"{heic.name} → {jpg.name}")