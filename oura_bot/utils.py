import tomllib
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


def load_users(data_path: Path = BASE_DIR / 'users.toml') -> list[dict[str, str]]:
    with open(data_path, 'rb') as f:
        users = tomllib.load(f)

    if 'users' not in users:
        return []
    return users['users']
