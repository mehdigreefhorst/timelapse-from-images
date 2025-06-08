from pathlib import Path
from align_images_improved import align_images, apply_to_fullres
import os
from image_convert import convert_heic_dng_to_jpg
from timelapse import InputSettings, create_slow_motion_transition, create_timelapse



def timelapse_from_images(input_folder_path, input_settings: InputSettings):


    input_path = Path(input_folder_path)
    contains_heic_dng = any((f.lower().endswith(".heic") or f.lower().endswith(".dng")) for f in os.listdir(input_path))

    if contains_heic_dng:
        fullres_dir = input_path / "converted_jpg"
        convert_heic_dng_to_jpg(input_path, fullres_dir)
    else:
        fullres_dir = input_path

    reduced_output = input_path / "processed"
    fullres_output = input_path / "fullres_aligned"
    transform_file = reduced_output / "transformations.json"

    print(f"[INFO] Aligning images from: {fullres_dir}")
    print(f"[INFO] Temporary reduced output: {reduced_output}")
    print(f"[INFO] Aligned full-resolution output: {fullres_output}")
    print(f"[INFO] Transformation file: {transform_file}")

    if input_settings.alignment == False:
        fullres_output = fullres_dir

    else:
        align_images(str(fullres_dir), str(reduced_output), str(transform_file))
        print(fullres_dir)
        print("os.listdir(fullres_dir) = ", os.listdir(fullres_dir))
        image_files = sorted([f for f in os.listdir(fullres_dir) if f.lower().endswith(('.jpg', '.jpeg'))])
        if not image_files:
            raise FileNotFoundError("No .jpg images found in the input folder.")

        first_image = image_files[0]
        apply_to_fullres(str(transform_file), str(fullres_dir), str(fullres_output), first_image)

    images_folder = fullres_output

    output_standard_timelapse = input_path / "timelapse.mp4"
    fps = 1/input_settings.duration_per_image
    create_timelapse(str(images_folder), str(output_standard_timelapse), fps=fps)
    print(f"[INFO] Saved timelapse to: {output_standard_timelapse}")

    output_smooth_timelapse = input_path / "timelapse_smooth.mp4"
    # create_slow_motion_transition(str(images_folder), str(output_smooth), fps=30, transition_frames=60)
    print(f"[INFO] Saved smooth timelapse to: {output_smooth_timelapse}")
    return output_standard_timelapse, fullres_output

if __name__ == "__main__":
    input_path = os.path.abspath("photos_plants")
    timelapse_from_images(input_path)
