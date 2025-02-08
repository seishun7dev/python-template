from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String
from pydantic import BaseModel

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50))
    email = Column(String(100), unique=True)

# --------------------------
# Pydantic Models
# --------------------------
class UserCreate(BaseModel):
    name: str
    email: str

