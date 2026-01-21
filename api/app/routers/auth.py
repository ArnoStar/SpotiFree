from fastapi import APIRouter, Depends

from app.core.security import hash_password
from app.core.config import settings
from app.db.models import User
from app.db.database_sql import get_db
from app.db.database_redis import redis
from app.shemas.auth import UserSignIn
from app.deps.auth import verify_credentials, verify_new_user_information, verify_validation_code, get_current_user
from app.services.auth import create_token, generate_random_code, create_user, add_email_to_confirmation
from app.services.email import send_confirmation_email

from sqlalchemy.orm import Session

REGISTER_EXPIRATION_TIME = settings.register_expiration_time

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/login")
def login(user:User = Depends(verify_credentials)):
    token = create_token({"user":user.email})
    return {"access_token": token, "token_type": "bearer"}

@router.post("/signin")
async def signin(user_info: UserSignIn = Depends(verify_new_user_information)):
    confirmation_code = generate_random_code()
    await send_confirmation_email(user_info.email, confirmation_code)
    await add_email_to_confirmation(user_info.email, hash_password(user_info.password), confirmation_code)
    return {"message":"Please confirm your email"}

@router.post("/confirm")
async def confirm(user_info: dict = Depends(verify_validation_code), db:Session = Depends(get_db)):
    user = create_user(user_info["email"], user_info["password_hash"], db)
    await redis.delete(user.email)
    return user

@router.get("/me")
def me(user:User = Depends(get_current_user)):
    return user
