from nate2_scripts.console.resolvers import Context, Resolver


class DynamoResolver(Resolver):
    def get_service_names(self) -> list[str]:
        return ["dynamodb", "dynamo", "dyn"]

    # def try_resolve_arn(self, context: Context, arn: Arn) -> str | None:
    #     if arn.service != "dynamodb":
    #         return None

    #     resource_type, resource_id = split(arn.resource, 1, "/")
    #     if resource_type != "table":
    #         return None
    #     region = arn.region
    #     try:
    #         context.session.client("dynamodb", region_name=region).describe_table(
    #             TableName=resource_id
    #         )
    #         return f"{region}.console.aws.amazon.com/dynamodbv2/home?region={region}#table?name={resource_id}"
    #     except Exception:
    #         return None

    def try_resolve_service(
        self, context: Context, service: str, search: str
    ) -> str | None:
        return "/dynamodbv2/home#tables"
