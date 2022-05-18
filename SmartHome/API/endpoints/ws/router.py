from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from .schemas import SocketType, SocketData, MerlinData, MerlinRaw
from .WSManager import WSManager


class ConnectionManager:
    active_connections: list[WebSocket]
    wsmanager: WSManager

    def __init__(self):
        self.active_connections: list[WebSocket] = []
        self.wsmanager = WSManager()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()

    def disconnect(self, websocket: WebSocket):
        pass

    async def handle_socket(self, websocket: WebSocket, msg: str):
        try: socket = SocketData.parse_raw(msg)
        except: return
        match socket.type:
            case SocketType.merlin:
                try: merlin_data = MerlinData(**socket.data)
                except: return
                self.wsmanager.merlin_send(merlin_data)
            case SocketType.merlin_raw:
                try: merlin_raw_data = MerlinRaw(**socket.data)
                except: return
                self.wsmanager.merlin_send_raw(merlin_raw_data)
        # await websocket.send_text(message)

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
