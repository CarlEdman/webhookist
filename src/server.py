#! python3

import logging

#import secrets

import uvicorn
import sqlmodel

from fastapi import FastAPI, Depends, HTTPException, Query, Response, status
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, FileResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from typing import Annotated
from sqlmodel import Session, SQLModel, select, func
from contextlib import asynccontextmanager

from settings import settings
from templates import templates
from static import static
from security import get_current_user, hash_password
from websockets import endpoint as ws_endpoint
from models import User, UserInDB
from log import log

def get_session():
  with Session(engine) as session:
    yield session

SessionDep = Annotated[Session, Depends(get_session)]
UserDep = Annotated[User, Depends(get_user)]


@asynccontextmanager
async def lifespan(app: FastAPI):
  SQLModel.metadata.create_all(engine)
  with Session(engine) as session:
    user = session.get(User, 0)
    if not user:
 #     pw = secrets.token_urlsafe(nbytes=6)
      pw = "ragamuffin"
      user = UserInDB(id = 0, username="superuser", superuser=True, password_hash=hash_password(pw))
      session.add(user)
      session.commit()
      log.info(f'No superuser account found.  Generating new one with password "{pw}"')
  yield

app = FastAPI(lifespan=lifespan)
engine = sqlmodel.create_engine(settings.sqlurl, connect_args={"check_same_thread": False}, echo=True)
app.mount("/static", static , name="static")
app.websocket("/ws", name="ws")(ws_endpoint)

#app.add_middleware(HTTPSRedirectMiddleware)

@app.get("/favicon.ico")
async def favicon() -> Response:
  return FileResponse( "static/favicon.ico")

@app.get("/")
async def root() -> Response:
  return FileResponse("static/index.html")

# async def root() -> Response:
#   return RedirectResponse(url="static/index.html", status_code=status.HTTP_307_TEMPORARY_REDIRECT)

@app.get("/hooks/{user_id}")
async def read_user(user_id: int, user: UserDep) -> Response:
  return JSONResponse({"user_id": user_id})

@app.get("/hooks/")
async def read_users(token: Annotated[str, Depends(security_scheme)], user: UserDep):
  return {"token": token}

@app.get("/users/me")
async def read_users_me(user: UserDep) -> User:
  return user

if __name__ == "__main__":
  uvicorn.run(app, host=settings.host, port=settings.port)
