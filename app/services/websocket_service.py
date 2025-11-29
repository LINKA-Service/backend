from typing import Dict, List
from fastapi import WebSocket


class ConnectionManager:
    def __init__(self):
        # Store active connections by channel_id
        self.active_connections: Dict[int, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, channel_id: int):
        await websocket.accept()
        if channel_id not in self.active_connections:
            self.active_connections[channel_id] = []
        self.active_connections[channel_id].append(websocket)

    def disconnect(self, websocket: WebSocket, channel_id: int):
        if channel_id in self.active_connections:
            self.active_connections[channel_id].remove(websocket)
            if not self.active_connections[channel_id]:
                del self.active_connections[channel_id]

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: dict, channel_id: int):
        if channel_id in self.active_connections:
            for connection in self.active_connections[channel_id]:
                await connection.send_json(message)


manager = ConnectionManager()
