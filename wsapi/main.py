import asyncio
import json
import logging
import os
from datetime import datetime, timedelta, timezone
from typing import Optional, Union

import bcrypt
import jwt
import redis.asyncio as redis
from fastapi import (Cookie, Depends, FastAPI, Query, WebSocket,
                     WebSocketDisconnect, WebSocketException, status)
from fastapi.middleware import Middleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from lib.event import Event
from manger import ConnectionManager

SECRET_KEY = "mysecretkey"

logging = logging.getLogger("gunicorn.error")
root = os.path.dirname(os.path.abspath(__file__))

origins = ["*"]

middleware = [
    Middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    ),
]

app = FastAPI(middleware=middleware)

manager = ConnectionManager()
redis = redis.Redis(host='redis', port=6379, decode_responses=True)
pubsub = redis.pubsub()

# Utils


def validate_json_request(json_request):
    try:
        request = json.loads(json_request)
        data = json.loads(request['data'])
        if "type" in request and "data" in request:
            return True
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
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)
    return session or token


async def send_event(stream, action, data={}):
    try:
        event = Event(stream=stream, action=action, data=data)
        await event.publish(redis)
        logging.info("success")
    except Exception as e:
        logging.error(f"failied with error: {e}")

# Routes


@app.get("/")
async def get():
    with open(os.path.join(root, 'index.html')) as fh:
        html = fh.read()
    return HTMLResponse(html)


@app.get("/health")
async def get():
    return "OK"


@app.post("/auth")
async def auth():
    token = create_access_token(dict())
    return token


@app.post("/auth")
async def authenticate_user(email: str, password: str):
    await send_event('api', 'authuser', json.loads({'email': email, 'password': password}))
    if not validate_credentials(email, password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    # Generate access token
    token = create_access_token({"email": email})
    return {"access_token": token}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, q: Union[int, None] = None, cookie_or_token: str = Depends(get_cookie_or_token)):
    try:
        await manager.connect(websocket)
        while True:
            try:
                request = await websocket.receive_text()
                if not validate_json_request(request):
                    await manager.send_message(json.dumps({"echo_request": request, "error": "Invalid json request"}), websocket)
                    continue
                request = json.loads(request)
                data = json.loads(request['data'])
                args = data['args']
                decoded_token = decode_access_token(cookie_or_token)
                ch = manager.get_channel_name(websocket)
                if ch:
                    args['auth'] = ch
                if decoded_token is None:
                    logging.info('Invalid token')
                    # raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)
                await send_event('api', data['action'], args)
                try:
                    res = await asyncio.wait_for(manager.receive_message(websocket), timeout=30.0)
                    if res is not None:
                        await manager.send_message(json.dumps({"echo_request": data, "response": res}), websocket)
                    else:
                        await manager.send_message(json.dumps({"echo_request": request, "error": "No response"}), websocket)
                except TimeoutError:
                    logging.warning('Timeout while waiting for response!')
            except WebSocketDisconnect:
                logging.info('Client disconnected')
                break
            except Exception as e:
                logging.error(f"Error while processing the message: {e}")
    except Exception as e:
        logging.error(f"Disconecting ws client due to error: {e}")
    finally:
        await manager.disconnect(websocket)
