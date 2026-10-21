from nate2_scripts.console.resolvers import Context, Resolver


class InspectorResolver(Resolver):
    def get_service_names(self) -> list[str]:
        return ["inspector"]

    def try_resolve_service(
        self, context: Context, service: str, search: str
    ) -> str | None:
        return "/inspector/v2/home#/dashboard"
