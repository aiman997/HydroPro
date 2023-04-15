import asyncio
import logging
import json
import uuid
from typing import List, Union

import redis.asyncio as redis
from fastapi import WebSocket, WebSocketDisconnect

MAX_CONNECTIONS = 100

logging.basicConfig(level=logging.DEBUG)

class ConnectionManager:
    def __init__(self):
        self.active_connections = {}
        self.redis = redis.Redis(host='redis', port=6379, decode_responses=True)
        self.pubsub = self.redis.pubsub(ignore_subscribe_messages=True)

    async def connect(self, websocket: WebSocket):
        try:
            if len(self.active_connections) >= MAX_CONNECTIONS:
                await websocket.close(code=1000, reason="Too many connections")
            else:
                await websocket.accept()
                channel_name = str(uuid.uuid4())
                # Cache the channel name in Redis for 5 minutes
                await self.redis.set(channel_name, websocket.client.host, ex=300)
                self.active_connections[websocket] = channel_name
        except WebSocketDisconnect:
            del self.active_connections[websocket]

    async def disconnect(self, websocket: WebSocket):
        channel_name = self.active_connections.pop(websocket, None)
        if channel_name is not None:
            await self.redis.delete(channel_name)

    async def send_message(self, message: str, websocket: WebSocket):
        try:
            await websocket.send_text(message)
        except Exception as e:
            logging.error(f"Error sending message: {e}")
            await websocket.close(code=1011, reason="Internal server error")

    async def broadcast(self, message: str):
        for connection, channel_name in self.active_connections.items():
            try:
                await connection.send_text(message)
            except Exception as e:
                logging.error(f"Error broadcasting message: {e}")
                del self.active_connections[connection]
                self.redis.delete(channel_name)

    async def publish_message(self, message: str):
        try:
            await self.pubsub.publish(self.channel, message)
        except Exception as e:
            logging.error(f"Error publishing message: {e}")

    async def receive_message(self, websocket: WebSocket):
        try:
            channel_name = self.active_connections[websocket]
            await self.pubsub.subscribe(channel_name)
            while True:
                message = await self.pubsub.get_message()
                if message and message["type"] == "message":
                    return message["data"]
                else:
                    continue
        except Exception as e:
            logging.error(f"Error receiving message: {e}")
            return None
        finally:
            await self.pubsub.unsubscribe(channel_name)

    def get_channel_name(self, websocket: WebSocket) -> Union[str, None]:
        return self.active_connections.get(websocket)
