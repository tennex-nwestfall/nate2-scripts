from nate2_scripts.console.resolvers import Context, Resolver


class ConfigResolver(Resolver):
    def get_service_names(self) -> list[str]:
        return ["config", "cfg"]

    def try_resolve_service(
        self, context: Context, service: str, search: str
    ) -> str | None:
        return "/config#/dashboard"
