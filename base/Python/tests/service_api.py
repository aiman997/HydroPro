import sys, os
import asyncio
import redis.asyncio as redis
import pytest

from unittest.mock import AsyncMock, Mock
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from lib.service import Service

@pytest.fixture
async def service():
    # Replace with appropriate connection details
    redis_conn = Mock()
    metrics_provider = Mock()
    service_instance = Service(
        name="test_service",
        stream="test_stream",
        streams=["test_stream"],
        actions=["action1", "action2"],
        redis_conn=redis_conn,
        metrics_provider=metrics_provider
    )
    yield service_instance
    await service_instance.redis.close()
    await service_instance.redis.wait_closed()

# Test generating worker ID
@pytest.mark.asyncio
async def test_generate_worker_id(service):
    worker_id = service.generate_worker_id()
    assert worker_id is not None

# Test RPC decorator
@pytest.mark.asyncio
async def test_rpc_decorator(service):
    @service.rpc
    async def test_rpc_method(self, args):
        return args

    assert callable(test_rpc_method)
    assert test_rpc_method.__name__ == 'wrap_func'

# Test sending an event
@pytest.mark.asyncio
async def test_send_event(service):
    await service.send_event("action1", {"key": "value"})

# Test creating a consumer group
@pytest.mark.asyncio
async def test_create_consumer_group(service):
    await service.create_consumer_group()
