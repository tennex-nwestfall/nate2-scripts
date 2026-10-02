import re

from nate2_scripts.console.resolvers import Context, Resolver
from nate2_scripts.console.types import Arn


class S3Resolver(Resolver):
    def get_service_names(self) -> list[str]:
        return ["s3"]

    def try_resolve_name(self, context: Context, name: str, search: str) -> str | None:
        # search query for the S3 is not in the url
        # so search is unused
        arn = Arn("s3", "", "", name)
        return self.get_s3_link_if_valid(context, arn)

    def try_resolve_arn(
        self,
        context: Context,
        arn: Arn,
    ) -> str | None:
        # not an s3 bucket arn
        if arn.service != "s3":
            return None

        return self.get_s3_link_if_valid(context, arn)

    def try_resolve_service(
        self, context: Context, service: str, search: str
    ) -> str | None:
        if service not in self.get_service_names():
            return None
        return "console.aws.amazon.com/s3/home"

    def try_resolve_id(self, context: Context, id: str) -> str | None:
        match = re.match(r"^s3://(.+)", id)
        if match:
            return self.get_s3_link_if_valid(context, Arn("s3", "", "", match.group(1)))
        return None

    def get_s3_link_if_valid(self, context: Context, arn: Arn) -> str | None:
        try:
            rest_parts = arn.resource.split("/")
            bucket_resp = context.session.client("s3").head_bucket(Bucket=rest_parts[0])
            context.set_region(
                bucket_resp["ResponseMetadata"]["HTTPHeaders"]["x-amz-bucket-region"]
            )
            # no path
            if len(rest_parts) == 0:
                return None
            # only bucket
            elif len(rest_parts) == 1:
                return self.get_arn_link(arn)
            # bucket and object
            elif len(rest_parts) > 1:
                if rest_parts[-1] == "":
                    response = context.session.client("s3").list_objects_v2(
                        Bucket=rest_parts[0], Prefix="/".join(rest_parts[1:]), MaxKeys=1
                    )
                    if response["KeyCount"] == 0:
                        return None
                else:
                    context.session.client("s3").head_object(
                        Bucket=rest_parts[0], Key="/".join(rest_parts[1:])
                    )
                return self.get_arn_link(arn)
        except Exception:  # noqa: BLE001
            return None
