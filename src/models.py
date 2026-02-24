import sqlmodel

from sqlmodel import Field, Session, SQLModel, Column, TEXT

class User(SQLModel, table=True):
  __tablename__ = "users"
  id: int | None = Field(default=None, primary_key=True)
  name: str = Field(index=True)

class Hook(SQLModel, table=True):
  __tablename__ = "hooks"
  id: int | None = Field(default=None, primary_key=True)
  user_id: int | None = Field(default=None)
  name: str = Field(index=True, max_length=255, unique=True)
  content: str = Field(index=False, max_length=2**16-1)
