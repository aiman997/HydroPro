import os
from datetime import date, datetime
from typing import List
from uuid import UUID, uuid1
import json

import logging
import asyncio
import bcrypt
import redis.asyncio as redis
# from aioprometheus.pusher import Pusher
from fastapi import APIRouter, BackgroundTasks, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from lib.event import Event

# PUSH_GATEWAY_ADDR = os.environ.get("PUSH_GATEWAY_ADDR")
# pusher = Pusher("metric", PUSH_GATEWAY_ADDR, grouping_key={"instance": "api"})

redis_conn = redis.Redis(host="redis", port=6379, decode_responses=False)
router = APIRouter()

@router.post("/auth")
async def authenticate_user(email: str, password: str):
    hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    data = {'email': email, 'password': hashed_password}
    event = Event(stream='api', action='authuser', data=data)
    data['auth'] = await event.generate_hash(redis_conn)
    await event.publish(redis_conn)
    res = await asyncio.wait_for(event.receive_message(data['auth'], redis_conn), timeout=30.0)
    logging.info(f"{res}")
    if not res:
        logging.info(f"{res}")
        raise RuntimeError("Something bad happened while authenticating")
    token = create_access_token(data['email'], expire_delta)
    return {"access_token": token}
