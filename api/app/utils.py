import asyncio
import json
import logging
import os
import jwt
from lib.event import Event
import redis.asyncio as redis
from typing import Optional, Union
from datetime import datetime, timedelta
from fastapi import Cookie, Query, WebSocket, WebSocketException, status

logging = logging.getLogger("gunicorn.error")
SECRET_KEY = "mysecretkey"


def validate_json_request(json_request):
    try:
        request = json.loads(json_request)
        logging.info(f"{json_request}")
        if "type" in request and "data" in request:
            data = json.loads(request["data"])
            logging.info(f"{data}")
            if "action" in data and "args" in data:
                return True
            else:
                return False
        else:
            return False
    except Exception as e:
        logging.error(f"Invalid request with error: {e}")
        return False


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")
    return encoded_jwt


def decode_access_token(token: str):
    try:
        decoded_token = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return str(decoded_token)
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


async def get_cookie_or_token(
    websocket: WebSocket,
    session: Union[str, None] = Cookie(default=None),
    token: Union[str, None] = Query(default=None),
):
    if session is None and token is None:
        logging.info("No session No token")
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)
    return session or token


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
