import os
import cv2
import numpy as np
import json
import logging
import multiprocessing
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
import re

def get_optimal_process_count():
    return multiprocessing.cpu_count()

def resize_image(image, target_width=1280):
    h, w = image.shape[:2]
    scale = min(target_width / w, 720 / h)
    if scale < 1:
        new_size = (int(w * scale), int(h * scale))
        return cv2.resize(image, new_size, interpolation=cv2.INTER_AREA), scale
    return image, 1.0

def add_day_label(image, filename, base_date="20250521"):
    date_match = re.search(r'(\d{8})', filename)
    if date_match:
        date_str = date_match.group(1)
        try:
            year = int(date_str[:4])
            month = int(date_str[4:6])
            day = int(date_str[6:8])
            import datetime
            current_date = datetime.date(year, month, day)
            base_date_obj = datetime.date(int(base_date[:4]), int(base_date[4:6]), int(base_date[6:8]))
            day_diff = (current_date - base_date_obj).days + 1
            label = f"Day {day_diff}"
        except Exception as e:
            logging.warning(f"Failed to calculate day number: {e}")
            label = filename
    else:
        label = filename

    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.8
    font_thickness = 2
    font_color = (255, 255, 255)
    outline_color = (0, 0, 0)
    outline_thickness = 3

    h, w = image.shape[:2]
    x_pos = 20
    y_pos = h - 30

    cv2.putText(image, label, (x_pos, y_pos), font, font_scale, outline_color, outline_thickness)
    cv2.putText(image, label, (x_pos, y_pos), font, font_scale, font_color, font_thickness)

    return image

def process_single_image(args):
    image_file, images_folder, output_folder, reference_img_path = args

    try:
        reference_img = cv2.imread(reference_img_path)
        reference_img, ref_scale = resize_image(reference_img)
        reference_gray = cv2.cvtColor(reference_img, cv2.COLOR_BGR2GRAY)
        feature_detector = cv2.SIFT_create()
        reference_keypoints, reference_descriptors = feature_detector.detectAndCompute(reference_gray, None)

        current_path = os.path.join(images_folder, image_file)
        current_img = cv2.imread(current_path)
        if current_img is None:
            logging.error(f"Could not read image: {current_path}")
            return None

        current_img, curr_scale = resize_image(current_img)
        current_gray = cv2.cvtColor(current_img, cv2.COLOR_BGR2GRAY)

        current_keypoints, current_descriptors = feature_detector.detectAndCompute(current_gray, None)
        if len(current_keypoints) < 10:
            logging.warning(f"Too few keypoints in {image_file}, skipping.")
            return None

        matcher = cv2.BFMatcher()
        matches = matcher.knnMatch(reference_descriptors, current_descriptors, k=2)
        good_matches = [m for m, n in matches if m.distance < 0.75 * n.distance]

        if len(good_matches) < 4:
            logging.warning(f"Not enough good matches in {image_file}, skipping.")
            return None

        ref_pts = np.float32([reference_keypoints[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
        curr_pts = np.float32([current_keypoints[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)

        H, _ = cv2.findHomography(curr_pts, ref_pts, cv2.RANSAC, 5.0)

        transform_data = {
            "filename": image_file,
            "homography": H.tolist(),
            "ref_scale": ref_scale,
            "curr_scale": curr_scale
        }
        return transform_data

    except Exception as e:
        logging.error(f"Error processing {image_file}: {str(e)}")
        return None

def align_images(images_folder, output_folder, transform_path):
    os.makedirs(output_folder, exist_ok=True)
    image_files = sorted([f for f in os.listdir(images_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg'))])

    if not image_files:
        logging.error("No images found.")
        return

    reference_path = os.path.join(images_folder, image_files[0])
    ref_img = cv2.imread(reference_path)
    if ref_img is None:
        logging.error("Could not read reference image.")
        return

    ref_img_resized, _ = resize_image(ref_img)
    ref_img_resized = add_day_label(ref_img_resized, image_files[0])
    cv2.imwrite(os.path.join(output_folder, image_files[0]), ref_img_resized)

    tasks = [(image_files[i], images_folder, output_folder, reference_path) for i in range(1, len(image_files))]

    with ProcessPoolExecutor(max_workers=get_optimal_process_count()) as executor:
        results = list(executor.map(process_single_image, tasks))
        transforms = [r for r in results if r]

    with open(transform_path, 'w') as f:
        json.dump(transforms, f, indent=2)

    logging.info(f"Saved transformations for {len(transforms)} images.")

def apply_to_fullres(transform_path, fullres_folder, output_folder, reference_filename):
    os.makedirs(output_folder, exist_ok=True)
    with open(transform_path) as f:
        transforms = json.load(f)

    ref_img = cv2.imread(os.path.join(fullres_folder, reference_filename))
    if ref_img is None:
        logging.error(f"Reference full-res image not found: {reference_filename}")
        return

    h_ref, w_ref = ref_img.shape[:2]
    cv2.imwrite(os.path.join(output_folder, reference_filename), ref_img)

    for t in transforms:
        img_path = os.path.join(fullres_folder, t["filename"])
        full_img = cv2.imread(img_path)
        if full_img is None:
            logging.warning(f"Missing image: {t['filename']}")
            continue

        H = np.array(t["homography"])
        S_ref = np.diag([1 / t["ref_scale"], 1 / t["ref_scale"], 1])
        S_curr = np.diag([t["curr_scale"], t["curr_scale"], 1])
        H_scaled = S_ref @ H @ S_curr

        aligned = cv2.warpPerspective(full_img, H_scaled, (w_ref, h_ref))
        aligned = add_day_label(aligned, t["filename"])
        cv2.imwrite(os.path.join(output_folder, t["filename"]), aligned)
        logging.info(f"Aligned full-res image: {t['filename']}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    base_dir = Path(__file__).parent
    fullres_dir = base_dir / "converted_jpg"
    reduced_output = base_dir / "processed"
    fullres_output = base_dir / "fullres_aligned"
    transform_file = reduced_output / "transformations.json"

    align_images(str(fullres_dir), str(reduced_output), str(transform_file))

    first_image = sorted([f for f in os.listdir(fullres_dir) if f.lower().endswith(('.jpg', '.jpeg'))])[0]
    apply_to_fullres(str(transform_file), str(fullres_dir), str(fullres_output), first_image)
