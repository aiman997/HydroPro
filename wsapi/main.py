import json
import asyncio
import logging
import bcrypt
import datetime
from fastapi import FastAPI, HTTPException, Depends, status, WebSocket, WebSocketDisconnect
from fastapi.security import HTTPBasic, HTTPBasicCredentials, OAuth2PasswordBearer
from fastapi.responses import HTMLResponse
from typing import Optional
import redis.asyncio as redis
from lib.event import Event
from manger import ConnectionManager

app = FastAPI()
redis = redis.Redis(host='redis', port=6379, decode_responses=True)
logging = logging.getLogger("gunicorn.error")
pubsub = redis.pubsub()
manager = ConnectionManager()

html = """
<html<html>
	<head>
		<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css" integrity="sha384-Gn5384xqQ1aoWXA+058RXPxPg6fy4IWvTNh0E263XmFcJlSAwiGgFAW/dAiS6JXm" crossorigin="anonymous">
		<style>
		.container {
			display: flex;
			flex-direction: column;
			align-items: center;
			margin-top: 50px;
		}

		textarea {
			width: 50%;
			height: 150px;
			padding: 10px;
			font-size: 16px;
			margin-bottom: 20px;
		}
		</style>
		<script>
		const random = (length = 8) => {
			return Math.random().toString(16).substr(2, length);
		};

		function formatJson(jsonString) {
			return JSON.stringify(JSON.parse(jsonString), null, 2);
		}

		function sendRequest() {
			var socket = new WebSocket("ws://localhost:8000/ws");

			socket.onopen = function (event) {
			var request = {
				type: "request",
				auth: random(8),
				data: document.getElementById("requestData").value
			};
			socket.send(JSON.stringify(request));
			};

			socket.onmessage = function (event) {
			var response = formatJson(event.data);
			document.getElementById("responseData").value = response;
			};

			socket.onerror = function (error) {
			console.error("Error: " + error.message);
			};
		}
		</script>
	</head>
	<body>
		<div class="container">
		<h1>WebSocket JSON Request/Response</h1>
		<p>Enter your request data in the input field below:</p>
		<textarea id="requestData" rows="4" cols="50"></textarea>
		<button class="btn btn-primary" onclick="sendRequest()">Send Request</button>
		<p>Response:</p>
		<textarea id="responseData" rows="4" cols="50" readonly></textarea>
		</div>
	</body>
</html>

"""

@app.get("/")
async def get():
	return HTMLResponse(html)

@app.get("/health")
async def get():
	return "OK"

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
	await manager.connect(websocket)
	try:
		request     = await websocket.receive_text()
		is_json_req = validate_json_request(request)
		request     = json.loads(request)
		if is_json_req:
			data = json.loads(request['data'])
			await pubsub.subscribe(request['auth'])
			data['args']['auth'] = request['auth']
			await send_event('api', data['action'], data['args'])
			while True:
				res = await pubsub.get_message(ignore_subscribe_messages=True, timeout=30)
				if res is not None:
					logging.info(res)
					await manager.send_message(json.dumps({"echo_request": request['data'], "response": res}), websocket)
					break
		else:
			await manager.send_message(json.dumps({"echo_request": request, "error": "Invalid json request"}), websocket)
	except WebSocketDisconnect:
		logging.info("Disconecting ws client")
		manager.disconnect(websocket)

# Utils

def validate_json_request(json_request):
	try:
		request = json.loads(json_request)
		data    = json.loads(request['data'])
		if "type" in request and "data" in request:
			return True
		else:
			return False
	except json.JSONDecodeError as e:
		logging.error(f"Invalid request with error: {e}")
		return False

async def send_event(stream, action, data={}):
	try:
		event = Event(stream=stream, action=action, data=data)
		await event.publish(redis)
		logging.info("success")
	except Exception as e:
		logging.error(f"failied with error: {e}")
