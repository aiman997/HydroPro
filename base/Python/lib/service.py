import asyncio
import hashlib
import logging
import uuid
from datetime import datetime
from functools import wraps

import redis.asyncio as redis
from aioprometheus import REGISTRY, Counter, Gauge
from aioprometheus.pusher import Pusher
from lib.event import Event
from redis.exceptions import ResponseError

logging.basicConfig(level=logging.INFO)

class Service:
    pending_event_timeout = 30000
    worker_timeout = 30000

    def __init__(
        self,
        name: str,
        stream: str,
        streams: list,
        actions: list,
        redis_conn,
        metrics_provider,
    ):
        self.name = name
        self.stream = stream
        self.streams = streams
        self.actions = actions
        self.redis = redis_conn
        self.pusher = metrics_provider
        self.rpcs = []
        self.pubsub = self.redis.pubsub(ignore_subscribe_messages=True)
        self.counter = Counter(self.name + "_events", "Events count")
        self.workergauge = Gauge("workers", "Number of workers spawned")
        self.workergauge.set({"type": self.name}, 0)

    def generate_worker_id(self):
        self.workergauge.inc({"type": self.name})
        self.worker_id = f"{self.name}-{uuid.uuid4()}"
        return self.worker_id

    @staticmethod
    def rpc(func):
        @wraps(func)
        async def wrap_func(self, args):
            res = await func(self, dict(args))
            await self.redis.publish(args["auth"], str(res))
            logging.info(f"published {res} on " + args["auth"])
        return wrap_func

    async def send_event(self, action: str, data: dict = None):
        if data is None:
            data = {}
        event = Event(stream=self.stream, action=action, data=data)
        await event.publish(self.redis)
        self.counter.inc({"type": f"{action} event"})

    async def create_consumer_group(self):
        for key in self.streams:
            try:
                res = await self.redis.xinfo_stream(key)
                mkstream = not bool(res)
                await self.redis.xgroup_create(key, self.name, id="$", mkstream=mkstream)
            except ResponseError:
                pass

    async def process_and_ack_event(self, e):
        if e.action in self.actions:
            await self.process_event(e)
            logging.info(
                f"{datetime.now()} - XACK Stream: {e.stream} - {e.event_id}: {e.action} {e.data}"
            )
            await self.redis.xack(e.stream, self.name, e.event_id)
            self.counter.inc({"type": e.stream + e.action})
            await self.pusher.replace(REGISTRY)

    async def listen(self):
        try:
            await self.create_consumer_group(key)
            self.generate_worker_id()
            await self.claim_and_handle_pending_events()
            await self.clear_idle_workers()
        except Exception as e:
            logging.error(f"Error creating consumer group: {e}")
            return

        while True:
            try:
                streams = {key: ">" for key in self.streams}
                event = await self.redis.xreadgroup(self.name, self.worker_id, streams, 1, 0)
                e = Event(event=event)
                await self.process_and_ack_event(e)
            except Exception as ex:
                logging.error(f"While processing event: {ex}")

    async def claim_and_handle_pending_events(self):
        for k in self.streams:
            pending_events = await self.redis.xpending_range(k, self.name, min="-", max="+", count=1000)
            if pending_events:
                event_ids = [event["message_id"] for event in pending_events]
                await self.redis.xclaim(k, self.name, self.worker_id, self.pending_event_timeout, event_ids)
                streams = {key: "0" for key in self.streams}
                pending_events = await self.redis.xreadgroup(self.name, self.worker_id, streams)
                for stream in pending_events:
                    for event in stream[1]:
                        e = Event(event=[[stream[0], [event]]])
                        await self.process_and_ack_event(e)

    async def clear_idle_workers(self):
        for k in self.streams:
            existing_workers = await self.redis.xinfo_consumers(k, self.name)
            for worker in existing_workers:
                if worker["idle"] > self.worker_timeout:
                    await self.redis.xgroup_delconsumer(k, self.name, worker["name"])
                    self.workergauge.dec({"type": self.name})

    async def process_event(self, e):
        if e.action in self.rpcs:
            try:
                method = getattr(self, e.action)
                result = await method(e.data)
                if result and e.data["auth"]:
                    await self.redis.publish(e.data["auth"], str(result))
                return result
            except AttributeError:
                raise NotImplementedError(f"Class `{self.__class__.__name__}` does not implement `{e.action}`")
        else:
            try:
                await self.handle_event(e.data)
            except Exception as ex:
                logging.error(f"While handle event: {ex}")

    async def generate_hash(self, data):
        hash_object = hashlib.sha256(str(data).encode())
        unique_hash = hash_object.hexdigest()
        await self.redis.set(unique_hash, str(data), ex=3600)
        return unique_hash

    async def subscribe_to_channel(self, channel_name):
        await self.pubsub.subscribe(channel_name)
        message = await self.pubsub.get_message()
        while message is None:
            message = await self.pubsub.get_message()
        await self.expire_hash(channel_name)
        return message.get('data', None)

    async def check_hash_validity(self, hash_value):
        exists = await self.redis.exists(hash_value)
        if exists:
            data = await self.redis.get(hash_value)
            return data.decode()
        return await self.subscribe_to_channel(hash_value)

    async def expire_hash(self, hash_value):
        await self.redis.delete(hash_value)
