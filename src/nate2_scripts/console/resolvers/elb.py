from nate2_scripts.console.resolvers import Arn, Context, Resolver, split


class ElbResolver(Resolver):
    def get_service_names(self) -> list[str]:
        return ["elb"]

    def try_resolve_name(self, context: Context, name: str, search: str) -> str | None:
        return None

    def try_resolve_arn(self, context: Context, arn: Arn) -> str | None:
        if arn.service != "elasticloadbalancing":
            return None

        resource_type, resource_id = split(arn.resource, 1, "/")
        region = arn.region
        client = context.session.client("elbv2", region_name=region)
        base = f"{region}.console.aws.amazon.com/ec2/home?region={region}"
        full_arn = f"arn:aws:elasticloadbalancing:{region}:{arn.account}:{arn.resource}"
        try:
            if resource_type == "loadbalancer":
                result = client.describe_load_balancers(LoadBalancerArns=[full_arn])
                if not result.get("LoadBalancers"):
                    return None
                return f"{base}#LoadBalancers:loadBalancerArn={full_arn}"
            if resource_type == "targetgroup":
                result = client.describe_target_groups(TargetGroupArns=[full_arn])
                if not result.get("TargetGroups"):
                    return None
                return f"{base}#TargetGroup:targetGroupArn={full_arn}"
        except Exception:
            return None
        return None

    def try_resolve_service(
        self, context: Context, service: str, search: str
    ) -> str | None:
        if service not in self.get_service_names():
            return None
        region = context.default_region
        return f"{region}.console.aws.amazon.com/ec2/home#LoadBalancers"

    def try_resolve_id(self, context: Context, id: str) -> str | None:
        return None
