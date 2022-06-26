from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from .schemas import SocketType, SocketData, MerlinData
from .WSManager import WSManager


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
        socket = SocketData.parse_raw(msg)
        # try:
        #     socket = SocketData.parse_raw(msg)
        # except:  # TODO: specify exception
        #     return

        match socket.type:
            case SocketType.merlin:
                merlin_data = MerlinData(**socket.data)
                # try:
                #     merlin_data = MerlinData(**socket.data)
                # except: # TODO: specify exception
                #     return
                await self.wsmanager.merlin_send(merlin_data)

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
