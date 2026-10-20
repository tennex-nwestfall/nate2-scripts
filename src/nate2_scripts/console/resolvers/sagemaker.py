from nate2_scripts.console.resolvers import Context, Resolver


class SagemakerResolver(Resolver):
    def get_service_names(self) -> list[str]:
        return ["sagemaker", "sage"]

    def try_resolve_service(
        self, context: Context, service: str, search: str
    ) -> str | None:
        return "/sagemaker/home#/dashboard"
