from typing import Generator

from httpx import Auth, Request, Response


class BearerAuth(Auth):
    """Bearer token auth class."""

    def __init__(self, *, token: str) -> None:
        self.token = token
        self._auth_header = self._build_auth_header(token=self.token)

    def auth_flow(self, request: Request) -> Generator[Request, Response, None]:
        request.headers['Authorization'] = self._auth_header
        yield request

    @staticmethod
    def _build_auth_header(*, token: str) -> str:
        return f'Bearer {token}'
