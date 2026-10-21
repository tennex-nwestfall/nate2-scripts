from nate2_scripts.console.resolvers import Context, Resolver


class EventBridgeResolver(Resolver):
    def get_service_names(self) -> list[str]:
        return ["eventbridge", "eb"]

    def try_resolve_service(
        self, context: Context, service: str, search: str
    ) -> str | None:
        return "/events/home#/dashboard"
