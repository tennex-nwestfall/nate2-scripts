from nate2_scripts.console.resolvers import Context, Resolver


class EcrResolver(Resolver):
    def get_service_names(self) -> list[str]:
        return ["ecr", "docker"]

    def try_resolve_service(
        self, context: Context, service: str, search: str
    ) -> str | None:
        return "/ecr/private-registry/repositories"

    # def try_resolve_id(self, context: Context, id: str) -> str | None:
    #     # TODO parse 556471794894.dkr.ecr.us-west-2.amazonaws.com/abodybuilder3
    #     # deal with account change in here
    #     return None
