from fastapi import FastAPI

import app.routers.auth as auth
from app.db.database_sql import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(auth.router)