from typing import TypedDict
from urllib.parse import quote

import boto3


class CallerIdentity(TypedDict):
    UserId: str
    Account: str
    Arn: str


class Context:
    session: boto3.Session
    regions: list[str]
    identity: CallerIdentity

    def set_region(self, region: str):
        self.session._session.set_config_variable("region", region)

    @property
    def region(self) -> str:
        return self.session.region_name

    @property
    def account(self) -> str:
        return self.identity["Account"]


class Arn:
    region: str
    service: str
    resource: str
    account: str

    @staticmethod
    def try_parse(arn: str) -> "Arn | None":
        parts = arn.split(":")
        if len(parts) < 6:
            return None
        if parts[0] != "arn":
            return None
        if parts[1] != "aws":
            return None

        return Arn(*parts[2:])

    def __init__(self, service="", region="", account="", *resource):
        self.service = service
        self.region = region
        self.account = account
        self.resource = ":".join(resource)

    def encode(self) -> str:
        return quote(self.str())

    def str(self) -> str:
        return f"arn:aws:{self.service}:{self.region}:{self.account}:{self.resource}"
