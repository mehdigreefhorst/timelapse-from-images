from pathlib import Path
import subprocess
from align_images_improved import align_images, apply_to_fullres
import os
import shutil
import datetime
from timelapse import create_slow_motion_transition, create_timelapse

def convert_heic_to_jpg(source_folder, jpg_folder):
    os.makedirs(jpg_folder, exist_ok=True)
    for filename in sorted(os.listdir(source_folder)):
        src_path = os.path.join(source_folder, filename)
        if filename.lower().endswith('.heic'):
            jpg_path = os.path.join(jpg_folder, os.path.splitext(filename)[0] + '.jpg')
            subprocess.run(['sips', '-s', 'format', 'jpeg', src_path, '--out', jpg_path])
            print(f"Converted: {filename} -> {jpg_path}")
        else:
            dst_path = os.path.join(jpg_folder, filename)
            shutil.copy2(src_path, dst_path)
            print(f"Copied: {filename} -> {dst_path}")

def timelapse_from_images(input_folder_path):
    session_date = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
    base_dir = Path("sessions") / session_date
    base_dir.mkdir(parents=True, exist_ok=True)

    input_path = Path(input_folder_path)
    contains_heic = any(f.lower().endswith(".heic") for f in os.listdir(input_path))

    if contains_heic:
        fullres_dir = base_dir / "converted_jpg"
        convert_heic_to_jpg(input_path, fullres_dir)
    else:
        fullres_dir = input_path

    reduced_output = base_dir / "processed"
    fullres_output = base_dir / "fullres_aligned"
    transform_file = reduced_output / "transformations.json"

    print(f"[INFO] Aligning images from: {fullres_dir}")
    print(f"[INFO] Temporary reduced output: {reduced_output}")
    print(f"[INFO] Aligned full-resolution output: {fullres_output}")
    print(f"[INFO] Transformation file: {transform_file}")

    align_images(str(fullres_dir), str(reduced_output), str(transform_file))

    image_files = sorted([f for f in os.listdir(fullres_dir) if f.lower().endswith(('.jpg', '.jpeg'))])
    if not image_files:
        raise FileNotFoundError("No .jpg images found in the input folder.")

    first_image = image_files[0]
    apply_to_fullres(str(transform_file), str(fullres_dir), str(fullres_output), first_image)

    images_folder = fullres_output

    output_standard = base_dir / "timelapse.mp4"
    create_timelapse(str(images_folder), str(output_standard), fps=1)
    print(f"[INFO] Saved timelapse to: {output_standard}")

    output_smooth = base_dir / "timelapse_smooth.mp4"
    create_slow_motion_transition(str(images_folder), str(output_smooth), fps=30, transition_frames=60)
    print(f"[INFO] Saved smooth timelapse to: {output_smooth}")

if __name__ == "__main__":
    input_path = os.path.abspath("photos_plants")
    timelapse_from_images(input_path)
