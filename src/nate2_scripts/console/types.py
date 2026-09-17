from typing import TypedDict

import boto3


class CallerIdentity(TypedDict):
    UserId: str
    Account: str
    Arn: str


class Context:
    session: boto3.Session
    regions: list[str]
    identity: CallerIdentity
    current_region: str
