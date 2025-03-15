import cloudinary
import cloudinary.uploader
from app.core.config import settings

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


# https://res.cloudinary.com/dnsp4ojli/image/upload/v1741105349/ln5dmftxq9obaxydvq7l.jpg
# https://res.cloudinary.com/dnsp4ojli/video/upload/v1741108818/v1dyhuc6hmgmr5mlwf1a.mp4
# https://res.cloudinary.com/dnsp4ojli/video/upload/v1741109025/sk2nz9lme4kkfhmlvkd0.mp4

# https://res.cloudinary.com/dnsp4ojli/video/upload/sp_auto/v1741109273/daycache/images/ewmycbfbsgctuh3fyual.m3u8


def delete_from_cloudinary(file_url: str):
    pathlist = file_url.split(".")[0].split("/")[1:]
    public_id = "/".join(pathlist)
    print(public_id)
    result = cloudinary.uploader.destroy(public_id)
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
    