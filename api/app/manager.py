import asyncio
import logging
import uuid
from datetime import datetime, timedelta
from typing import List, Union

from lib.event import Event
import redis.asyncio as redis
from fastapi import WebSocket, WebSocketDisconnect
from utils import *

MAX_CONNECTIONS = 100

class ConnectionManager:
    def __init__(self, redis_host: str = 'redis', redis_port: int = 6379):
        self.active_connections = {}
        self.expire_delta = timedelta(hours=6)
        self.redis = redis.Redis(
            host=redis_host, port=redis_port, decode_responses=True)
        self.pubsub = self.redis.pubsub(ignore_subscribe_messages=True)

    async def is_connected(self, websocket: WebSocket) -> bool:
        try:
            channel_name = self.active_connections.get(websocket)
            if channel_name:
                is_connected = await self.redis.get(channel_name)
                return bool(is_connected)
            return False
        except redis.exceptions.RedisError as e:
            logging.error(f"While checking if connected: {e}")
            return False

    async def connect(self, websocket: WebSocket):
        try:
            active = await self.is_connected(websocket)
            channel_name = self.active_connections.get(websocket)
            if active:
                logging.warning(f"This should never happen!!!! while connected tried to connect")
                await websocket.close(code=1000, reason="Active connection already exists")
            elif channel_name:
                await self.redis.set(channel_name, websocket.client.host, ex=self.expire_delta.seconds)
                self.active_connections[websocket] = channel_name
            elif len(self.active_connections) >= MAX_CONNECTIONS:
                await websocket.close(code=1000, reason="Too many connections")
            else:
                channel_name = create_access_token({'name' : str(uuid.uuid4())}, self.expire_delta)
                await self.redis.set(channel_name, websocket.client.host, ex=self.expire_delta.seconds)
                await websocket.accept()
                self.active_connections[websocket] = channel_name
        except WebSocketDisconnect:
            await self.disconnect(websocket)
        except Exception as e:
            logging.error(f"While connecting: {e}")

    async def disconnect(self, websocket: WebSocket):
        channel_name = self.active_connections.pop(websocket, None)
        await websocket.close()
        if channel_name:
            await self.redis.delete(channel_name)

    async def send_message(self, message: str, websocket: WebSocket):
        try:
            active = await self.is_connected(websocket)
            if active:
                await websocket.send_text(message)
        except Exception as e:
            logging.error(f"Error sending message: {e}")
            await websocket.close(code=1011, reason="Internal server error")

    async def broadcast(self, message: str):
        for websocket, channel_name in list(self.active_connections.items()):
            active = await self.is_connected(websocket)
            if active:
                try:
                    await websocket.send_text(message)
                except Exception as e:
                    logging.error(f"Error broadcasting message: {e}")
                    del self.active_connections[websocket]
                    await self.redis.delete(channel_name)
            else:
                await websocket.close(code=1011, reason="Internal server error")

    async def receive_message(self, websocket: WebSocket, time_seconds: int = '60'):
        try:
            channel_name = self.active_connections.get(websocket)
            if not channel_name:
                return None
            await self.redis.set(channel_name, websocket.client.host, ex=self.expire_delta.seconds)
            data = await asyncio.wait_for(event.receive_message(channel_name, self.redis), timeout=time_seconds)
            logging.info(data)
            return data
        except Exception as e:
            logging.error(f"Error receiving message: {e}")
            return None

    def get_channel_name(self, websocket: WebSocket) -> Union[str, None]:
        return self.active_connections.get(websocket)
