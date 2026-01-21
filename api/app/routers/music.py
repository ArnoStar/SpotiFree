from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import StreamingResponse

from app.db.database_sql import get_db
from app.services.music import add_music, get_metadata_music

from sqlalchemy.orm import Session

router = APIRouter(prefix="/music", tags=["Music"])

@router.post("/")
def post_music(music = Depends(add_music)):
    return music

@router.get("/")
def get_music(music_id:str, db:Session = Depends(get_db)):
    return get_metadata_music(music_id, db)
