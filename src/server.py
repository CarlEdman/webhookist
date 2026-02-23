#! python3
import uvicorn
import sqlmodel

from fastapi import FastAPI, Depends, HTTPException, Query, Response, status
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, FileResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from typing import Annotated
from sqlmodel import Field, Session, SQLModel
from contextlib import asynccontextmanager
from pydantic import BaseModel

from settings import settings
from templates import templates
from static import static
from security import get_current_active_user, User
import websockets

def get_session():
  with Session(engine) as session:
    yield session

@asynccontextmanager
async def lifespan(app: FastAPI):
  SQLModel.metadata.create_all(engine)
  yield

SessionDep = Annotated[Session, Depends(get_session)]

app = FastAPI(lifespan=lifespan)
engine = sqlmodel.create_engine(settings.sqlurl, connect_args={"check_same_thread": False})
app.mount("/static", static , name="static")


#app.add_middleware(HTTPSRedirectMiddleware)

@app.get("/favicon.ico")
async def favicon() -> Response:
  return FileResponse( "static/favicon.ico")

@app.get("/")
async def root() -> Response:
  return FileResponse("static/index.html")

# async def root() -> Response:
#   return RedirectResponse(url="static/index.html", status_code=status.HTTP_307_TEMPORARY_REDIRECT)

@app.get("/items/{item_id}")
async def read_item(item_id: int) -> Response:
  return JSONResponse({"item_id": item_id})

# @app.get("/items/")
# async def read_items(token: Annotated[str, Depends(security_scheme)]):
#   return {"token": token}

@app.get("/users/me")
async def read_users_me(current_user: Annotated[User, Depends(get_current_active_user)]) -> User:
  return current_user

if __name__ == "__main__":
  uvicorn.run(app, host=settings.host, port=settings.port)
