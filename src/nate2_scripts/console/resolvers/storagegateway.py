from nate2_scripts.console.resolvers import Context, Resolver


class StorageGatewayResolver(Resolver):
    def get_service_names(self) -> list[str]:
        return ["storagegateway", "sgw"]

    def try_resolve_service(
        self, context: Context, service: str, search: str
    ) -> str | None:
        return "/storagegateway/home#/gateways"
