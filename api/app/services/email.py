from fastapi_mail import FastMail, MessageSchema

from app.core.config import mail_config

from pydantic import EmailStr

async def send_confirmation_email(email: EmailStr, code:str):
    message = MessageSchema(
        subject="Your confirmation code",
        recipients=[email],
        body=f"Your confirmation code is {code}",
        subtype="plain"
    )

    fm = FastMail(mail_config)
    await fm.send_message(message)