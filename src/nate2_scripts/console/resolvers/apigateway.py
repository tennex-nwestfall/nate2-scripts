from nate2_scripts.console.resolvers import Context, Resolver


class ApiGatewayResolver(Resolver):
    def get_service_names(self) -> list[str]:
        return ["apigateway", "api"]

    def try_resolve_service(
        self, context: Context, service: str, search: str
    ) -> str | None:
        return "/apigateway/main/apis"
