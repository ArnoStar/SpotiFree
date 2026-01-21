from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from fastapi.security import OAuth2PasswordRequestForm

from app.shemas.auth import UserSignIn
from app.db.models import User
from app.db.database_sql import get_db
from app.db.database_redis import redis
from app.core.security import hash_password
from app.core.config import settings
from app.services.email import send_confirmation_email

from random import randint
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from datetime import datetime, timedelta
import json

oauth2shema = OAuth2PasswordBearer("/auth/login")

SECRET_KEY = settings.jwt_secret_key
ALGORITHM = settings.jwt_algorithm

REGISTER_EXPIRATION_TIME = settings.register_expiration_time

def create_token(data: dict, delta_exp_time: timedelta | None = None):
    to_encode = data.copy()

    if delta_exp_time:
        to_encode["exp"] = datetime.now() + delta_exp_time
    else:
        to_encode["exp"] = datetime.now() + timedelta(minutes=15)

    encoded = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded

def create_user(email:str, password_hash:str, db:Session = Depends(get_db)):
    user = User(email = email, password_hash = password_hash)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def get_user(email:str, db:Session = Depends(get_db)):
    return db.query(User).filter(User.email == email).first()

def user_exist(email:str, db:Session = Depends(get_db)) -> bool:
    return get_user(email, db) != None

def generate_random_code(lenght:int = 8):
    code = ""
    for _ in range(lenght):
        code+=str(randint(0,9))
    return code

async def add_email_to_confirmation(email:str, password_hash:str, code:int):
    user_info = {"code":code,"password_hash":password_hash, "email":email}
    await redis.set(name = email, value = json.dumps(user_info), ex=REGISTER_EXPIRATION_TIME)

'''
async def valid_email(confirmation:ConfirmationCode, db:Session = Depends(get_db)):
    user_info = await redis.get(confirmation.email)
    if user_info is None:
        raise HTTPException(401, "Email not signed in")
    user_info = json.loads(user_info)
    if user_info["code"] != confirmation.code:
        raise HTTPException(401, "Wrong code")

    user = create_user(confirmation.email, user_info["password_hash"], db)

    await redis.delete(user.email)

    return user
'''