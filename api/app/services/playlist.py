from fastapi import Depends, HTTPException

from app.db.database_sql import get_db
from app.db.models import PlayList, PlayListMusic, UserPlayList, Music, User
from app.deps.auth import get_current_user
from app.services.music import get_metadata_music
from app.shemas.playlist import PlayListGet

from sqlalchemy.orm import Session

def create_playlist(user:User, db:Session) -> PlayList:
    playlist = PlayList(author=user)

    db.add(playlist)
    db.commit()
    db.refresh(playlist)

    return playlist

def follow_playlist(user:User, playlist:PlayList, db:Session) -> UserPlayList:
    for playlist_link in user.playlist_link:
        if playlist_link.playlist.id == playlist.id:
            raise HTTPException(409, f"User id:{user.id} aleready follows this playlist")

    playlist_user_link = UserPlayList(user = user, playlist = playlist)

    db.add(playlist_user_link)
    db.commit()
    db.refresh(playlist_user_link)
    
    return playlist_user_link

def get_playlist(id:int, db:Session = Depends(get_db)) -> PlayList:
    playlist = db.query(PlayList).filter(PlayList.id == id).first()
    return playlist

def add_playlist(user:User = Depends(get_current_user), db:Session = Depends(get_db)) -> PlayList:
    playlist:PlayList = create_playlist(user, db)
    follow_playlist(user, playlist, db)
    return playlist

def get_playlist_with_musics(playlist:PlayList = Depends(get_playlist)) -> PlayListGet:
    music_ids:list[str] = [link.music_id for link in playlist.music_link]

    return PlayListGet(id = playlist.id, author_id = playlist.author.id, creation_date = playlist.creation_date, music_ids = music_ids)

def current_user_follow_playlist(
    user:User = Depends(get_current_user),
    playlist:PlayList = Depends(get_playlist),
    db:Session = Depends(get_db)
    ) -> UserPlayList:

    for playlist_link in user.playlist_link:
        if playlist_link.playlist.id == playlist.id:
            raise HTTPException(409, "You're aleready following this playlist")

    return follow_playlist(user, playlist, db)

def add_music_to_playlist(
    user:User = Depends(get_current_user),
    playlist:PlayList = Depends(get_playlist),
    music:Music = Depends(get_metadata_music),
    db:Session = Depends(get_db)
    ) -> PlayListMusic:

    if playlist is None:
        raise HTTPException(404, "This playlist doesn't exist")
    if playlist.author != user:
        raise HTTPException(403, "You can't add a music to a playlist you don't own")
    if music is None:
        raise HTTPException(404, "This music doesn't exist")
    for music_link in playlist.music_link:
        if music_link.music == music:
            raise HTTPException(409, "This music is aleready in the playlist")

    playlist_music_link = PlayListMusic(playlist=playlist, music=music)

    db.add(playlist_music_link)
    db.commit()
    db.refresh(playlist_music_link)

    return playlist_music_link