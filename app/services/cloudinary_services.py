import cloudinary
import cloudinary.uploader
from urllib.parse import urlparse
import cloudinary.api
from app.core.config import settings
import re

cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET,
)


def upload_to_cloudinary(file):
    folder = "daycache/"
    folder += "image" if file.content_type.startswith("image") else "files"
    print(file)
    upload_result = cloudinary.uploader.upload(
        file.file, resource_type="auto", folder=folder
    )
    trimmed_url = upload_result["secure_url"].split("upload/")[1]
    print(trimmed_url)
    return trimmed_url

def delete_from_cloudinary(file_url: str):
    # Extract the path from the URL
    parsed_url = urlparse(file_url)
    resource_type = get_resource_type(file_url)
    path = parsed_url.path  # e.g. /demo/image/upload/v1670000000/folder/my_image.jpg

    # Remove version part and extension
    match = re.search(r"/(?:v\d+/)?(.+?)\.\w+$", path)
    if not match:
        raise ValueError("Invalid Cloudinary URL format")

    public_id = match.group(1)  # e.g. folder/my_image
    print("public ID:", public_id)

    # Delete from Cloudinary
    result = cloudinary.uploader.destroy(public_id, resource_type=resource_type)
    print("delete result", result)
    return result


def get_complete_file_url(file_url: str) -> str:
    return f"https://res.cloudinary.com/dnsp4ojli/{get_resource_type(file_url)}/upload/{file_url}"

def get_resource_type(file_url: str) -> str:
    if file_url.endswith((".jpg", ".jpeg", ".png", ".gif", ".webp")):
        return "image"
    elif file_url.endswith((".mp4", ".avi", ".mov", ".mkv", ".webm")):
        return "video"
    else:
        return "raw"
    