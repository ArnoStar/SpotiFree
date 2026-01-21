from fastapi import FastAPI

from app.routers.auth import router as auth_router
from app.routers.music import router as media_router
from app.routers.playlist import router as playlist_router
from app.db.database_sql import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(auth_router)
app.include_router(media_router)
app.include_router(playlist_router)