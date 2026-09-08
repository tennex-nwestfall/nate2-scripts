from nate2_scripts.console.resolvers import Arn, Context, Resolver, split


class EksResolver(Resolver):
    def get_service_names(self) -> list[str]:
        return ["eks"]

    def try_resolve_name(self, context: Context, name: str, search: str) -> str | None:
        return None

    def try_resolve_arn(self, context: Context, arn: Arn) -> str | None:
        if arn.service != "eks":
            return None

        resource_type, resource_id = split(arn.resource, 1, "/")
        if resource_type != "cluster":
            return None
        region = arn.region
        try:
            context.session.client("eks", region_name=region).describe_cluster(
                name=resource_id
            )
            return f"{region}.console.aws.amazon.com/eks/home?region={region}#/clusters/{resource_id}"
        except Exception:
            return None

    def try_resolve_service(
        self, context: Context, service: str, search: str
    ) -> str | None:
        if service not in self.get_service_names():
            return None
        return f"{context.default_region}.console.aws.amazon.com/eks/"

    def try_resolve_id(self, context: Context, id: str) -> str | None:
        return None
