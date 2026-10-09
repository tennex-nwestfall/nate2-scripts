import urllib.parse

from nate2_scripts.console.resolvers import Arn, Context, Resolver, split


class LambdaResolver(Resolver):
    def get_service_names(self) -> list[str]:
        return ["lambda"]

    def try_resolve_name(self, context: Context, name: str) -> str | None:
        # TODO: implement name resolution for Lambda functions
        return None
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
        # TODO: implement ARN resolution for Lambda functions
        return None
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
        base = "/lambda/home"
        if search:
            return f"{base}#functions?o0=:&v0={urllib.parse.quote(search)}"
        return base

    def try_resolve_id(self, context: Context, id: str) -> str | None:
        return None
