from pydantic import BaseModel

class MusicPost(BaseModel):
    format:str
    link:str