#! python3

from fastapi import FastAPI, WebSocket, Depends, HTTPException, Query, Response, WebSocketDisconnect, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import Annotated

from settings import settings

fake_users_db = {
  "johndoe": {
    "username": "johndoe",
    "full_name": "John Doe",
    "email": "johndoe@example.com",
    "hashed_password": "fakehashedsecret",
    "disabled": False,
  },
  "alice": {
    "username": "alice",
    "full_name": "Alice Wonderson",
    "email": "alice@example.com",
    "hashed_password": "fakehashedsecret2",
    "disabled": True,
  },
}

class User(BaseModel):
  username: str
  email: str | None = None
  full_name: str | None = None
  disabled: bool = False

class UserInDB(User):
  hashed_password: str

def get_user(db, username: str) -> User | None:
  if username in db:
    return UserInDB(**db[username])

security_scheme = OAuth2PasswordBearer(tokenUrl="token")

def fake_hash_password(password: str) -> str:
  return "fakehashed" + password

def fake_decode_token(token) -> User:
  user = get_user(fake_users_db, token)
  return user

async def get_current_user(token: Annotated[str, Depends(security_scheme)]) -> User:
  user = fake_decode_token(token)
  if not user:
    raise HTTPException(
      status_code=status.HTTP_401_UNAUTHORIZED,
      detail="Not authenticated",
      headers={"WWW-Authenticate": "Bearer"},
    )
  return user

async def get_current_active_user(current_user: Annotated[User, Depends(get_current_user)]) -> User:
  if current_user.disabled:
    raise HTTPException(status_code=400, detail="Inactive user")
  return current_user


if __name__ == "__main__":
  pass

