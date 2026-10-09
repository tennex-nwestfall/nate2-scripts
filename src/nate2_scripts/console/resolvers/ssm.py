from urllib.parse import quote

from nate2_scripts.console.resolvers import Arn, Context, Resolver


class SsmResolver(Resolver):
    def get_service_names(self) -> list[str]:
        return ["ssm", "parameter", "ps"]

    def try_resolve_name(self, context: Context, name: str) -> str | None:
        return None

    def try_resolve_arn(self, context: Context, arn: Arn) -> str | None:
        return None

    def try_resolve_service(
        self, context: Context, service: str, search: str
    ) -> str | None:

        if service == "ssm":
            return "/systems-manager/home"
        if search:
            return f"/systems-manager/parameters#list_parameter_filters=Name:%3A:{quote(search)}"
        return "/systems-manager/parameters"

    def try_resolve_id(self, context: Context, id: str) -> str | None:
        return None
