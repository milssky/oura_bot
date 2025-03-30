from oura_bot.auth import BearerAuth


def test_bearer_auth() -> None:
    token = 'test_token'
    auth_header = f'Bearer {token}'
    auth = BearerAuth(token=token)
    assert auth._auth_header == auth_header
