from abc import ABC, abstractmethod

from nate2_scripts.console.types import Arn, Context


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
