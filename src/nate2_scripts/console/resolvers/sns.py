from nate2_scripts.console.resolvers import Arn, Context, Resolver


class SnsResolver(Resolver):
    def get_service_names(self) -> list[str]:
        return ["sns"]

    def try_resolve_name(self, context: Context, name: str, search: str) -> str | None:
        return None

    def try_resolve_arn(self, context: Context, arn: Arn) -> str | None:
        if arn.service != "sns":
            return None

        region = arn.region
        topic = arn.resource
        full_arn = f"arn:aws:sns:{region}:{arn.account}:{topic}"
        try:
            context.session.client("sns", region_name=region).get_topic_attributes(
                TopicArn=full_arn
            )
            return f"{region}.console.aws.amazon.com/sns/v3/home?region={region}#/topic/{full_arn}"
        except Exception:
            return None

    def try_resolve_service(
        self, context: Context, service: str, search: str
    ) -> str | None:
        if service not in self.get_service_names():
            return None
        return f"{context.default_region}.console.aws.amazon.com/sns/"

    def try_resolve_id(self, context: Context, id: str) -> str | None:
        return None
