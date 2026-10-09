from nate2_scripts.console.resolvers import Arn, Context, Resolver


class SupportResolver(Resolver):
    def get_service_names(self) -> list[str]:
        return ["support"]

    def try_resolve_name(self, context: Context, name: str) -> str | None:
        return None

    def try_resolve_arn(self, context: Context, arn: Arn) -> str | None:
        return None

    def try_resolve_service(
        self, context: Context, service: str, search: str
    ) -> str | None:
        # link must have the region section set to "support"
        # bad but better than changing the overall resolver logic
        context.set_region("support")
        return "/support/home"

    def try_resolve_id(self, context: Context, id: str) -> str | None:
        return None
