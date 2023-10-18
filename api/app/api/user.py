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

redis_conn = redis.Redis(host="redis", port=6379, decode_responses=False)
# pusher = Pusher("metric", PUSH_GATEWAY_ADDR, grouping_key={"instance": "api"})
router = APIRouter()


class Signup(BaseModel):
    email: str
    password: str
    firstname: str
    lastname: str
    birthday: datetime
    roles: str = "user"


class User(BaseModel):
    id: UUID
    email: str
    password: str


@router.post("/users/newbie")
async def create_user(
    email: str, password: str, first_name: str, last_name: str, roles: str
):
    hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    data = {
        "email": email,
        "password": hashed_password,
        "first_name": first_name,
        "last_name": last_name,
        "roles": roles,
    }
    event = Event(stream="api", action="newuser", data=data)
    data["auth"] = await event.generate_hash(redis_conn)
    try:
        await event.publish(redis_conn)
        res = await asyncio.wait_for(event.receive_message(data["auth"], redis_conn), timeout=30.0)
        logging.info(f"{res}")
        if not res:
            logging.info(f"{res}")
            raise RuntimeError("Something bad happened while authenticating")
        token = create_access_token(data["email"], timedelta(hours=6))
        return {"access_token": token}
    except Exception as e:
        logging.warn(f"Exception while creating new user: {e}")
        return {"error": 1, "message": str(e)}
