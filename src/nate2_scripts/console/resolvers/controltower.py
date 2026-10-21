from nate2_scripts.console.resolvers import Context, Resolver


class ControlTowerResolver(Resolver):
    def get_service_names(self) -> list[str]:
        return ["controltower"]

    def try_resolve_service(
        self, context: Context, service: str, search: str
    ) -> str | None:
        return "/controltower/home/landing"
