import hashlib
import json
import logging

logging.basicConfig(level=logging.INFO)

class Event:
    def __init__(self, stream: str = "", action: str = "", data: dict = {}, event=None):
        self.stream = stream
        self.action = action
        self.data = data
        self.event_id = None
        if event:
            self.parse_event(event)

    def parse_event(self, event):
        self.stream = event[0][0].decode('utf-8')
        self.event_id = event[0][1][0][0].decode('utf-8')
        raw_data = event[0][1][0][1]
        self.action = raw_data.pop(b'action').decode('utf-8')
        self.data = {k.decode('utf-8'): json.loads(v.decode('utf-8')) for k, v in raw_data.items()}

    async def publish(self, redis_conn):
        logging.info(f"Adding to stream: {self.stream} data: {self.action} {self.data}")
        body = {"action": self.action}
        body.update({k: json.dumps(v, default=str) for k, v in self.data.items()})
        try:
            await redis_conn.xadd(self.stream, body, maxlen=1000)
        except Exception as e:
            logging.error(f"While publishing on {self.stream}: {e}")

    async def generate_hash(self, redis_conn):
        hash_object = hashlib.sha256(json.dumps(self.data, default=str).encode())
        unique_hash = hash_object.hexdigest()
        try:
            await redis_conn.set(unique_hash, json.dumps(self.data, default=str), ex=3600)
            return unique_hash
        except Exception as e:
            logging.error(f"While publishing on {self.stream}: {e}")
            return None

    async def receive_message(self, channel_name, redis_conn):
        pubsub = redis_conn.pubsub(ignore_subscribe_messages=True)
        await pubsub.subscribe(channel_name)
        msg = Event()
        try:
            while True:
                message = await pubsub.get_message()
                if message and message["type"] == "message":
                    msg.data = message["data"]
                    await redis_conn.delete(channel_name)
                    return msg
                else:
                    continue
        except Exception as e:
            logging.error(f"Error receiving message: {e}")
            return msg
        finally:
            await pubsub.unsubscribe(channel_name)
