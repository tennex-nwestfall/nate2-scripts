import urllib.parse
from asyncio import streams

from nate2_scripts.console.resolvers import Context, Resolver, split
from nate2_scripts.console.types import Arn


def cw_encode(value: str) -> str:
    return urllib.parse.quote(value, safe="").replace("%", "$25")


class LogsResolver(Resolver):
    def get_service_names(self) -> list[str]:
        return ["logs", "cw", "cloudwatch"]

    def try_resolve_name(self, context: Context, name: str, search: str) -> str | None:
        for region in context.regions:
            try:
                client = context.session.client("logs", region_name=region)
                result = client.describe_log_groups(logGroupNamePrefix=name, limit=1)
                groups = result.get("logGroups", [])
                if groups and groups[0]["logGroupName"] == name:
                    context.set_region(region)
                    arn = Arn("logs", region, context.account, "log-group", name, "*")
                    return self.get_arn_link(arn)
            except Exception:  # noqa: BLE001, S112
                continue
        return None

    def try_resolve_arn(self, context: Context, arn: Arn) -> str | None:
        if arn.service != "logs":
            return None

        resource_type, group, stream_type, stream_name = split(arn.resource, 3, ":")
        if resource_type != "log-group":
            return None

        name = group or ""
        try:
            client = context.session.client("logs")
            if stream_type == "*":
                result = client.describe_log_groups(logGroupNamePrefix=name, limit=1)
                groups = result.get("logGroups", [])
                if not groups or groups[0]["logGroupName"] != name:
                    return None
                arn = Arn(
                    "logs", context.region, context.account, "log-group", group, "*"
                )
            elif stream_type == "log-stream":
                result = client.describe_log_streams(
                    logGroupName=name, logStreamNamePrefix=stream_name, limit=1
                )
                streams = result.get("logStreams", [])
                if not streams or streams[0]["logStreamName"] != stream_name:
                    return None
                arn = Arn(
                    "logs",
                    context.region,
                    context.account,
                    "log-group",
                    group,
                    stream_type,
                    stream_name,
                )
            else:
                return None

            return self.get_arn_link(arn)
        except Exception:  # noqa: BLE001
            return None

    def try_resolve_service(
        self, context: Context, service: str, search: str
    ) -> str | None:
        if service not in self.get_service_names():
            return None

        if service == "logs":
            if search:
                return f"console.aws.amazon.com/cloudwatch/home#logsV2:log-groups$3FlogGroupNameFilter$3D{urllib.parse.quote_plus(search).replace('%', '$25')}"
            else:
                return "console.aws.amazon.com/cloudwatch/home#logsV2:log-groups"
        else:
            return "console.aws.amazon.com/cloudwatch/home"

    def try_resolve_id(self, context: Context, id: str) -> str | None:
        return None
