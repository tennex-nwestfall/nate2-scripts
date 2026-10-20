import urllib.parse

from nate2_scripts.console.resolvers import Arn, Context, Resolver, split


class LambdaResolver(Resolver):
    def get_service_names(self) -> list[str]:
        return ["lambda"]

    def try_resolve_name(self, context: Context, name: str) -> str | None:
        for region in context.regions:
            try:
                response = context.session.client(
                    "lambda", region_name=region
                ).get_function(FunctionName=name)
                context.set_region(region)
                arn = response["Configuration"]["FunctionArn"]  # type: ignore
                return self.get_arn_str_link(arn)
            except Exception:  # noqa: BLE001, S112
                continue
        return None

    def try_resolve_arn(self, context: Context, arn: Arn) -> str | None:
        if arn.service != "lambda":
            return None

        resource_type, resource_id = split(arn.resource, 1, ":")
        if resource_type != "function":
            return None
        context.set_region(arn.region)
        try:
            context.session.client("lambda").get_function(
                FunctionName=resource_id or ""
            )
            return self.get_arn_link(arn)
        except Exception:  # noqa: BLE001
            return None

    def try_resolve_service(
        self, context: Context, service: str, search: str
    ) -> str | None:
        base = "/lambda/home"
        if search:
            return f"{base}#functions?o0=:&v0={urllib.parse.quote(search)}"
        return base
