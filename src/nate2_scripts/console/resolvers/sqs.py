import urllib.parse

from nate2_scripts.console.resolvers import Arn, Context, Resolver


class SqsResolver(Resolver):
    def get_service_names(self) -> list[str]:
        return ["sqs"]

    def try_resolve_name(self, context: Context, name: str, search: str) -> str | None:
        return None

    def try_resolve_arn(self, context: Context, arn: Arn) -> str | None:
        if arn.service != "sqs":
            return None

        region = arn.region
        queue = arn.resource
        try:
            url = context.session.client("sqs", region_name=region).get_queue_url(
                QueueName=queue, QueueOwnerAWSAccountId=arn.account
            )["QueueUrl"]
            encoded = urllib.parse.quote(url, safe="")
            return f"{region}.console.aws.amazon.com/sqs/v3/home?region={region}#/queues/{encoded}"
        except Exception:
            return None

    def try_resolve_service(
        self, context: Context, service: str, search: str
    ) -> str | None:
        if service not in self.get_service_names():
            return None
        return f"{context.default_region}.console.aws.amazon.com/sqs/"

    def try_resolve_id(self, context: Context, id: str) -> str | None:
        return None
