import logging
import os
from datetime import datetime

import redis.asyncio as redis
# from aioprometheus.pusher import Pusher
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from prometheus_fastapi_instrumentator import Instrumentator

from api import admin, auth, user, websocket

PUSH_GATEWAY_ADDR = os.environ.get("PUSH_GATEWAY_ADDR")

root = os.path.dirname(os.path.abspath(__file__))
app  = FastAPI()
app.add_middleware(
	CORSMiddleware,
	allow_origins = ["*"],
	allow_credentials = True,
	allow_methods = ["*"],
	allow_headers = ["*"],
)
app.include_router(user.router)
app.include_router(websocket.router)
Instrumentator().instrument(app).expose(app)
redis_conn = redis.Redis(host="redis", port=6379, decode_responses=False)


@app.middleware("http")
async def log_transaction_filter(request: Request, call_next):
	start_time = datetime.now()
	method_name = request.method
	qp_map = request.query_params
	pp_map = request.path_params
	with open("request_log.txt", mode="a") as reqfile:
		content = f"method: {method_name}, query param: {qp_map}, path params: {pp_map} received at {datetime.now()}"
		reqfile.write(content)
	response = await call_next(request)
	process_time = datetime.now() - start_time
	response.headers["X-Time-Elapsed"] = str(process_time)
	return response


@app.get("/")
async def get():
    with open(os.path.join(root, "public/index.html")) as fh:
        html = fh.read()
    return HTMLResponse(html)


@app.get("/websocket")
async def get():
    with open(os.path.join(root, "public/ws.html")) as fh:
        html = fh.read()
    return HTMLResponse(html)


@app.get("/health")
async def health_check():
    return "OK"
