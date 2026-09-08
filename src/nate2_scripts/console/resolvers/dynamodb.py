from nate2_scripts.console.resolvers import Arn, Context, Resolver, split


class DynamoDbResolver(Resolver):
    def get_service_names(self) -> list[str]:
        return ["dynamo"]

    def try_resolve_name(self, context: Context, name: str, search: str) -> str | None:
        return None

    def try_resolve_arn(self, context: Context, arn: Arn) -> str | None:
        if arn.service != "dynamodb":
            return None

        resource_type, resource_id = split(arn.resource, 1, "/")
        if resource_type != "table":
            return None
        region = arn.region
        try:
            context.session.client("dynamodb", region_name=region).describe_table(
                TableName=resource_id
            )
            return f"{region}.console.aws.amazon.com/dynamodbv2/home?region={region}#table?name={resource_id}"
        except Exception:
            return None

    def try_resolve_service(
        self, context: Context, service: str, search: str
    ) -> str | None:
        if service not in self.get_service_names():
            return None
        return f"{context.default_region}.console.aws.amazon.com/dynamodb/"

    def try_resolve_id(self, context: Context, id: str) -> str | None:
        return None
