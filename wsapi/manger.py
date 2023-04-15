from typing import List
from fastapi import WebSocket, WebSocketDisconnect

MAX_CONNECTIONS = 100

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        try:
            if len(self.active_connections) >= MAX_CONNECTIONS:
                await websocket.close(code=1000, reason="Too many connections")
            else:
                await websocket.accept()
                self.active_connections.append(websocket)
        except WebSocketDisconnect:
            self.active_connections.remove(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_message(self, message: str, websocket: WebSocket):
        try:
            await websocket.send_text(message)
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            await websocket.close(code=1011, reason="Internal server error")

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.error(f"Error broadcasting message: {e}")
                self.active_connections.remove(connection)
