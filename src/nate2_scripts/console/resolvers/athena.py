from nate2_scripts.console.resolvers import Arn, Context, Resolver


class AthenaResolver(Resolver):
    def get_service_names(self) -> list[str]:
        return ["athena"]

    def try_resolve_name(self, context: Context, name: str) -> str | None:
        return None

    def try_resolve_arn(self, context: Context, arn: Arn) -> str | None:
        return None

    def try_resolve_service(
        self, context: Context, service: str, search: str
    ) -> str | None:
        return "/athena/home#/query-editor"

    def try_resolve_id(self, context: Context, id: str) -> str | None:
        return None
