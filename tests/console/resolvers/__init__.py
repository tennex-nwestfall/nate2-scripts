import boto3


def make_session(profile_name: str, region: str | None = None):
    return boto3.Session(
        profile_name=profile_name,
        region_name=region,
    )
