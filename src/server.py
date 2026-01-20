#! python3

import uvicorn
import sqlmodel
import asyncio

from fastapi import FastAPI, WebSocket, Depends, HTTPException, Query, WebSocketDisconnect
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
engine = sqlmodel.create_engine(settings.sqlurl, connect_args={"check_same_thread": False})
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

websockets : set[WebSocket] = set()

async def broadcast(msg: str):
  async with asyncio.TaskGroup() as tg:
    for w in websockets:
      tg.create_task(w.send_text(msg))

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
  await websocket.accept()
  websockets.add(websocket)
  await broadcast(f"Socket {repr(websocket)} opened; now {len(websockets)} WebSockets.")
  try:
    while True:
      data = await websocket.receive_text()
      await broadcast(f"Message text from {repr(websocket)} was: {data} {repr(settings)}")
  except WebSocketDisconnect:
    websockets.remove(websocket)
    await broadcast(f"Socket {repr(websocket)} disconnected; now {len(websockets)} remaining WebSockets.")
  except Exception as e:
    websockets.remove(websocket)

if __name__ == "__main__":
  uvicorn.run(app, host=settings.host, port=settings.port)
