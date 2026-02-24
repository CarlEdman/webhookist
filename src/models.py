from sqlalchemy import Boolean
import sqlmodel

from sqlmodel import Field, Session, SQLModel, Column

class User(SQLModel):
  id: int | None = Field(default=None, primary_key=True)
  username: str = Field(index=True, unique=True)
#  email: str | None = Field(default=None)
#  full_name: str | None = Field(default=None)
  disabled: Boolean = Field(default=False)
  superuser: Boolean = Field(default=False)

class UserInDB(User, table=True):
  __tablename__ = "users"
  password_hash: str = Field()

class Hook(SQLModel, table=True):
  __tablename__ = "hooks"
  id: int = Field(default=None, primary_key=True)
  user_id: int = Field(default=None)
  name: str = Field(index=True, max_length=255)
  content: str = Field(index=False, max_length=2**16-1)
