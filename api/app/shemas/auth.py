from pydantic import BaseModel, field_validator

class UserLogIn(BaseModel):
    email:str
    password:str

class UserSignIn(BaseModel):
    email:str
    password:str
    password_confirm:str

    @field_validator("password_confirm")
    @classmethod
    def passwords_match(cls, password_confirm, info):
        password = info.data.get("password")
        if password != password_confirm:
            raise ValueError("Passwords do not match")
        return password_confirm

class ConfirmationIn(BaseModel):
    code:str
    email:str