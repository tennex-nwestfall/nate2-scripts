import boto3
import pytest

from nate2_scripts.console import get_suffix
from nate2_scripts.console.resolvers import Arn
from tests.console.resolvers import make_link, make_session

CLOUDWATCH_CONSOLE_URL = "console.aws.amazon.com/cloudwatch/home"

GROUP1 = "/aws/lambda/function"
STREAM1 = "2024/03/14/[$LATEST]0123456789abcdef"

GROUP2 = "/aws/lambda/function2"
STREAM2 = "2025/03/14/[$LATEST]abcdef0123456789"

GROUP3 = "/aws/lambda/function3"


@pytest.fixture(autouse=True)
def cloudwatch_resources(aws_profiles):
    """Seed the moto backend (already active via the aws_profiles fixture) with
    the buckets/objects the tests check for existence."""
    session = boto3.Session(profile_name="fake-A-org", region_name="us-east-1")
    cw = session.client("logs")
    cw.create_log_group(logGroupName=GROUP1)
    cw.create_log_stream(logGroupName=GROUP1, logStreamName=STREAM1)
    cw.create_log_group(logGroupName=GROUP2)
    cw.create_log_stream(logGroupName=GROUP2, logStreamName=STREAM2)

    session = boto3.Session(profile_name="fake-A-org", region_name="us-west-2")
    cw = session.client("logs")
    cw.create_log_group(logGroupName=GROUP3)


# --------------------------------
# Service
# --------------------------------


def test_base_cw():
    session = make_session("fake-A-org")
    suffix, context = get_suffix(
        "cw",
        "this parameter doesn't matter",
        "us-east-1",
        session,
    )
    assert suffix == f"{CLOUDWATCH_CONSOLE_URL}"
    assert context.session.region_name == "us-east-1"
    assert context.identity["Account"] == "111111111111"


def test_base_cloudwatch():
    session = make_session("fake-A-org")
    suffix, context = get_suffix(
        "cloudwatch",
        "this parameter doesn't matter",
        "us-west-2",
        session,
    )
    assert suffix == f"{CLOUDWATCH_CONSOLE_URL}"
    assert context.session.region_name == "us-west-2"
    assert context.identity["Account"] == "111111111111"


def test_base_logs():
    session = make_session("fake-A-org")
    suffix, context = get_suffix(
        "logs",
        "",
        "",
        session,
    )
    assert suffix == f"{CLOUDWATCH_CONSOLE_URL}#logsV2:log-groups"
    assert context.session.region_name == "us-east-1"
    assert context.identity["Account"] == "111111111111"


def test_base_logs_search():
    session = make_session("fake-B-org")
    suffix, context = get_suffix(
        "logs",
        "123 /%+wow()@#$!\\';",
        "",
        session,
    )
    assert (
        suffix
        == f"{CLOUDWATCH_CONSOLE_URL}#logsV2:log-groups$3FlogGroupNameFilter$3D123+$252F$2525$252Bwow$2528$2529$2540$2523$2524$2521$255C$2527$253B"
    )
    assert context.region == "us-west-2"
    assert context.account == "444444444444"


# --------------------------------
# ARN
# --------------------------------


def test_logs_arn():
    session = make_session("fake-A-org")
    arn = Arn("logs", "us-east-1", "111111111111", "log-group", GROUP1, "*")
    suffix, context = get_suffix(
        arn.str(),
        "this parameter doesn't matter",
        "us-west-2",
        session,
    )
    assert suffix == make_link(arn)
    assert context.session.region_name == "us-east-1"
    assert context.identity["Account"] == "111111111111"


def test_logs_arn_west():
    session = make_session("fake-A-org")
    arn = Arn("logs", "us-west-2", "111111111111", "log-group", GROUP3, "*")
    suffix, context = get_suffix(
        arn.str(),
        "this parameter doesn't matter",
        "",
        session,
    )
    assert suffix == make_link(arn)
    assert context.session.region_name == "us-west-2"
    assert context.identity["Account"] == "111111111111"


def test_logs_arn_wrong_region():
    session = make_session("fake-A-org")
    arn = Arn("logs", "us-west-2", "111111111111", "log-group", GROUP1, "*")
    suffix, _context = get_suffix(
        arn.str(),
        "this parameter doesn't matter",
        "",
        session,
    )
    assert suffix == None


def test_logs_arn_wrong_account():
    session = make_session("fake-B-org")
    arn = Arn("logs", "us-east-1", "111111111111", "log-group", GROUP1, "*")
    suffix, context = get_suffix(
        arn.str(),
        "this parameter doesn't matter",
        "",
        session,
    )
    assert suffix == make_link(arn)
    assert context.session.region_name == "us-east-1"
    assert context.identity["Account"] == "111111111111"


# --------------------------------
# Name
# --------------------------------
