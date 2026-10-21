from nate2_scripts.console.resolvers import Context, Resolver


class LexResolver(Resolver):
    def get_service_names(self) -> list[str]:
        return ["lex"]

    def try_resolve_service(
        self, context: Context, service: str, search: str
    ) -> str | None:
        return "/lexv2/home#bots"
