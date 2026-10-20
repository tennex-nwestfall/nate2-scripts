from nate2_scripts.console.resolvers import Context, Resolver


class AthenaResolver(Resolver):
    def get_service_names(self) -> list[str]:
        return ["athena"]

    def try_resolve_service(
        self, context: Context, service: str, search: str
    ) -> str | None:
        return "/athena/home#/query-editor"
