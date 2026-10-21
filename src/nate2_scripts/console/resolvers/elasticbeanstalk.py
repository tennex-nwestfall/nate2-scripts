from nate2_scripts.console.resolvers import Context, Resolver


class ElasticBeanstalkResolver(Resolver):
    def get_service_names(self) -> list[str]:
        return ["elasticbeanstalk", "bean"]

    def try_resolve_service(
        self, context: Context, service: str, search: str
    ) -> str | None:
        return "/elasticbeanstalk/applications"
