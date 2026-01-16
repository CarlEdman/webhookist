import uvicorn
import sqlmodel

from fastapi import FastAPI, WebSocket, Depends, HTTPException, Query
from fastapi.responses import HTMLResponse
from pydantic_settings import BaseSettings
from typing import Annotated
from sqlmodel import Field, Session, SQLModel
from contextlib import asynccontextmanager

from settings import settings

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

@app.get("/")
async def root():
  return HTMLResponse("""
<!DOCTYPE html>
<html>
  <head>
    <title>Chat</title>
  </head>
  <body>
    <h1>WebSocket Chat</h1>
    <form action="" onsubmit="sendMessage(event)">
      <input type="text" id="messageText" autocomplete="off"/>
      <button>Send</button>
    </form>
    <ul id='messages'>
    </ul>
    <script>
      var ws = new WebSocket("ws://" + document.location.host + "/ws");
      ws.onmessage = function(event) {
        var messages = document.getElementById('messages')
        var message = document.createElement('li')
        var content = document.createTextNode(event.data)
        message.appendChild(content)
        messages.appendChild(message)
      };
      function sendMessage(event) {
        var input = document.getElementById("messageText")
        ws.send(input.value)
        input.value = ''
        event.preventDefault()
      }
    </script>
  </body>
</html>
""")

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

