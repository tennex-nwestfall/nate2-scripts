from abc import ABC, abstractmethod
from urllib.parse import quote

from nate2_scripts.console.types import Arn, Context


def split(arn: str | None, num: int, chr=":") -> list[str | None]:
    return ((arn.split(chr, num) if arn else []) + [None] * 10)[: num + 1]


class Resolver(ABC):
    @abstractmethod
    def get_service_names(self) -> list[str]:
        """Return a list of service names that this resolver can handle."""

    def try_resolve_name(self, context: Context, name: str) -> str | None:
        """Try to resolve the given name within the provided context."""
        return None

    def try_resolve_arn(
        self,
        context: Context,
        arn: Arn,
    ) -> str | None:
        """Try to resolve the given ARN within the provided context."""
        return None

    @abstractmethod
    def try_resolve_service(
        self, context: Context, service: str, search: str
    ) -> str | None:
        """Try to resolve the given service name within the provided context."""

    def try_resolve_id(self, context: Context, id: str) -> str | None:
        """Try to resolve the given ID within the provided context."""
        return None

    def get_arn_link(self, arn: Arn) -> str:
        """Return a link to view the given ARN."""
        return f"/go/view?arn={arn.encode()}"

    def get_arn_str_link(self, arn: str) -> str:
        """Return a link to view the given ARN string."""
        return f"/go/view?arn={quote(arn)}"
