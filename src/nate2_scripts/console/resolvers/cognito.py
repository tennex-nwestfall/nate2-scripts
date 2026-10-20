from nate2_scripts.console.resolvers import Context, Resolver


class CognitoResolver(Resolver):
    def get_service_names(self) -> list[str]:
        return ["cognito", "cn"]

    def try_resolve_service(
        self, context: Context, service: str, search: str
    ) -> str | None:
        return "/cognito/v2/idp/user-pools"
