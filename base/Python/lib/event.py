import json
import time
import logging
import asyncio

logging.basicConfig(level=logging.INFO)

class Event():
    def __init__(self, stream="", action="", data={}, producer="", event=None):
        self.stream = stream
        self.action = action
        self.data = data
        self.event_id = None
        if event:
            self.parse_event(event)

    def parse_event(self, event):
        self.stream = event[0][0].decode('utf-8')
        self.event_id = event[0][1][0][0].decode('utf-8')
        self.data = event[0][1][0][1]
        self.action = self.data.pop(b'action').decode('utf-8')
        params = {}
        for k, v in self.data.items():
            params[k.decode('utf-8')] = json.loads(v.decode('utf-8'))
            self.data = params

    async def publish(self, redis_conn):
        body = {
            "action": self.action
        }
        for k, v in self.data.items():
            body[k] = json.dumps(v, default=str)
        await redis_conn.xadd(self.stream, body, maxlen=1000)
