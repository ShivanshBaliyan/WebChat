from fastapi import FastAPI, WebSocket, Request, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import uuid
import json
import os

templates = Jinja2Templates(directory="templates")

class ConnectionManager:
    def __init__(self) -> None:
        self.active_connections: dict = {}

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        client_id = str(uuid.uuid4())
        self.active_connections[client_id] = websocket
        await self.send_message(websocket, json.dumps({"isMe": True, "data": "You have joined!", "username": "You"}))
        return client_id

    async def send_message(self, ws: WebSocket, message: str):
        try:
            await ws.send_text(message)
        except Exception as e:
            print(f"Error sending message: {e}")

    def find_connection_id(self, websocket: WebSocket):
        websocket_list = list(self.active_connections.values())
        id_list = list(self.active_connections.keys())
        try:
            pos = websocket_list.index(websocket)
            return id_list[pos]
        except ValueError:
            return None

    async def broadcast(self, websocket: WebSocket, data: str):
        try:
            decoded_data = json.loads(data)
            for connection in self.active_connections.values():
                is_me = connection == websocket
                await connection.send_text(json.dumps({
                    "isMe": is_me, 
                    "data": decoded_data.get('message', ''), 
                    "username": decoded_data.get('username', 'Anonymous')
                }))
        except Exception as e:
            print(f"Error broadcasting message: {e}")

    def disconnect(self, websocket: WebSocket):
        client_id = self.find_connection_id(websocket)
        if client_id and client_id in self.active_connections:
            del self.active_connections[client_id]
        return client_id

app = FastAPI()

# Mount static files if directory exists
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

connection_manager = ConnectionManager()

@app.get("/", response_class=HTMLResponse)
async def get_room(request: Request):
    return templates.TemplateResponse(request, "index.html")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    try:
        await connection_manager.connect(websocket)
        while True:
            data = await websocket.receive_text()
            await connection_manager.broadcast(websocket, data)
    except WebSocketDisconnect:
        connection_manager.disconnect(websocket)
