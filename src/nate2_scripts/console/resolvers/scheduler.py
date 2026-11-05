from nate2_scripts.console.resolvers import Context, Resolver


class SchedulerResolver(Resolver):
    def get_service_names(self) -> list[str]:
        return ["scheduler", "sch"]

    def try_resolve_service(
        self, context: Context, service: str, search: str
    ) -> str | None:
        return "/scheduler/home#schedules"
