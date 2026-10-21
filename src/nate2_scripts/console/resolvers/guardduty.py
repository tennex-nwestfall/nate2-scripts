from nate2_scripts.console.resolvers import Context, Resolver


class GuardDutyResolver(Resolver):
    def get_service_names(self) -> list[str]:
        return ["guardduty", "guard"]

    def try_resolve_service(
        self, context: Context, service: str, search: str
    ) -> str | None:
        return "/guardduty/home#/summary"
