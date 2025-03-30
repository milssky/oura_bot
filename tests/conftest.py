from unittest.mock import AsyncMock

import pytest
from httpx import AsyncByteStream, Response
from tortoise import Tortoise

from oura_bot.client import OuraClient
from oura_bot.models import User
from oura_bot.repository import UserMeasureRepository


@pytest.fixture
def mock_response_factory():
    def factory(status_code=200, json_data=None, content=None):
        stream = AsyncMock(spec=AsyncByteStream)
        response = Response(
            status_code=status_code, json=json_data, content=content, request=AsyncMock()
        )
        response._stream = stream
        return response

    return factory


@pytest.fixture
async def oura_client(mock_response_factory):
    client = OuraClient(token='test_token')
    mock_transport = AsyncMock()
    client._transport = mock_transport

    mock_transport.handle_async_request.return_value = mock_response_factory(
        json_data={'default': 'response'}
    )

    yield client, mock_transport
    await client.aclose()


@pytest.fixture(scope='session', autouse=True)
async def initialize_tests():
    await Tortoise.init(db_url='sqlite://:memory:', modules={'models': ['oura_bot.models']})
    await Tortoise.generate_schemas()
    yield
    await Tortoise.close_connections()


@pytest.fixture
async def user():
    return await User.create(
        name='Test',
        timezone='America/Phoenix',
    )


@pytest.fixture
def repo():
    return UserMeasureRepository()
