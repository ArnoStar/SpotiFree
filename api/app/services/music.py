from fastapi import HTTPException, Depends

from app.shemas.music import MusicPost
from app.core.config import settings
from app.db.database_sql import get_db
from app.db.models import Music, User
from app.deps.auth import get_current_user
from app.services.deps import register_function

from pytubefix import AsyncYouTube
from pytubefix.exceptions import VideoUnavailable, RegexMatchError
from sqlalchemy.orm import Session
from typing import Callable

AUDIO_DIR = settings.audio_dir

downloaders:dict[str, Callable[[str], str]] = dict()

def add_metadata_music(music_id:str, user:User, db:Session):
    music = Music(id=music_id, added_by=user)
    db.add(music)
    db.commit()
    db.refresh(music)

    return music

def get_metadata_music(music_id:str, db:Session = Depends(get_db)) -> Music:
    return db.query(Music).filter(Music.id == music_id).first()

def music_exist(music_id:str,  db:Session):
    return get_metadata_music(music_id, db) != None

def verify_music(music_id:str, db:Session):
    if music_exist(music_id, db):
        raise HTTPException(400, "The song already exist")

def get_video_from_youtube(url:str) -> AsyncYouTube:
    try:
        video = AsyncYouTube(url)
    except RegexMatchError:
        raise HTTPException(400, "Wrong link, you need a valid youtube link")

    return video

@register_function(downloaders, "youtube")
async def download_music_youtube(video:AsyncYouTube):
    try:
        streams = await video.streams()
    except VideoUnavailable:
        raise HTTPException(404, "Video not found or unavailable")
    
    filename = f"{video.video_id}.mp3"

    audio = streams.get_audio_only()
    audio.download(filename=filename, output_path=AUDIO_DIR)

    return AUDIO_DIR+filename
        
async def add_music(music_information:MusicPost, user:User = Depends(get_current_user), db:Session = Depends(get_db)):
    format:str = music_information.format
    url:str = music_information.link
    video = get_video_from_youtube(url)
    download = downloaders.get(format)
    music_id = video.video_id

    if download is None:
        raise HTTPException(400, "Invalid format")

    verify_music(music_id, db)
    await download(video)
    music_metadata = add_metadata_music(music_id, user, db)

    return music_metadata
