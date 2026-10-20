from nate2_scripts.console.resolvers import Context, Resolver


class CloudTrailResolver(Resolver):
    def get_service_names(self) -> list[str]:
        return ["cloudtrail", "ct"]

    def try_resolve_service(
        self, context: Context, service: str, search: str
    ) -> str | None:
        return "/cloudtrailv2/home"
