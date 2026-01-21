from fastapi import APIRouter
from fastapi import Depends

from app.services.auth import login_user, signin_user, get_current_user, valid_email
from app.db.models import User

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/login")
def login(token: str = Depends(login_user)):
    return {"access_token": token, "token_type": "bearer"}

@router.post("/signin")
def signin(result: str = Depends(signin_user)):
    return result

@router.post("/confirm")
def confirm(user: str = Depends(valid_email)):
    return user

@router.get("/me")
def me(user:User = Depends(get_current_user)):
    return user