import asyncio
import json
import logging
import os
from typing import Union

import redis.asyncio as redis
from fastapi import (APIRouter, BackgroundTasks, Depends, WebSocket,
                     WebSocketDisconnect, status)

from lib.event import Event
from manager import ConnectionManager
from utils import *

manager = ConnectionManager()
redis_conn = redis.Redis(host="redis", port=6379, decode_responses=False)
router = APIRouter()


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    q: Union[str, None] = None,
    cookie_or_token: str = Depends(get_cookie_or_token)
):
    try:
        await manager.connect(websocket)
        name = manager.get_channel_name(websocket)
        # await manager.broadcast(f"Newbie {name}")
        while True:
            request = await websocket.receive_text()
            logging.info(f"Received WebSocket message: {request}")
            if not validate_json_request(request):
                await manager.send_message(
                    json.dumps({"echo_request": request, "error": "Invalid request"}),
                    websocket,
                )
                break
            decoded_token = decode_access_token(cookie_or_token)
            if decoded_token is None:
                logging.info(f"Token: {cookie_or_token}")
                await manager.send_message(
                    json.dumps(
                        {
                            "echo_request": request,
                            "error": "Invalid token please reconnect",
                        }
                    ),
                    websocket,
                )

            request = json.loads(request)
            data = json.loads(request["data"])
            args = json.loads(data["args"])
            await process_request(data, args, websocket)
    except WebSocketDisconnect:
        logging.info("WebSocket client disconnected")
        await manager.disconnect(websocket)
    except Exception as e:
        logging.error(f"Error in WebSocket: {e}")
        await manager.disconnect(websocket)


async def process_request(data, args, websocket):
    try:
        event = Event(stream="api", action=args["action"], data=data)
        await event.publish(redis_conn)
        response = await asyncio.wait_for(
            manager.receive_message(websocket), timeout=30.0
        )
        if response is not None:
            await manager.send_message(
                json.dumps({"echo_request": data, "response": response}), websocket
            )
        else:
            await manager.send_message(
                json.dumps({"echo_request": request, "error": "No response"}), websocket
            )
    except asyncio.TimeoutError:
        logging.warning("Timeout while waiting for response!")

