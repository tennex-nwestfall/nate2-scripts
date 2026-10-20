from nate2_scripts.console.resolvers import Context, Resolver


class EksResolver(Resolver):
    def get_service_names(self) -> list[str]:
        return ["eks"]

    def try_resolve_service(
        self, context: Context, service: str, search: str
    ) -> str | None:
        return "/eks/clusters"
