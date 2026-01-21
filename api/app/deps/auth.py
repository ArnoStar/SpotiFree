from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from app.core.config import settings
from app.db.database_redis import redis
from app.db.database_sql import get_db
from app.db.models import User
from app.services.auth import get_user, user_exist
from app.shemas.auth import UserSignIn, ConfirmationIn
from app.core.security import verify_password

from sqlalchemy.orm import Session
from jose import jwt, JWTError
import json

oauth2shema = OAuth2PasswordBearer("/auth/login")

SECRET_KEY = settings.jwt_secret_key
ALGORITHM = settings.jwt_algorithm

REGISTER_EXPIRATION_TIME = settings.register_expiration_time

def verify_token(token: str = Depends(oauth2shema)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload["user"]
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    return payload

def get_current_user(token_data: dict = Depends(verify_token), db: Session = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    user = get_user(token_data["user"], db)
    if user is None:
        raise credentials_exception
    return user

def verify_credentials(credentials:OAuth2PasswordRequestForm = Depends(), db:Session = Depends(get_db)) -> User:
    if get_user(credentials.username, db) is None:
        raise HTTPException(401, "Invalid credentials, the email isn't registered")
        
    user:User = get_user(credentials.username, db)

    if not verify_password(credentials.password, user.password_hash):
        raise HTTPException(401, "Invalid credentials, wrong password")
            
    return user

def verify_new_user_information(user_info:UserSignIn, db:Session = Depends(get_db)) -> UserSignIn:
    if user_exist(user_info.email, db):
        raise HTTPException(409, "Already exists")
    if user_info.password != user_info.password_confirm:
        raise HTTPException(401, "Password confirmation wrong")
    return user_info

async def verify_validation_code(confirmation:ConfirmationIn) -> dict[str:str]:
    user_info = await redis.get(confirmation.email)
    if user_info is None:
        raise HTTPException(401, "Email not signed in")
    user_info = json.loads(user_info)
    if user_info["code"] != confirmation.code:
        raise HTTPException(401, "Wrong code")
    
    return user_info