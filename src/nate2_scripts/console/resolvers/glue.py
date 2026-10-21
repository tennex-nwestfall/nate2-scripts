from nate2_scripts.console.resolvers import Context, Resolver


class GlueResolver(Resolver):
    def get_service_names(self) -> list[str]:
        return ["glue"]

    def try_resolve_service(
        self, context: Context, service: str, search: str
    ) -> str | None:
        return "/gluestudio/home#/jobs"
