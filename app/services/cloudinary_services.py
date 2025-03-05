import cloudinary
import cloudinary.uploader
from app.core.config import settings

cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET
)

def upload_to_cloudinary(file):
    folder = "daycache/"
    folder += "image" if file.content_type.startswith("image") else "files"
    print(file)
    upload_result = cloudinary.uploader.upload(file.file, resource_type="auto", folder=folder)
    print(upload_result)
    return upload_result


# https://res.cloudinary.com/dnsp4ojli/image/upload/v1741105349/ln5dmftxq9obaxydvq7l.jpg
# https://res.cloudinary.com/dnsp4ojli/video/upload/v1741108818/v1dyhuc6hmgmr5mlwf1a.mp4
# https://res.cloudinary.com/dnsp4ojli/video/upload/v1741109025/sk2nz9lme4kkfhmlvkd0.mp4

# https://res.cloudinary.com/dnsp4ojli/video/upload/sp_auto/v1741109273/daycache/images/ewmycbfbsgctuh3fyual.m3u8

def delete_from_cloudinary(pulblic_id: str, resource_type):
    result = cloudinary.uploader.destroy(pulblic_id, resource_type=resource_type)
    return result