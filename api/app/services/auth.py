from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from fastapi.security import OAuth2PasswordRequestForm

from app.shemas.auth import UserSignIn, ConfirmationCode
from app.db.models import User
from app.db.database_sql import get_db
from app.db.database_redis import redis
from app.core.security import hash_password
from app.core.config import settings

from random import randint
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from datetime import datetime, timedelta
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

def get_current_user(token_data: dict = Depends(verify_token), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    user = get_user(token_data["user"], db)
    if user is None:
        raise credentials_exception
    return user

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

def login_user(form_data: OAuth2PasswordRequestForm = Depends(), db:Session = Depends(get_db)):
    user = get_user(form_data.username, db)
    if user is None:
        raise HTTPException(401, "Invalid credentials, the email isn't registered")
    
    token = create_token({"user":user.email})

    return token

async def signin_user(user_information:UserSignIn, db = Depends(get_db)):
    if get_user(user_information.email, db) is not None:
        raise HTTPException(409, "Already exists")
    
    password_hash = hash_password(user_information.password)
    #shity code for confimation code
    confirmation_code = ""
    for _ in range(8):
        confirmation_code+=str(randint(0,9))

    user_info = {"code":confirmation_code,
                 "password_hash": password_hash}
    print(user_info)
    await redis.set(name = user_information.email, value = json.dumps(user_info), ex=REGISTER_EXPIRATION_TIME)

    return {"message":"Please confirm your email"}

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