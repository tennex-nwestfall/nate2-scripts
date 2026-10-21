from nate2_scripts.console.resolvers import Context, Resolver


class QuickResolver(Resolver):
    def get_service_names(self) -> list[str]:
        return ["quick"]

    def try_resolve_service(
        self, context: Context, service: str, search: str
    ) -> str | None:
        # TODO: not sure how to get this to work
        # different from other services, Quicksight has its own path and domain
        # context.set_region("us-east-1.quicksight")
        context.useprefix = False
        return "quicksight.aws.amazon.com/"
