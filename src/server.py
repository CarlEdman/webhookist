#! python3

import uvicorn
import sqlmodel

from fastapi import FastAPI, WebSocket, Depends, HTTPException, Query
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from typing import Annotated
from sqlmodel import Field, Session, SQLModel
from contextlib import asynccontextmanager

from settings import settings
from templates import templates
from static import static

def get_session():
    with Session(engine) as session:
        yield session

@asynccontextmanager
async def lifespan(app: FastAPI):
  SQLModel.metadata.create_all(engine)
  yield

SessionDep = Annotated[Session, Depends(get_session)]

app = FastAPI(lifespan=lifespan)
engine = sqlmodel.create_engine(settings.fpt_sqlurl, connect_args={"check_same_thread": False})

app.mount("/static", static , name="static")

@app.get("/favicon.ico")
async def favicon() -> FileResponse:
  return FileResponse( "static/favicon.ico")

@app.get("/")
async def root() -> FileResponse:
  return FileResponse("static/index.html")

# async def root() -> RedirectResponse:
#   return RedirectResponse(url="static/index.html", status_code=307)

@app.get("/items/{item_id}")
async def read_item(item_id: int):
  return {"item_id": item_id}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
  await websocket.accept()
  while True:
    data = await websocket.receive_text()
    await websocket.send_text(f"Message text was: {data} {repr(settings)}")

if __name__ == "__main__":
  uvicorn.run(app, host=settings.fpt_host, port=settings.fpt_port)
