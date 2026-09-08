from nate2_scripts.console.resolvers import Arn, Context, Resolver, split


class EcsResolver(Resolver):
    def get_service_names(self) -> list[str]:
        return ["ecs"]

    def try_resolve_name(self, context: Context, name: str, search: str) -> str | None:
        return None

    def try_resolve_arn(self, context: Context, arn: Arn) -> str | None:
        if arn.service != "ecs":
            return None

        resource_type, resource_id = split(arn.resource, 1, "/")
        region = arn.region
        client = context.session.client("ecs", region_name=region)
        base = f"{region}.console.aws.amazon.com/ecs/v2/clusters"
        try:
            if resource_type == "cluster":
                result = client.describe_clusters(clusters=[resource_id])
                active = [
                    c for c in result.get("clusters", []) if c["status"] == "ACTIVE"
                ]
                if not active:
                    return None
                return f"{base}/{resource_id}/services?region={region}"
            if resource_type == "service":
                cluster, service_name = split(resource_id, 1, "/")
                result = client.describe_services(
                    cluster=cluster, services=[service_name]
                )
                active = [
                    s for s in result.get("services", []) if s["status"] == "ACTIVE"
                ]
                if not active:
                    return None
                return f"{base}/{cluster}/services/{service_name}?region={region}"
            if resource_type == "task":
                cluster, task_id = split(resource_id, 1, "/")
                result = client.describe_tasks(cluster=cluster, tasks=[task_id])
                if not result.get("tasks"):
                    return None
                return f"{base}/{cluster}/tasks/{task_id}?region={region}"
            if resource_type == "task-definition":
                family, revision = split(resource_id, 1, ":")
                td = f"{family}:{revision}" if revision else family
                result = client.describe_task_definition(taskDefinition=td)
                if not result.get("taskDefinition"):
                    return None
                base_td = f"{region}.console.aws.amazon.com/ecs/v2/task-definitions"
                if revision:
                    return f"{base_td}/{family}/{revision}?region={region}"
                return f"{base_td}/{family}?region={region}"
        except Exception:
            return None
        return None

    def try_resolve_service(
        self, context: Context, service: str, search: str
    ) -> str | None:
        if service not in self.get_service_names():
            return None
        return f"{context.default_region}.console.aws.amazon.com/ecs/"

    def try_resolve_id(self, context: Context, id: str) -> str | None:
        return None
