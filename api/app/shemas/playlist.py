from pydantic import BaseModel
from datetime import datetime

class PlayListGet(BaseModel):
    id:int
    author_id:int
    creation_date:datetime
    music_ids:list[str]