import json
from typing import TypedDict


class Secrets(TypedDict):
    bot_token: str


with open("secrets.json", "r") as f:
    secrets = json.load(f)


def get_secrets() -> Secrets:
    return secrets
