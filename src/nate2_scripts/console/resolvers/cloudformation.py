import urllib.parse

from nate2_scripts.console.resolvers import Arn, Context, Resolver


class CloudFormationResolver(Resolver):
    def get_service_names(self) -> list[str]:
        return ["cloudformation", "cf"]

    def try_resolve_name(self, context: Context, name: str, search: str) -> str | None:
        for region in context.regions:
            try:
                client = context.session.client("cloudformation", region_name=region)
                result = client.describe_stacks(StackName=name)
                stacks = result.get("Stacks", [])
                if stacks:
                    stack_id = urllib.parse.quote(stacks[0]["StackId"], safe="")
                    return f"{region}.console.aws.amazon.com/cloudformation/home?region={region}#/stacks/stackinfo?stackId={stack_id}"
            except Exception:
                continue
        return None

    def try_resolve_arn(self, context: Context, arn: Arn) -> str | None:
        # cloudformation was never resolved via ARN in the original implementation
        return None

    def try_resolve_service(
        self, context: Context, service: str, search: str
    ) -> str | None:
        if service not in self.get_service_names():
            return None
        return f"{context.default_region}.console.aws.amazon.com/cloudformation/"

    def try_resolve_id(self, context: Context, id: str) -> str | None:
        return None
