from fastapi import APIRouter, Depends

from app.db.models import PlayList, PlayListMusic, UserPlayList
from app.services.playlist import add_playlist, get_playlist_with_musics, current_user_follow_playlist, add_music_to_playlist
from app.shemas.playlist import PlayListGet

router = APIRouter(prefix="/playlist", tags=["Playlist"])

@router.post("/")
def post_pl(playlist:PlayList = Depends(add_playlist)):
    return playlist

@router.get("/{id}")
def get_pl(playlist:PlayList = Depends(get_playlist_with_musics), response_model=PlayListGet):
    return playlist

@router.put("/{id}/follow")
def put_current_user_to_pl(playlist_user_link:UserPlayList = Depends(current_user_follow_playlist)):
    return playlist_user_link

@router.put("/{id}/add/{music_id}")
def put_music_to_pl(playlist_music_link = Depends(add_music_to_playlist)):
    return playlist_music_link
