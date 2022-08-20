from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from managers import WSManager


class ConnectionManager:
    active_connections: list[WebSocket]
    wsmanager: WSManager

    def __init__(self):
        self.active_connections: list[WebSocket] = []
        self.wsmanager = WSManager()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def handle_socket(self, websocket: WebSocket, msg: str):
        await self.wsmanager.handle_message(msg)

connection = ConnectionManager()
router = APIRouter(
    prefix = '/ws',
    tags = ['ws',]
)

@router.websocket('/')
async def websocket_endpoint(websocket: WebSocket):
    await connection.connect(websocket)
    try:
        while True:
            msg = await websocket.receive_text()
            await connection.handle_socket(websocket, msg)
    except WebSocketDisconnect:
        connection.disconnect(websocket)
