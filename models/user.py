from datetime import datetime
from sqlmodel import Field, SQLModel

class User(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    email: str = Field(unique=True)
    password: str
    date_created: datetime = Field(default_factory=datetime.now)
    date_edited: datetime = Field(default_factory=datetime.now)
