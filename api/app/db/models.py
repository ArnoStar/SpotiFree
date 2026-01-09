from sqlalchemy import Column, Integer, String

from app.db.database_sql import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, unique=True)
    email = Column(String, index=True, unique=True)
    password_hash = Column(String)
