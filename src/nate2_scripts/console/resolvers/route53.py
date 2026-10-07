import base64

from nate2_scripts.console.resolvers import Arn, Context, Resolver


class Route53Resolver(Resolver):
    def get_service_names(self) -> list[str]:
        return ["route53", "53", "rr"]

    def try_resolve_name(self, context: Context, name: str) -> str | None:
        return None

    def try_resolve_arn(self, context: Context, arn: Arn) -> str | None:
        return None

    def try_resolve_service(
        self, context: Context, service: str, search: str
    ) -> str | None:
        if service not in self.get_service_names():
            return None
        if service == "rr":
            context.useprefix = False
            return base64.b64decode(b"eW91dHUuYmUvZFF3NHc5V2dYY1E=").decode()
        return "/route53/v2/home"

    def try_resolve_id(self, context: Context, id: str) -> str | None:
        return None
