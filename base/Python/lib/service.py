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

    def __init__(self, name: str, streams: list, actions: list, redis_conn, metrics_provider):
        self.name = name
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
            try:
                res = await func(self, dict(args))
                await self.redis.publish(args["auth"], str(res))
                logging.info(f"published {res} on " + args["auth"])
            except Exception as e:
                logging.error(f"Error in RPC function: {e}")
        return wrap_func

    async def send_event(self, action: str, data: dict = None):
        if data is None:
            data = {}
            try:
                event = Event(stream=self.name, action=action, data=data)
                await event.publish(self.redis)
                self.counter.inc({"type": f"{action} event"})
            except Exception as e:
                logging.error(f"Error sending event: {e}")

    async def create_consumer_group(self):
        for key in self.streams:
            try:
                existing_groups = await self.redis.xinfo_groups(key)
                if self.name not in [group['name'] for group in existing_groups]:
                    res = await self.redis.xgroup_create(key, self.name, id="$", mkstream=False)
            except Exception as e:
                if "no such key" in str(e):
                    res = await self.redis.xgroup_create(key, self.name, id="$", mkstream=True)
                elif "BUSYGROUP Consumer Group name already exists" in str(e):
                    next
                else:
                    logging.error(f"Exception while xgroup {key}: {e}")


    async def process_and_ack_event(self, e):
        if e.action in self.actions:
            try:
                await self.process_event(e)
                logging.info(
                    f"{datetime.now()} - XACK Stream: {e.stream} - {e.event_id}: {e.action} {e.data}"
                )
                await self.redis.xack(e.stream, self.name, e.event_id)
                self.counter.inc({"type": e.stream + e.action})
                await self.pusher.replace(REGISTRY)
            except Exception as ex:
                logging.error(f"Error processing and acknowledging event: {ex}")

    async def listen(self):
        await self.create_consumer_group()
        self.generate_worker_id()
        await self.claim_and_handle_pending_events()
        await self.clear_idle_workers()

        while True:
            try:
                streams = {key: ">" for key in self.streams}
                event = await self.redis.xreadgroup(self.name, self.worker_id, streams, 1, 0)
                logging.info(f"got from xread {event}")
                e = Event(event=event)
                await self.process_and_ack_event(e)
            except Exception as ex:
                logging.error(f"While processing event: {ex}")

    async def claim_and_handle_pending_events(self):
        for key in self.streams:
            try:
                pending_events = await self.redis.xpending_range(key, self.name, min="-", max="+", count=1000)
                if pending_events:
                    event_ids = [event["message_id"] for event in pending_events]
                    await self.redis.xclaim(key, self.name, self.worker_id, self.pending_event_timeout, event_ids)
                    streams = {key: "0" for key in self.streams}
                    pending_events = await self.redis.xreadgroup(self.name, self.worker_id, streams)
                    for stream in pending_events:
                        for event in stream[1]:
                            e = Event(event=[[stream[0], [event]]])
                            await self.process_and_ack_event(e)
            except Exception as ex:
                logging.error(f"Error claiming and handling pending events: {ex}")

    async def clear_idle_workers(self):
        for key in self.streams:
            try:
                existing_workers = await self.redis.xinfo_consumers(key, self.name)
                for worker in existing_workers:
                    if worker["idle"] > self.worker_timeout:
                        await self.redis.xgroup_delconsumer(key, self.name, worker["name"])
                        self.workergauge.dec({"type": self.name})
            except Exception as ex:
                logging.error(f"Error clearing idle workers: {ex}")

    async def process_event(self, e):
        if e.action in self.rpcs:
            try:
                method = getattr(self, e.action)
                result = await method(e.data)
                if result and e.data["auth"]:
                    await self.redis.publish(e.data["auth"], str(result))
                    return result
            except AttributeError:
                logging.error(f"RPC method '{e.action}' not implemented")
            except Exception as ex:
                logging.error(f"Error in RPC method '{e.action}': {ex}")
        else:
            try:
                await self.handle_event(e.data)
            except Exception as ex:
                logging.error(f"Error while handling event: {ex}")

    async def generate_hash(self, data):
        try:
            hash_object = hashlib.sha256(str(data).encode())
            unique_hash = hash_object.hexdigest()
            await self.redis.set(unique_hash, str(data), ex=3600)
            return unique_hash
        except Exception as e:
            logging.error(f"Error generating hash: {e}")

    async def subscribe_to_channel(self, channel_name):
        try:
            await self.pubsub.subscribe(channel_name)
            message = await self.pubsub.get_message()
            while message is None:
                message = await self.pubsub.get_message()
                await self.expire_hash(channel_name)
                return message.get('data', None)
        except Exception as e:
            logging.error(f"Error subscribing to channel: {e}")

    async def check_hash_validity(self, hash_value):
        try:
            exists = await self.redis.exists(hash_value)
            if exists:
                data = await self.redis.get(hash_value)
                return data.decode()
            return await self.subscribe_to_channel(hash_value)
        except Exception as e:
            logging.error(f"Error checking hash validity: {e}")

    async def expire_hash(self, hash_value):
        try:
            await self.redis.delete(hash_value)
        except Exception as e:
            logging.error(f"Error expiring hash: {e}")
