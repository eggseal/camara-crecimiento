import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, Query
from fastapi.responses import StreamingResponse
from fastapi.templating import Jinja2Templates
from typing import Dict

app = FastAPI()
templates = Jinja2Templates(directory="templates")

latest_frames: Dict[int, bytes] = {}
locks: Dict[int, asyncio.Lock] = {}


def get_lock(cam_id: int):
    if cam_id not in locks:
        locks[cam_id] = asyncio.Lock()
    return locks[cam_id]


@app.websocket("/ws/cam/{cam_id}")
async def websocket_endpoint(ws: WebSocket, cam_id: int):
    await ws.accept()
    lock = get_lock(cam_id)

    try:
        while True:
            data = await ws.receive_bytes()
            async with lock:
                latest_frames[cam_id] = data
    except WebSocketDisconnect:
        print(f"Camera {cam_id} disconnected")


@app.get("/stream/{cam_id}")
async def stream(cam_id: int):
    async def frame_generator():
        lock = get_lock(cam_id)

        while True:
            async with lock:
                frame = latest_frames.get(cam_id)

            if frame:
                yield (
                    b"--frame\r\n"
                    b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n"
                )

            await asyncio.sleep(0.1)

    return StreamingResponse(
        frame_generator(),
        media_type="multipart/x-mixed-replace; boundary=frame",
    )


@app.get("/")
async def index(request: Request, cam_id: int = Query(0)):
    print(f"Serving camera {cam_id}")
    return templates.TemplateResponse("index.html", {"request": request, "cam_id": cam_id})