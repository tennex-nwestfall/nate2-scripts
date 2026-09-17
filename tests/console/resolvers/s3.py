import boto3
import pytest

from nate2_scripts.console import get_suffix
from nate2_scripts.console.resolvers import Arn
from tests.console.resolvers import make_session

EAST_1_BUCKET = "exists-bucket"
WEST_2_BUCKET = "exists-bucket-west"
B_BUCKET = "exists-bucket-B"
KEY = "this/file/exists.txt"
KEY2 = "this/file_exists.txt"


@pytest.fixture(autouse=True)
def s3_resources(aws_profiles):
    """Seed the moto backend (already active via the aws_profiles fixture) with
    the buckets/objects the tests check for existence."""
    session = boto3.Session(profile_name="fake-A-org", region_name="us-east-1")
    s3 = session.client("s3")
    s3.create_bucket(Bucket=EAST_1_BUCKET)
    s3.put_object(Bucket=EAST_1_BUCKET, Key=KEY, Body=b"wow!")
    s3.put_object(Bucket=EAST_1_BUCKET, Key=KEY2, Body=b"wow2")

    session = boto3.Session(profile_name="fake-A-org", region_name="us-west-2")
    s3 = session.client("s3")
    s3.create_bucket(
        Bucket=WEST_2_BUCKET,
        CreateBucketConfiguration={"LocationConstraint": "us-west-2"},
    )

    session = boto3.Session(profile_name="fake-B-org", region_name="us-west-2")
    s3 = session.client("s3")
    s3.create_bucket(
        Bucket=B_BUCKET,
        CreateBucketConfiguration={"LocationConstraint": "us-west-2"},
    )


def test_s3_service():
    session = make_session("fake-A-org")
    suffix, context = get_suffix(
        "s3",
        "this parameter doesn't matter",
        "us-east-1",
        session,
    )
    assert suffix == "console.aws.amazon.com/s3/home"
    assert context.current_region == "us-east-1"
    assert context.identity["Account"] == "111111111111"


def test_s3_service_west_2():
    session = make_session("fake-A-org")
    suffix, context = get_suffix(
        "s3",
        "this parameter doesn't matter",
        "us-west-2",
        session,
    )
    assert suffix == "console.aws.amazon.com/s3/home"
    assert context.current_region == "us-west-2"
    assert context.identity["Account"] == "111111111111"


def test_s3_bucket_name():
    session = make_session("fake-A-org")
    suffix, context = get_suffix(
        EAST_1_BUCKET,
        "this parameter doesn't matter",
        "us-west-2",
        session,
    )
    arn = Arn(
        "s3",
        "",
        "111111111111",
        EAST_1_BUCKET,
    )
    assert suffix == f"console.aws.amazon.com/go/view?arn={arn.encode()}"
    assert context.current_region == "us-west-2"
    assert context.identity["Account"] == "111111111111"


def test_s3_bucket_name_missing():
    session = make_session("fake-A-org")
    suffix, context = get_suffix(
        "thisbucketdoesntexist",
        "this parameter doesn't matter",
        "us-west-2",
        session,
    )
    assert suffix == None
