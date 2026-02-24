#! python3

import logging
#import secrets
import uvicorn
import sqlmodel

from fastapi import FastAPI, Depends, HTTPException, Query, Response, status
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, FileResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from typing import Annotated, Dict
from sqlmodel import Session, SQLModel, select, func
from contextlib import asynccontextmanager

from settings import settings
from templates import templates
from static import static
from security import TokenDep, hash_password, get_current_user
from websockets import endpoint as ws_endpoint
from models import User, UserInDB, Hook
from log import log

def get_session():
  with Session(engine) as session:
    yield session

SessionDep = Annotated[Session, Depends(get_session)]
UserDep = Annotated[User, Depends(get_current_user)]

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
app.add_middleware(HTTPSRedirectMiddleware)
engine = sqlmodel.create_engine(settings.sqlurl, connect_args={"check_same_thread": False}, echo=True)
app.mount("/static", static , name="static")
app.websocket("/ws", name="ws")(ws_endpoint)

@app.get("/favicon.ico")
async def favicon() -> Response:
  return FileResponse( "static/favicon.ico")

@app.get("/")
async def root() -> Response:
  return FileResponse("static/index.html")

# async def root() -> Response:
#   return RedirectResponse(url="static/index.html", status_code=status.HTTP_307_TEMPORARY_REDIRECT)

@app.get("/users/")
async def read_users(user: UserDep, session: SessionDep) -> Dict[str, str]:
  "Dump "
  return {"token": token}

@app.get("/users/{user_id}")
async def read_user(hook_id: int, user: UserDep, session: SessionDep) -> Response:
  return JSONResponse({"hook_id": hook_id})

@app.get("/users/me")
async def read_users_me(user: UserDep, session: SessionDep) -> User:
  return user

@app.get("/hooks/")
async def read_hook (user: UserDep, session: SessionDep) -> Dict[str, str]:
  return {"token": token}

@app.get("/hooks/{hook_id}")
async def read_hook(hook_id: int, user: UserDep, session: SessionDep) -> Response:
  return JSONResponse({"hook_id": hook_id})

@app.post("/hooks")
async def create_hook(hook_id: int, user: UserDep, session: SessionDep) -> Response:  
  pass

@app.delete("/hooks/{hook_id}")
async def delete_hook(hook_id: int, user: UserDep, session: SessionDep) -> Response: 
  pass

@app.patch("/hooks/{hook_id}")
async def modify_hook(hook_id: int, user: UserDep, session: SessionDep) -> Response:
  pass

if __name__ == "__main__":
  uvicorn.run(app, host=settings.host, port=settings.port)
