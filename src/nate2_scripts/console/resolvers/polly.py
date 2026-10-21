from nate2_scripts.console.resolvers import Context, Resolver


class PollyResolver(Resolver):
    def get_service_names(self) -> list[str]:
        return ["polly"]

    def try_resolve_service(
        self, context: Context, service: str, search: str
    ) -> str | None:
        return "/polly/home"
