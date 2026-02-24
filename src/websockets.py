#! python3

import asyncio

from fastapi import WebSocket, WebSocketDisconnect

websockets : set[WebSocket] = set()

async def broadcast(msg: str):
  async with asyncio.TaskGroup() as tg:
    for w in websockets:
      tg.create_task(w.send_text(msg))

async def endpoint(websocket: WebSocket):
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
