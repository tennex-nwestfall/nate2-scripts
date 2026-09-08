from nate2_scripts.console.resolvers import Arn, Context, Resolver, split


class LambdaResolver(Resolver):
    def get_service_names(self) -> list[str]:
        return ["lambda"]

    def try_resolve_name(self, context: Context, name: str, search: str) -> str | None:
        for region in context.regions:
            try:
                context.session.client("lambda", region_name=region).get_function(
                    FunctionName=name
                )
                return f"{region}.console.aws.amazon.com/lambda/home?region={region}#/functions/{name}"
            except Exception:
                continue
        return None

    def try_resolve_arn(self, context: Context, arn: Arn) -> str | None:
        if arn.service != "lambda":
            return None

        resource_type, resource_id = split(arn.resource, 1, ":")
        if resource_type != "function":
            return None
        region = arn.region
        try:
            context.session.client("lambda", region_name=region).get_function(
                FunctionName=resource_id
            )
            return f"{region}.console.aws.amazon.com/lambda/home?region={region}#/functions/{resource_id}"
        except Exception:
            return None

    def try_resolve_service(
        self, context: Context, service: str, search: str
    ) -> str | None:
        if service not in self.get_service_names():
            return None
        region = context.default_region
        return f"{region}.console.aws.amazon.com/lambda/"

    def try_resolve_id(self, context: Context, id: str) -> str | None:
        return None
