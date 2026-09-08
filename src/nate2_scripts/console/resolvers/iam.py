from nate2_scripts.console.resolvers import Arn, Context, Resolver, split


class IamResolver(Resolver):
    def get_service_names(self) -> list[str]:
        return ["iam"]

    def try_resolve_name(self, context: Context, name: str, search: str) -> str | None:
        return None

    def try_resolve_arn(self, context: Context, arn: Arn) -> str | None:
        if arn.service != "iam":
            return None

        resource_type, resource_id = split(arn.resource, 1, "/")
        try:
            if resource_type == "role":
                # service-linked roles have a path prefix (e.g. aws-service-role/svc/RoleName)
                role_name = resource_id.split("/")[-1] if resource_id else ""
                context.session.client("iam").get_role(RoleName=role_name)
                return f"us-east-1.console.aws.amazon.com/iam/home#/roles/{role_name}"
            if resource_type == "user":
                context.session.client("iam").get_user(UserName=resource_id)
                return f"us-east-1.console.aws.amazon.com/iam/home#/users/{resource_id}"
        except Exception:
            return None
        return None

    def try_resolve_service(
        self, context: Context, service: str, search: str
    ) -> str | None:
        if service not in self.get_service_names():
            return None
        return f"{context.default_region}.console.aws.amazon.com/iam/"

    def try_resolve_id(self, context: Context, id: str) -> str | None:
        try:
            if id.startswith("role/"):
                name = id[len("role/") :]
                context.session.client("iam").get_role(RoleName=name)
                return f"us-east-1.console.aws.amazon.com/iam/home#/roles/{name}"
            if id.startswith("usr/"):
                name = id[len("usr/") :]
                context.session.client("iam").get_user(UserName=name)
                return f"us-east-1.console.aws.amazon.com/iam/home#/users/{name}"
        except Exception:
            return None
        return None
