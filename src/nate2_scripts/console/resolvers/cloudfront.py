from nate2_scripts.console.resolvers import Context, Resolver


class CloudFrontResolver(Resolver):
    def get_service_names(self) -> list[str]:
        # "cf" conflicts with cloudformation, so "front" is the alias instead
        return ["cloudfront", "front"]

    def try_resolve_service(
        self, context: Context, service: str, search: str
    ) -> str | None:
        return "/cloudfront/v4/home#/distributions"
