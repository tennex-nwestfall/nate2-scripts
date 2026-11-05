from nate2_scripts.console.resolvers import Context, Resolver


class DataSyncResolver(Resolver):
    def get_service_names(self) -> list[str]:
        return ["datasync", "ds"]

    def try_resolve_service(
        self, context: Context, service: str, search: str
    ) -> str | None:
        return "/datasync/home#/tasks"
