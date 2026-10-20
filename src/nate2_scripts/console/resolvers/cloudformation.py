from urllib.parse import quote_plus

from nate2_scripts.console.resolvers import Context, Resolver


class CloudFormationResolver(Resolver):
    def get_service_names(self) -> list[str]:
        return ["cloudformation", "cf"]

    def try_resolve_name(self, context: Context, name: str) -> str | None:
        for region in context.regions:
            try:
                client = context.session.client("cloudformation", region_name=region)
                result = client.describe_stacks(StackName=name)
                stacks = result.get("Stacks", [])
                if stacks:
                    context.set_region(region)
                    return self.get_arn_str_link(stacks[0]["StackId"])  # type: ignore
            except Exception:  # noqa: BLE001, S112
                continue
        return None

    def try_resolve_service(
        self, context: Context, service: str, search: str
    ) -> str | None:
        if search:
            return f"/cloudformation/home#/stacks?filteringText={quote_plus(search)}&filteringStatus=active&viewNested=true"
        return "/cloudformation/home#/stacks"
