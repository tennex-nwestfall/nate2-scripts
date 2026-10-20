import io
import json
import zipfile

import boto3
import pytest

from nate2_scripts.console import get_suffix
from nate2_scripts.console.resolvers import Arn
from tests.console.resolvers import make_link, make_session

ACCOUNT = "111111111111"
EAST_1_FUNCTION = "exists-function"
WEST_2_FUNCTION = "exists-function-west"


def _zip_bytes() -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as zf:
        zf.writestr("index.py", "def handler(event, context):\n    return event\n")
    return buffer.getvalue()


def _create_function(session: boto3.Session, name: str, role_arn: str) -> None:
    session.client("lambda").create_function(
        Code={"ZipFile": _zip_bytes()},
        FunctionName=name,
        Handler="index.handler",
        Role=role_arn,
        Runtime="python3.12",
    )


@pytest.fixture(autouse=True, scope="module")
def lambda_resources():
    """Seed the moto backend (already active via the aws_profiles fixture) with
    one function per region. moto requires the execution role to exist."""
    session = boto3.Session(profile_name="fake-A-org", region_name="us-east-1")
    role_arn = session.client("iam").create_role(
        AssumeRolePolicyDocument=json.dumps(
            {
                "Statement": [
                    {
                        "Action": "sts:AssumeRole",
                        "Effect": "Allow",
                        "Principal": {"Service": "lambda.amazonaws.com"},
                    }
                ],
                "Version": "2012-10-17",
            }
        ),
        RoleName="exists-lambda-role",
    )["Role"]["Arn"]
    _create_function(session, EAST_1_FUNCTION, role_arn)

    session = boto3.Session(profile_name="fake-A-org", region_name="us-west-2")
    _create_function(session, WEST_2_FUNCTION, role_arn)


# --------------------------------
# Service
# --------------------------------


def test_lambda_service():
    session = make_session("fake-A-org")
    suffix, context = get_suffix(
        "lambda",
        "",
        "",
        session,
    )
    assert suffix == "/lambda/home"
    assert context.session.region_name == "us-east-1"
    assert context.identity["Account"] == ACCOUNT


def test_lambda_service_west():
    session = make_session("fake-A-org")
    suffix, context = get_suffix(
        "lambda",
        "",
        "us-west-2",
        session,
    )
    assert suffix == "/lambda/home"
    assert context.session.region_name == "us-west-2"
    assert context.identity["Account"] == ACCOUNT


def test_lambda_service_search():
    session = make_session("fake-A-org")
    suffix, context = get_suffix(
        "lambda",
        "my function",
        "us-west-2",
        session,
    )
    assert suffix == "/lambda/home#functions?o0=:&v0=my%20function"
    assert context.session.region_name == "us-west-2"
    assert context.identity["Account"] == ACCOUNT


# --------------------------------
# ARN
# --------------------------------


def test_lambda_arn():
    session = make_session("fake-A-org")
    arn = Arn("lambda", "us-east-1", ACCOUNT, f"function:{EAST_1_FUNCTION}")
    suffix, context = get_suffix(
        arn.str(),
        "this parameter doesn't matter",
        "us-west-2",
        session,
    )
    assert suffix == make_link(arn)
    assert context.session.region_name == "us-east-1"
    assert context.identity["Account"] == ACCOUNT


def test_lambda_arn_west():
    session = make_session("fake-A-org")
    arn = Arn("lambda", "us-west-2", ACCOUNT, f"function:{WEST_2_FUNCTION}")
    suffix, context = get_suffix(
        arn.str(),
        "this parameter doesn't matter",
        "us-east-1",
        session,
    )
    assert suffix == make_link(arn)
    assert context.session.region_name == "us-west-2"
    assert context.identity["Account"] == ACCOUNT


def test_lambda_arn_nonexistent():
    session = make_session("fake-A-org")
    arn = Arn("lambda", "us-east-1", ACCOUNT, "function:thisfunctiondoesntexist")
    suffix, _context = get_suffix(
        arn.str(),
        "this parameter doesn't matter",
        "us-east-1",
        session,
    )
    assert suffix == None


def test_lambda_arn_wrong_region():
    session = make_session("fake-A-org")
    arn = Arn("lambda", "us-west-2", ACCOUNT, f"function:{EAST_1_FUNCTION}")
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


def test_lambda_function_name():
    session = make_session("fake-A-org")
    suffix, context = get_suffix(
        EAST_1_FUNCTION,
        "this parameter doesn't matter",
        "us-west-2",
        session,
    )
    arn = Arn("lambda", "us-east-1", ACCOUNT, f"function:{EAST_1_FUNCTION}")
    assert suffix == make_link(arn)
    assert context.session.region_name == "us-east-1"
    assert context.identity["Account"] == ACCOUNT


def test_lambda_function_name_west():
    session = make_session("fake-A-org")
    suffix, context = get_suffix(
        WEST_2_FUNCTION,
        "this parameter doesn't matter",
        "us-east-1",
        session,
    )
    arn = Arn("lambda", "us-west-2", ACCOUNT, f"function:{WEST_2_FUNCTION}")
    assert suffix == make_link(arn)
    assert context.session.region_name == "us-west-2"
    assert context.identity["Account"] == ACCOUNT


def test_lambda_function_name_missing():
    session = make_session("fake-A-org")
    suffix, _context = get_suffix(
        "thisfunctiondoesntexist",
        "this parameter doesn't matter",
        "us-west-2",
        session,
    )
    assert suffix == None
