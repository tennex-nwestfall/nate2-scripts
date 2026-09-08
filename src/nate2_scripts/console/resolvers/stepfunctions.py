import urllib.parse

from nate2_scripts.console.resolvers import Arn, Context, Resolver, split


class StepFunctionsResolver(Resolver):
    def get_service_names(self) -> list[str]:
        return ["step"]

    def try_resolve_name(self, context: Context, name: str, search: str) -> str | None:
        return None

    def try_resolve_arn(self, context: Context, arn: Arn) -> str | None:
        if arn.service != "states":
            return None

        resource_type, resource_id = split(arn.resource, 1, ":")
        region = arn.region
        account = arn.account
        client = context.session.client("stepfunctions", region_name=region)
        base = f"{region}.console.aws.amazon.com/states/home?region={region}"
        try:
            if resource_type == "stateMachine":
                full_arn = (
                    f"arn:aws:states:{region}:{account}:stateMachine:{resource_id}"
                )
                client.describe_state_machine(stateMachineArn=full_arn)
                return f"{base}#/statemachines/view/{urllib.parse.quote(full_arn, safe='')}"
            if resource_type == "execution":
                full_arn = f"arn:aws:states:{region}:{account}:execution:{resource_id}"
                client.describe_execution(executionArn=full_arn)
                return f"{base}#/v2/executions/details/{urllib.parse.quote(full_arn, safe='')}"
        except Exception:
            return None
        return None

    def try_resolve_service(
        self, context: Context, service: str, search: str
    ) -> str | None:
        if service not in self.get_service_names():
            return None
        return f"{context.default_region}.console.aws.amazon.com/states/"

    def try_resolve_id(self, context: Context, id: str) -> str | None:
        return None
