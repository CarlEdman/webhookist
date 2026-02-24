#! python3

import hashlib

from fastapi import FastAPI, WebSocket, Depends, HTTPException, Query, Response, WebSocketDisconnect, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import Annotated

from sqlalchemy import Boolean

from settings import settings
from models import User, UserInDB

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

def get_user(db, username: str) -> User | None:
  if username in db:
    return UserInDB(**db[username])

security_scheme = OAuth2PasswordBearer(tokenUrl="token")
TokenDep = Annotated[str, Depends(security_scheme)]
base_hash= hashlib.sha256(settings.salt.encode())

def hash_password(password: str) -> str:
  h = base_hash.clone()
  return h.update(password.encode()).hexdigest()

def test_password(password: str, hash:str) -> Boolean:
  return hash == hash_password(password)

async def get_current_user(token: TokenDep) -> User:
  user = fake_decode_token(token)
  if not user:
    raise HTTPException(
      status_code=status.HTTP_401_UNAUTHORIZED,
      detail="Not authenticated",
      headers={"WWW-Authenticate": "Bearer"},
    )
  if user.disabled:
    raise HTTPException(
      status_code=status.HTTP_403_FORBIDDEN,
      detail="Inactive user",
      headers={"WWW-Authenticate": "Bearer"},
    )
    
  return user

async def get_current_active_user(current_user: Annotated[User, Depends(get_current_user)]) -> User:
  if current_user.disabled:
    raise HTTPException(status_code=400, detail="Inactive user")
  return current_user

