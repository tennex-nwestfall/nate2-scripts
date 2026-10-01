import boto3

from nate2_scripts.console.resolvers import Arn


def make_session(profile_name: str, region: str | None = None):
    return boto3.Session(
        profile_name=profile_name,
        region_name=region,
    )


def make_link(arn: Arn) -> str:
    return f"console.aws.amazon.com/go/view?arn={arn.encode()}"
