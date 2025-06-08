import os
import shutil
import time
from supabase import create_client, Client
from timelapse import extract_input_settings
from timelapse_from_job import timelapse_from_images
from dotenv import load_dotenv

load_dotenv()
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_SERVICE_ROLE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
BUCKET_NAME = os.environ.get("SUPABASE_BUCKET", "timelapsevideos")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

def fetch_next_job():
    res = supabase.from_("timelapse_jobs").select("*").eq("status", "pending").order("created_at").limit(1).execute()
    if res.data and len(res.data) > 0:
        return res.data[0]
    return None

def mark_job_processing(job_id):
    supabase.from_("timelapse_jobs").update({"status": "processing"}).eq("id", job_id).execute()

def mark_job_done(job_id, video_url, signed_download_url):
    supabase.from_("timelapse_jobs").update({"status": "completed", "video_url": signed_download_url}).eq("id", job_id).execute()

def download_folder(folder_path: str, local_dir: str):
    os.makedirs(local_dir, exist_ok=True)
    print(f"Downloading from: {folder_path}")
    res = supabase.storage.from_("timelapseimages").list(folder_path)
    for file in res:
        file_name = file["name"]
        if file_name == "video":
            continue
        full_path = f"{folder_path}/{file_name}"
        download = supabase.storage.from_("timelapseimages").download(full_path)
        with open(os.path.join(local_dir, file_name), "wb") as f:
            f.write(download)

def upload_video(job, video_path: str) -> str:
    storage_path = f'{job["folder_path"]}/video/timelapse.mp4'
    with open(video_path, "rb") as f:
        supabase.storage.from_(BUCKET_NAME).upload(storage_path, f.read(), {"content-type": "video/mp4"})
    signed = supabase.storage.from_(BUCKET_NAME).create_signed_url(storage_path, 3600)
    signed_download_url = supabase.storage.from_(BUCKET_NAME).create_signed_url(storage_path, 3600, {"download": True})

    print("signed url = ", signed)
    return signed["signedUrl"], signed_download_url["signedUrl"]

def upload_aligned_photos(job, images_folder_path: str) -> str:
    storage_path = f'{job["folder_path"]}/aligned_images'

    for file_name in os.listdir(images_folder_path):
        file_path = os.path.join(images_folder_path, file_name)
        storage_path_file = os.path.join(storage_path, file_name)
        with open(file_path, "rb") as f:
            supabase.storage.from_(BUCKET_NAME).upload(storage_path_file, f.read(), {"content-type": "image/jpg"})

def process_job(job):
    print(f"Processing job: {job['id']}")
    mark_job_processing(job["id"])
    local_input = f"tmp/{job['id']}"
    download_folder(job["folder_path"], local_input)
    input_settings = extract_input_settings(job)
    print("input settings = ", input_settings)
    output_video_path, aligned_images_path = timelapse_from_images(local_input, input_settings)  # ✅ call your existing processing pipeline
    signed_url, signed_download_url = upload_video(job, output_video_path)
    #upload_aligned_photos(job, aligned_images_path)
    mark_job_done(job["id"], signed_url, signed_download_url)
    shutil.rmtree(local_input)

if __name__ == "__main__":
    # storage_path = f'{"2d852821-22f6-432c-aea7-b5c9e0e4b409/6eb960cd-faca-4213-8a6e-c42b64085517"}/video/timelapse.mp4'
    # signed = supabase.storage.from_(BUCKET_NAME).create_signed_url(storage_path, 3600, {"download": True})
    # print("signed url = ", signed)
    # raise Exception("hi")
    while True:
        print("fetch one")
        job = fetch_next_job()
        if job:
            process_job(job)
            # try:
                
            # except Exception as e:
            #     print(f"[ERROR] Failed processing job {job['id']}: {e}")
        else:
            print("No pending jobs. Waiting...")
            time.sleep(10)
