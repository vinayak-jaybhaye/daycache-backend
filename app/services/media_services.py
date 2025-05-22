from sqlalchemy.orm import Session
from fastapi import UploadFile
from app.models.media import Media
from fastapi import HTTPException
from app.services.cloudinary_services import (
    upload_to_cloudinary,
    delete_from_cloudinary,
    get_complete_file_url,
)

def add_media_to_entry(entry_id: int, file: UploadFile, db: Session):
    trimmed_url = upload_to_cloudinary(file)
    if not trimmed_url:
        raise Exception("Failed to upload media to cloudinary")

    new_media = Media(entry_id=entry_id, file_url=trimmed_url)

    db.add(new_media)
    db.commit()
    db.refresh(new_media)
    return new_media


def delete_media_from_entry(media_id: int, db: Session):
    media = (
        db.query(Media).filter(Media.id == media_id).first()
    )

    if not media:
        raise HTTPException(status_code=404, detail="Media not found")
    
    # delete media from cloudinary
    result = delete_from_cloudinary(media.file_url)
    # file_url format -> "v1741112189/daycache/files/volv8qobfty7rp2vymi9.mp4"
    # print(result) => {'result': 'ok'}
    if result.get('result') != 'ok':
        return False
    db.delete(media)
    db.commit()
    return True



def get_media_for_entry(db: Session, entry_id: int):
    media_list = db.query(Media).filter(Media.entry_id == entry_id).all()
    # inject the cloudinary url
    for media in media_list:
        media.file_url = get_complete_file_url(media.file_url)
    return media_list


def get_single_media(db: Session, entry_id: int, media_id: int):
    media = (
        db.query(Media).filter(Media.id == media_id, Media.entry_id == entry_id).first()
    )

    media.file_url = get_complete_file_url(media.file_url)

    if not media:
        raise HTTPException(status_code=404, detail="Media not found")

    return media
