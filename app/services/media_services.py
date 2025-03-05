from sqlalchemy.orm import Session
from fastapi import UploadFile
from app.models.media import Media
from fastapi import HTTPException
from app.services.cloudinary_services import upload_to_cloudinary, delete_from_cloudinary

def add_media_to_entry(db: Session, entry_id: int, file: UploadFile):
    upload_result = upload_to_cloudinary(file)

    if not upload_result:
        raise Exception("Failed to upload media to cloudinary")
    
    trimmed_url = upload_result["secure_url"].split("upload/")[1]
    new_media = Media(
        entry_id=entry_id,
        file_url=trimmed_url
    )

    db.add(new_media)
    db.commit()
    db.refresh(new_media)
    return new_media


def delete_media_from_entry(db: Session, entry_id: int, media_id: int):
    media = db.query(Media).filter(Media.id == media_id, Media.entry_id == entry_id).first()

    if not media:
        raise HTTPException(status_code=404, detail="Media not found")
    # delete media from cloudinary
    pathlist = media.file_url.split('.')[0].split('/')[1:]
    public_id = '/'.join(pathlist)
    print(public_id)
    delete_from_cloudinary(public_id, get_resource_type(media.file_url))
    # file_url format -> "v1741112189/daycache/files/volv8qobfty7rp2vymi9.mp4"

    db.delete(media)
    db.commit()

def get_resource_type(file_url: str) -> str:
    if file_url.endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')):
        return 'image'
    elif file_url.endswith(('.mp4', '.avi', '.mov', '.mkv', '.webm')):
        return 'video'
    else:
        return 'raw'

def get_media_for_entry(db: Session, entry_id: int):
    media_list = db.query(Media).filter(Media.entry_id == entry_id).all()
    #inject the cloudinary url
    for media in media_list:
        media.file_url = f"https://res.cloudinary.com/dnsp4ojli/{get_resource_type(media.file_url)}/upload/{media.file_url}"
    return media_list

def get_single_media(db: Session, entry_id: int, media_id: int):
    media = db.query(Media).filter(
        Media.id == media_id,
        Media.entry_id == entry_id
    ).first()

    media.file_url = f"https://res.cloudinary.com/dnsp4ojli/{get_resource_type(media.file_url)}/upload/{media.file_url}"

    if not media:
        raise HTTPException(status_code=404, detail="Media not found")

    return media