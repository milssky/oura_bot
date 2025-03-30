import pytest


@pytest.mark.asyncio
async def test_get_total_sleep(oura_client, mock_response_factory) -> None:
    client, mock_transport = oura_client

    custom_response = mock_response_factory(
        json_data={'data': [{'id': 'test', 'score': 85}]},
        status_code=200,
    )
    mock_transport.handle_async_request.return_value = custom_response

    result = await client.get_total_sleep()
    assert isinstance(result, dict)
    assert 'data' in result
    assert len(result['data']) == 1
    assert 'score' in result['data'][0]
    assert result['data'][0]['score'] == 85
