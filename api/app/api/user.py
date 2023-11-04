import os
from datetime import date, datetime
from typing import List
from uuid import UUID, uuid1
import json

import logging
import asyncio
import bcrypt
import redis.asyncio as redis
from fastapi import APIRouter, BackgroundTasks, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from lib.event import Event
from utils import *


redis_conn = redis.Redis(host="redis", port=6379, decode_responses=False)
router = APIRouter()


class Signup(BaseModel):
    username: str
    email: str
    password: str
    firstname: str
    lastname: str
    birthday: datetime
    roles: str = "user"


class User(BaseModel):
    email: str
    password: str


@router.post("/users/newbie")
async def create_user(
    username: str, email: str, password: str, first_name: str, last_name: str, roles: str
):
    hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    data = {
        "username": email,
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
        res = res.data
        logging.warn(f"From user service {res}")
        if not res:
            logging.warn(f"Got nothing from users service")
            raise RuntimeError("Something bad happened while creating new user")
        token = create_access_token({ "email": data["email"] }, timedelta(hours=6))
        return {"access_token": token, "user": res}
    except Exception as e:
        logging.warn(f"Exception while creating new user: {e}")
        return {"error": 1, "message": str(e)}
