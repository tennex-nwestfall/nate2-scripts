import json

import boto3
import pytest

from nate2_scripts.console import get_suffix
from nate2_scripts.console.resolvers import Arn
from tests.console.resolvers import make_link, make_session

ACCOUNT = "111111111111"
CLOUDFORMATION_CONSOLE_URL = "/cloudformation/home#/stacks"
EAST_1_STACK_NAME = "exists-stack"
WEST_2_STACK_NAME = "exists-stack-west"

TEMPLATE_BODY = json.dumps(
    {
        "AWSTemplateFormatVersion": "2010-09-09",
        "Resources": {"Topic": {"Type": "AWS::SNS::Topic"}},
    }
)


def _create_stack(region: str, name: str) -> str:
    session = boto3.Session(profile_name="fake-A-org", region_name=region)
    cloudformation = session.client("cloudformation")
    return cloudformation.create_stack(StackName=name, TemplateBody=TEMPLATE_BODY)[
        "StackId"
    ]


@pytest.fixture(autouse=True, scope="module")
def cloudformation_stacks() -> dict[str, str]:
    """Seed the moto backend (already active via the aws_profiles fixture) with
    one stack in us-east-1 and one in us-west-2. moto generates the stack ids
    (which are full ARNs), so they are returned keyed by region."""
    return {
        "us-east-1": _create_stack("us-east-1", EAST_1_STACK_NAME),
        "us-west-2": _create_stack("us-west-2", WEST_2_STACK_NAME),
    }


# --------------------------------
# Service
# --------------------------------


def test_cloudformation_service():
    session = make_session("fake-A-org")
    suffix, context = get_suffix(
        "cloudformation",
        "",
        "",
        session,
    )
    assert suffix == CLOUDFORMATION_CONSOLE_URL
    assert context.session.region_name == "us-east-1"
    assert context.identity["Account"] == ACCOUNT


def test_cloudformation_service_cf_west():
    session = make_session("fake-A-org")
    suffix, context = get_suffix(
        "cf",
        "",
        "us-west-2",
        session,
    )
    assert suffix == CLOUDFORMATION_CONSOLE_URL
    assert context.session.region_name == "us-west-2"
    assert context.identity["Account"] == ACCOUNT


def test_cloudformation_service_search():
    session = make_session("fake-A-org")
    suffix, context = get_suffix(
        "cf",
        "my cool stack",
        "",
        session,
    )
    assert (
        suffix
        == f"{CLOUDFORMATION_CONSOLE_URL}?filteringText=my+cool+stack&filteringStatus=active&viewNested=true"
    )
    assert context.session.region_name == "us-east-1"
    assert context.identity["Account"] == ACCOUNT


# --------------------------------
# Name
# --------------------------------


def test_cloudformation_stack_name(cloudformation_stacks):
    session = make_session("fake-A-org")
    suffix, context = get_suffix(
        EAST_1_STACK_NAME,
        "this parameter doesn't matter",
        "us-west-2",
        session,
    )
    arn = Arn.try_parse(cloudformation_stacks["us-east-1"])
    assert arn is not None
    assert suffix == make_link(arn)
    assert context.session.region_name == "us-east-1"
    assert context.identity["Account"] == ACCOUNT


def test_cloudformation_stack_name_west(cloudformation_stacks):
    session = make_session("fake-A-org")
    suffix, context = get_suffix(
        WEST_2_STACK_NAME,
        "this parameter doesn't matter",
        "us-east-1",
        session,
    )
    arn = Arn.try_parse(cloudformation_stacks["us-west-2"])
    assert arn is not None
    assert suffix == make_link(arn)
    assert context.session.region_name == "us-west-2"
    assert context.identity["Account"] == ACCOUNT


def test_cloudformation_stack_name_missing():
    session = make_session("fake-A-org")
    suffix, _context = get_suffix(
        "thisstackdoesntexist",
        "this parameter doesn't matter",
        "us-west-2",
        session,
    )
    assert suffix == None
