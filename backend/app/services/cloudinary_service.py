import os
import time
import hashlib
import requests
from dotenv import load_dotenv

load_dotenv()

CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME")
API_KEY = os.getenv("CLOUDINARY_API_KEY")
API_SECRET = os.getenv("CLOUDINARY_API_SECRET")


def upload_image_to_cloudinary(file_bytes: bytes, filename: str):
    timestamp = str(int(time.time()))

    # Tạo chữ ký
    string_to_sign = f"timestamp={timestamp}{API_SECRET}"
    signature = hashlib.sha1(string_to_sign.encode("utf-8")).hexdigest()

    url = f"https://api.cloudinary.com/v1_1/{CLOUD_NAME}/image/upload"

    files = {
        "file": (filename, file_bytes)
    }

    data = {
        "api_key": API_KEY,
        "timestamp": timestamp,
        "signature": signature
    }

    response = requests.post(url, files=files, data=data)
    response.raise_for_status()

    return response.json()