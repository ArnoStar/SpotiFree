from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import StreamingResponse

from app.services.music import add_music

import os

router = APIRouter(prefix="/music", tags=["Music"])

@router.post("/")
def post_music(music = Depends(add_music)):
    return music

