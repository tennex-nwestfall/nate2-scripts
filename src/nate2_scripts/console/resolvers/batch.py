from nate2_scripts.console.resolvers import Arn, Context, Resolver, split


class BatchResolver(Resolver):
    def get_service_names(self) -> list[str]:
        return ["batch"]

    def try_resolve_name(self, context: Context, name: str, search: str) -> str | None:
        return None

    def try_resolve_arn(self, context: Context, arn: Arn) -> str | None:
        if arn.service != "batch":
            return None

        resource_type, resource_id = split(arn.resource, 1, "/")
        region = arn.region
        account = arn.account
        client = context.session.client("batch", region_name=region)
        base = f"{region}.console.aws.amazon.com/batch/home?region={region}"
        try:
            if resource_type == "job-queue":
                result = client.describe_job_queues(jobQueues=[resource_id])
                if not result.get("jobQueues"):
                    return None
                full_arn = f"arn:aws:batch:{region}:{account}:job-queue/{resource_id}"
                return f"{base}#queues/detail/{full_arn}"
            if resource_type == "compute-environment":
                result = client.describe_compute_environments(
                    computeEnvironments=[resource_id]
                )
                if not result.get("computeEnvironments"):
                    return None
                full_arn = f"arn:aws:batch:{region}:{account}:compute-environment/{resource_id}"
                return f"{base}#compute-environments/detail/{full_arn}"
            if resource_type == "job-definition":
                full_arn = (
                    f"arn:aws:batch:{region}:{account}:job-definition/{resource_id}"
                )
                result = client.describe_job_definitions(jobDefinitions=[full_arn])
                if not result.get("jobDefinitions"):
                    return None
                return f"{base}#job-definition/detail/{full_arn}"
            if resource_type == "job":
                result = client.describe_jobs(jobs=[resource_id])
                if not result.get("jobs"):
                    return None
                return f"{base}#jobs/detail/{resource_id}"
        except Exception:
            return None
        return None

    def try_resolve_service(
        self, context: Context, service: str, search: str
    ) -> str | None:
        if service not in self.get_service_names():
            return None
        return f"{context.default_region}.console.aws.amazon.com/batch/"

    def try_resolve_id(self, context: Context, id: str) -> str | None:
        return None
