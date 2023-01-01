from redis.exceptions import ResponseError
from datetime import datetime
from lib.event import Event
import json
import uuid
import logging
import asyncio
import async_timeout
import redis.asyncio as redis
import os
from aioprometheus import REGISTRY, Counter, Gauge
from aioprometheus.pusher import Pusher
from aioprometheus import Counter

class Service:
  pending_event_timeout = 30000
  worker_timeout        = 30000

  def __init__(self, name, stream, streams, actions, redis_conn, metrics_provider):
    self.name = name
    self.stream = stream
    self.redis = redis_conn
    self.events = dict()
    self.pusher = metrics_provider
    self.counter = Counter(self.name, "Events count")
    self.streams = streams
    self.actions = actions

  async def send_event(self, action, data={}):
    event = Event(stream=self.stream, action=action, data=data)
    await event.publish(self.redis)
    self.counter.inc({'type': f"{action} event"})

  async def listen(self):
    service_events = self.streams
    service_actions = self.actions
    await self.create_consumer_group()
    streams = {key: ">" for key in service_events}
    self.generate_worker_id()
    await self.claim_and_handle_pending_events()
    await self.clear_idle_workers()
    while True:
      event = await self.redis.xreadgroup(self.name, self.worker_id, streams, 1, 0)
      e = Event(event=event)
      if e.action in service_actions:
        result = await self.handel_event(e.data)
        logging.debug(f"{datetime.now()} - XACK Stream: {e.stream} - {e.event_id}: {e.action} {e.data}")
        await self.redis.xack(e.stream, self.name, e.event_id)
        self.counter.inc({'type': e.stream + e.action})
        resp = await self.pusher.replace(REGISTRY)

  async def create_consumer_group(self):
    for key in self.streams:
      try:
        await self.redis.xinfo_stream(key)
        mkstream = False
      except ResponseError:
        mkstream = True
      try:
        await self.redis.xgroup_create(key, self.name, id=u'$', mkstream=mkstream)
      except ResponseError:
        pass

  def generate_worker_id(self):
    self.worker_id = self.name + f"-{uuid.uuid4()}"
    return self.worker_id

  async def claim_and_handle_pending_events(self):
    for k in self.streams:
      pending_events = await self.redis.xpending_range(k, self.name, min="-", max="+", count=1000)
      if len(pending_events) > 0:
        event_ids = [event['message_id'] for event in pending_events]
        await self.redis.xclaim(k, self.name, self.worker_id, self.pending_event_timeout, event_ids)
        streams = {key: "0" for key in self.streams}
        pending_events = await self.redis.xreadgroup(self.name, self.worker_id, streams, None, 0)
        for stream in pending_events:
          for event in stream[1]:
            actions = self.actions
            formatted_event = [[stream[0], [event]]]
            e = Event(event=formatted_event)
            if e.action in actions:
              logging.debug(f"{datetime.now()} - XACK Stream: {e.stream} - {e.event_id}: {e.action} {e.data}")
              await self.handel_event(e.data)
              await self.redis.xack(e.stream, self.name, e.event_id)
              resp = await self.pusher.replace(REGISTRY)

  async def clear_idle_workers(self):
    for k in self.events.keys():
      existing_workers = await self.redis.xinfo_consumers(k, self.name)
      for worker in existing_workers:
        if worker['idle'] > self.worker_timeout:
          await self.redis.xgroup_delconsumer(k, self.name, worker['name'])
