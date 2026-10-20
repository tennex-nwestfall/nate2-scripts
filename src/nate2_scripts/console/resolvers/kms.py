from nate2_scripts.console.resolvers import Context, Resolver


class KmsResolver(Resolver):
    def get_service_names(self) -> list[str]:
        return ["kms"]

    def try_resolve_service(
        self, context: Context, service: str, search: str
    ) -> str | None:
        return "/kms/home#/kms/keys"
