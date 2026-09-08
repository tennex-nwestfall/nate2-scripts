from nate2_scripts.console.resolvers import Arn, Context, Resolver


class TennexResolver(Resolver):
    def get_service_names(self) -> list[str]:
        return ["tennex"]

    def try_resolve_name(self, context: Context, name: str, search: str) -> str | None:
        return None

    def try_resolve_arn(self, context: Context, arn: Arn) -> str | None:
        return None

    def try_resolve_service(
        self, context: Context, service: str, search: str
    ) -> str | None:
        if service not in self.get_service_names():
            return None
        region = context.default_region
        return (
            f"{region}.console.aws.amazon.com/marketplace/search"
            "?applicationId=AWS-Marketplace-Console&ref_=ucaf&text=tennex"
        )

    def try_resolve_id(self, context: Context, id: str) -> str | None:
        return None
