from abc import ABC, abstractmethod
from urllib.parse import quote

import boto3

from nate2_scripts.console.types import Context


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
        return quote(
            f"arn:aws:{self.service}:{self.region}:{self.account}:{self.resource}"
        )


def split(arn: str | None, num: int, chr=":") -> list[str | None]:
    return ((arn.split(chr, num) if arn else []) + [None] * 10)[: num + 1]


class Resolver(ABC):
    @abstractmethod
    def get_service_names(self) -> list[str]:
        pass

    @abstractmethod
    def try_resolve_name(self, context: Context, name: str, search: str) -> str | None:
        pass

    @abstractmethod
    def try_resolve_arn(
        self,
        context: Context,
        arn: Arn,
    ) -> str | None:
        pass

    @abstractmethod
    def try_resolve_service(
        self, context: Context, service: str, search: str
    ) -> str | None:
        pass

    @abstractmethod
    def try_resolve_id(self, context: Context, id: str) -> str | None:
        pass

    def get_arn_link(self, arn: Arn) -> str:
        return f"console.aws.amazon.com/go/view?arn={arn.encode()}"
