from nate2_scripts.console.resolvers import Context, Resolver


class BackupResolver(Resolver):
    def get_service_names(self) -> list[str]:
        return ["backup", "bp"]

    def try_resolve_service(
        self, context: Context, service: str, search: str
    ) -> str | None:
        return "/backup/home#/dashboard/activity/backup/"
