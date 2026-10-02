import boto3
import pytest

from nate2_scripts.console import get_suffix
from nate2_scripts.console.resolvers import Arn
from tests.console.resolvers import make_link, make_session

EAST_1_BUCKET = "exists-bucket"
WEST_2_BUCKET = "exists-bucket-west"
B_BUCKET = "exists-bucket-B"
KEY = "this/file/exists.txt"
KEY2 = "this/file_exists.txt"
KEY3 = "a/file.txt"


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
    s3.put_object(Bucket=WEST_2_BUCKET, Key=KEY3, Body=b"wow3")

    session = boto3.Session(profile_name="fake-B-org", region_name="us-west-2")
    s3 = session.client("s3")
    s3.create_bucket(
        Bucket=B_BUCKET,
        CreateBucketConfiguration={"LocationConstraint": "us-west-2"},
    )


# --------------------------------
# Service
# --------------------------------


def test_s3_service():
    session = make_session("fake-A-org")
    suffix, context = get_suffix(
        "s3",
        "this parameter doesn't matter",
        "",
        session,
    )
    assert suffix == "console.aws.amazon.com/s3/home"
    assert context.session.region_name == "us-east-1"
    assert context.identity["Account"] == "111111111111"


def test_s3_service_west():
    session = make_session("fake-A-org")
    suffix, context = get_suffix(
        "s3",
        "this parameter doesn't matter",
        "us-west-2",
        session,
    )
    assert suffix == "console.aws.amazon.com/s3/home"
    assert context.session.region_name == "us-west-2"
    assert context.identity["Account"] == "111111111111"


# --------------------------------
# ARN
# --------------------------------


def test_s3_arn():
    session = make_session("fake-A-org")
    arn = Arn("s3", "", "", EAST_1_BUCKET)
    suffix, context = get_suffix(
        arn.str(),
        "this parameter doesn't matter",
        "us-west-2",
        session,
    )
    assert suffix == make_link(arn)
    assert context.session.region_name == "us-east-1"
    assert context.identity["Account"] == "111111111111"


def test_s3_arn_west():
    session = make_session("fake-A-org")
    arn = Arn("s3", "", "", WEST_2_BUCKET)
    suffix, context = get_suffix(
        arn.str(),
        "this parameter doesn't matter",
        "us-east-1",
        session,
    )
    assert suffix == make_link(arn)
    assert context.session.region_name == "us-west-2"
    assert context.identity["Account"] == "111111111111"


def test_s3_arn_nonexistent():
    session = make_session("fake-A-org")
    arn = Arn("s3", "", "", "exist")
    suffix, _context = get_suffix(
        arn.str(),
        "this parameter doesn't matter",
        "us-east-1",
        session,
    )
    assert suffix == None


def test_s3_arn_file():
    session = make_session("fake-A-org")
    arn = Arn("s3", "", "", f"{EAST_1_BUCKET}/{KEY}")
    suffix, context = get_suffix(
        arn.str(),
        "this parameter doesn't matter",
        "",
        session,
    )
    assert suffix == make_link(arn)
    assert context.session.region_name == "us-east-1"
    assert context.identity["Account"] == "111111111111"


def test_s3_arn_file_nonexistent():
    session = make_session("fake-A-org")
    arn = Arn("s3", "", "", f"{EAST_1_BUCKET}/this")
    suffix, _context = get_suffix(
        arn.str(),
        "this parameter doesn't matter",
        "us-west-2",
        session,
    )
    assert suffix == None


def test_s3_arn_path():
    session = make_session("fake-A-org")
    arn = Arn("s3", "", "", f"{EAST_1_BUCKET}/this/")
    suffix, context = get_suffix(
        arn.str(),
        "this parameter doesn't matter",
        "us-west-1",
        session,
    )
    assert suffix == make_link(arn)
    assert context.session.region_name == "us-east-1"
    assert context.identity["Account"] == "111111111111"


def test_s3_arn_path_nonexistent():
    session = make_session("fake-A-org")
    arn = Arn("s3", "", "", f"{EAST_1_BUCKET}/no")
    suffix, _context = get_suffix(
        arn.str(),
        "this parameter doesn't matter",
        "us-east-1",
        session,
    )
    assert suffix == None


# --------------------------------
# Name
# --------------------------------


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
        "",
        EAST_1_BUCKET,
    )
    assert suffix == make_link(arn)
    assert context.session.region_name == "us-east-1"
    assert context.identity["Account"] == "111111111111"


def test_s3_bucket_name_missing():
    session = make_session("fake-A-org")
    suffix, _context = get_suffix(
        "thisbucketdoesntexist",
        "this parameter doesn't matter",
        "us-west-2",
        session,
    )
    assert suffix == None


# --------------------------------
# Id
# --------------------------------


def test_s3_bucket_object_exists():
    session = make_session("fake-A-org")
    suffix, _context = get_suffix(
        f"s3://{EAST_1_BUCKET}/{KEY}",
        "this parameter doesn't matter",
        "us-west-2",
        session,
    )
    arn = Arn(
        "s3",
        "",
        "",
        f"{EAST_1_BUCKET}/{KEY}",
    )
    assert suffix == make_link(arn)
    assert _context.session.region_name == "us-east-1"
    assert _context.identity["Account"] == "111111111111"


def test_s3_bucket_object_exists_west():
    session = make_session("fake-A-org")
    suffix, _context = get_suffix(
        f"s3://{WEST_2_BUCKET}/{KEY3}",
        "this parameter doesn't matter",
        "us-west-2",
        session,
    )
    arn = Arn(
        "s3",
        "",
        "",
        f"{WEST_2_BUCKET}/{KEY3}",
    )
    assert suffix == make_link(arn)
    assert _context.session.region_name == "us-west-2"
    assert _context.identity["Account"] == "111111111111"


def test_s3_bucket_object_doesnt_exist():
    session = make_session("fake-A-org")
    suffix, _context = get_suffix(
        f"s3://{EAST_1_BUCKET}/this/file",
        "this parameter doesn't matter",
        "us-west-2",
        session,
    )
    assert suffix == None


def test_s3_bucket_path_exists():
    session = make_session("fake-A-org")
    suffix, _context = get_suffix(
        f"s3://{EAST_1_BUCKET}/this/file/",
        "this parameter doesn't matter",
        "us-west-2",
        session,
    )
    arn = Arn(
        "s3",
        "",
        "",
        f"{EAST_1_BUCKET}/this/file/",
    )
    assert suffix == make_link(arn)
    assert _context.session.region_name == "us-east-1"
    assert _context.identity["Account"] == "111111111111"


def test_s3_bucket_path_exists_west():
    session = make_session("fake-A-org")
    suffix, _context = get_suffix(
        f"s3://{WEST_2_BUCKET}/a/",
        "this parameter doesn't matter",
        "us-east-1",
        session,
    )
    arn = Arn(
        "s3",
        "",
        "",
        f"{WEST_2_BUCKET}/a/",
    )
    assert suffix == make_link(arn)
    assert _context.session.region_name == "us-west-2"
    assert _context.identity["Account"] == "111111111111"


def test_s3_bucket_path_doesnt_exist():
    session = make_session("fake-A-org")
    suffix, _context = get_suffix(
        "thisbucketdoesntexist",
        "this parameter doesn't matter",
        "us-west-2",
        session,
    )
    assert suffix == None
