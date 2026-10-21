from nate2_scripts.console.resolvers import Context, Resolver


class ArtifactResolver(Resolver):
    def get_service_names(self) -> list[str]:
        return ["artifact"]

    def try_resolve_service(
        self, context: Context, service: str, search: str
    ) -> str | None:
        return "/artifact/v2/home"
