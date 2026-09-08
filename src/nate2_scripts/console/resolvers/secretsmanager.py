import re
import urllib.parse

from nate2_scripts.console.resolvers import Arn, Context, Resolver, split


class SecretsManagerResolver(Resolver):
    def get_service_names(self) -> list[str]:
        return ["sm", "secretsmanager", "secretmanager"]

    def try_resolve_name(self, context: Context, name: str, search: str) -> str | None:
        return None

    def try_resolve_arn(self, context: Context, arn: Arn) -> str | None:
        if arn.service != "secretsmanager":
            return None

        resource_type, resource_id = split(arn.resource, 1, ":")
        if resource_type != "secret":
            return None
        region = arn.region
        full_arn = f"arn:aws:secretsmanager:{region}:{arn.account}:secret:{resource_id}"
        try:
            context.session.client(
                "secretsmanager", region_name=region
            ).describe_secret(SecretId=full_arn)
            # secret arns end with a random 6-char suffix that the console omits
            name = re.sub(r"-[A-Za-z0-9]{6}$", "", resource_id or "")
            encoded = urllib.parse.quote(name, safe="")
            return f"{region}.console.aws.amazon.com/secretsmanager/home?region={region}#!/secret?name={encoded}"
        except Exception:
            return None

    def try_resolve_service(
        self, context: Context, service: str, search: str
    ) -> str | None:
        if service not in self.get_service_names():
            return None
        return f"{context.default_region}.console.aws.amazon.com/secretsmanager/"

    def try_resolve_id(self, context: Context, id: str) -> str | None:
        return None
