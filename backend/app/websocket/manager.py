from collections import defaultdict
from fastapi import WebSocket

class ConnectionManager:
    def __init__(self) -> None:
        self.connections: dict[str, set[WebSocket]] = defaultdict(set)

    async def connect(self, websocket: WebSocket, user_id: str) -> None:
        await websocket.accept()
        self.connections[user_id].add(websocket)

    def disconnect(self, websocket: WebSocket, user_id: str) -> None:
        self.connections[user_id].discard(websocket)
        if not self.connections[user_id]:
            del self.connections[user_id]

    async def send_to_user(self, user_id: str, event: dict) -> None:
        if user_id == "broadcast":
            await self.broadcast(event)
            return
        for connection in list(self.connections.get(user_id, ())):
            await connection.send_json(event)

    async def broadcast(self, event: dict) -> None:
        for user_id in list(self.connections.keys()):
            for connection in list(self.connections[user_id]):
                try:
                    await connection.send_json(event)
                except Exception:
                    pass

manager = ConnectionManager()
