from nate2_scripts.console.resolvers import Arn, Context, Resolver


class CloudFrontResolver(Resolver):
    def get_service_names(self) -> list[str]:
        # "cf" conflicts with cloudformation, so "front" is the alias instead
        return ["cloudfront", "front"]

    def try_resolve_name(self, context: Context, name: str, search: str) -> str | None:
        return None

    def try_resolve_arn(self, context: Context, arn: Arn) -> str | None:
        return None

    def try_resolve_service(
        self, context: Context, service: str, search: str
    ) -> str | None:
        if service not in self.get_service_names():
            return None
        return f"{context.default_region}.console.aws.amazon.com/cloudfront/"

    def try_resolve_id(self, context: Context, id: str) -> str | None:
        return None
