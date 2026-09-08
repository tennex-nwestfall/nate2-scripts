from nate2_scripts.console.resolvers import Arn, Context, Resolver


class SsmResolver(Resolver):
    def get_service_names(self) -> list[str]:
        return ["ssm"]

    def try_resolve_name(self, context: Context, name: str, search: str) -> str | None:
        return None

    def try_resolve_arn(self, context: Context, arn: Arn) -> str | None:
        return None

    def try_resolve_service(
        self, context: Context, service: str, search: str
    ) -> str | None:
        if service not in self.get_service_names():
            return None
        return f"{context.default_region}.console.aws.amazon.com/systems-manager/"

    def try_resolve_id(self, context: Context, id: str) -> str | None:
        return None
