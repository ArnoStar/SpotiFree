from fastapi import APIRouter
from fastapi import Depends

from app.services.auth import login_user, signin_user, get_current_user
from app.db.models import User

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/login")
def login(token: str = Depends(login_user)):
    print(token)
    return {"access_token": token, "token_type": "bearer"}

@router.post("/signin")
def signin(user: str = Depends(signin_user)):
    return user

@router.get("/me")
def me(user:User = Depends(get_current_user)):
    return user