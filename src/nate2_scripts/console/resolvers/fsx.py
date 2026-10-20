from nate2_scripts.console.resolvers import Context, Resolver


class FsxResolver(Resolver):
    def get_service_names(self) -> list[str]:
        return ["fsx"]

    def try_resolve_service(
        self, context: Context, service: str, search: str
    ) -> str | None:
        return "/fsx#file-systems"
