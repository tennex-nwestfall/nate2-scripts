from nate2_scripts.console import get_suffix
from tests.console.resolvers import make_session

DYNAMO_CONSOLE_URL = "/dynamodbv2/home#tables"

# --------------------------------
# Service
# --------------------------------


def test_service_dynamodb():
    session = make_session("fake-A-org")
    suffix, context = get_suffix(
        "dynamodb",
        "this parameter doesn't matter",
        "",
        session,
    )
    assert suffix == f"{DYNAMO_CONSOLE_URL}"
    assert context.session.region_name == "us-east-1"
    assert context.identity["Account"] == "111111111111"


def test_service_dynamo():
    session = make_session("fake-A-org")
    suffix, context = get_suffix(
        "dynamo",
        "this parameter doesn't matter",
        "us-west-2",
        session,
    )
    assert suffix == f"{DYNAMO_CONSOLE_URL}"
    assert context.session.region_name == "us-west-2"
    assert context.identity["Account"] == "111111111111"


def test_service_dyn():
    session = make_session("fake-B-org")
    suffix, context = get_suffix(
        "dyn",
        "this parameter doesn't matter",
        "",
        session,
    )
    assert suffix == f"{DYNAMO_CONSOLE_URL}"
    assert context.session.region_name == "us-west-2"
    assert context.identity["Account"] == "444444444444"
