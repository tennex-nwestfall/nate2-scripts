from nate2_scripts.console.resolvers import Context, Resolver


class LightsailResolver(Resolver):
    def get_service_names(self) -> list[str]:
        return ["lightsail", "ls"]

    def try_resolve_service(
        self, context: Context, service: str, search: str
    ) -> str | None:
        return "/lightsail/webapp/home/instances"
