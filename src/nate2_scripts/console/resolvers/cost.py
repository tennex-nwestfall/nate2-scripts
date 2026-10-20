from nate2_scripts.console.resolvers import Context, Resolver


class CostResolver(Resolver):
    def get_service_names(self) -> list[str]:
        return ["cost"]

    def try_resolve_service(
        self, context: Context, service: str, search: str
    ) -> str | None:
        # Cost Management is only available in the us-east-1 region
        context.set_region("us-east-1")
        return "/costmanagement/home"
