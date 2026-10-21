from nate2_scripts.console.resolvers import Context, Resolver


class RdsResolver(Resolver):
    def get_service_names(self) -> list[str]:
        return ["rds"]

    # def try_resolve_arn(self, context: Context, arn: Arn) -> str | None:
    #     if arn.service != "rds":
    #         return None

    #     resource_type, resource_id = split(arn.resource, 1, ":")
    #     region = arn.region
    #     try:
    #         client = context.session.client("rds", region_name=region)
    #         base = f"{region}.console.aws.amazon.com/rds/home?region={region}"
    #         if resource_type == "db":
    #             if client.describe_db_instances(DBInstanceIdentifier=resource_id)[
    #                 "DBInstances"
    #             ]:
    #                 return f"{base}#database:id={resource_id};is-cluster=false"
    #         elif resource_type == "cluster":
    #             if client.describe_db_clusters(DBClusterIdentifier=resource_id)[
    #                 "DBClusters"
    #             ]:
    #                 return f"{base}#database:id={resource_id};is-cluster=true"
    #     except Exception:
    #         return None
    #     return None

    def try_resolve_service(
        self, context: Context, service: str, search: str
    ) -> str | None:
        return "/rds"
