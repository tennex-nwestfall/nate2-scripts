import urllib.parse

from nate2_scripts.console.resolvers import Arn, Context, Resolver, split


class LogsResolver(Resolver):
    def get_service_names(self) -> list[str]:
        return ["logs", "cw", "cloudwatch"]

    def try_resolve_name(self, context: Context, name: str, search: str) -> str | None:
        for region in context.regions:
            try:
                client = context.session.client("logs", region_name=region)
                result = client.describe_log_groups(logGroupNamePrefix=name)
                if any(
                    lg["logGroupName"] == name for lg in result.get("logGroups", [])
                ):
                    encoded = urllib.parse.quote(name, safe="")
                    return f"{region}.console.aws.amazon.com/cloudwatch/home?region={region}#logsV2:log-groups/log-group/{encoded}"
            except Exception:
                continue
        return None

    def try_resolve_arn(self, context: Context, arn: Arn) -> str | None:
        if arn.service != "logs":
            return None

        resource_type, resource_id = split(arn.resource, 1, ":")
        if resource_type != "log-group":
            return None
        region = arn.region
        # log-group arns often carry a trailing ':*' wildcard
        name = resource_id or ""
        if name.endswith(":*"):
            name = name[:-2]
        try:
            client = context.session.client("logs", region_name=region)
            result = client.describe_log_groups(logGroupNamePrefix=name)
            if not any(
                lg["logGroupName"] == name for lg in result.get("logGroups", [])
            ):
                return None
            encoded = urllib.parse.quote(name, safe="")
            return f"{region}.console.aws.amazon.com/cloudwatch/home?region={region}#logsV2:log-groups/log-group/{encoded}"
        except Exception:
            return None

    def try_resolve_service(
        self, context: Context, service: str, search: str
    ) -> str | None:
        if service not in self.get_service_names():
            return None
        region = context.default_region
        return f"{region}.console.aws.amazon.com/cloudwatch/home#logsV2:log-groups"

    def try_resolve_id(self, context: Context, id: str) -> str | None:
        return None
