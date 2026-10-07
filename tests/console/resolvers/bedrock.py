from nate2_scripts.console import get_suffix
from tests.console.resolvers import make_session

BEDROCK_CONSOLE_URL = "/bedrock/"

# --------------------------------
# Service
# --------------------------------


def test_service_br():
    session = make_session("fake-A-org")

    suffix, context = get_suffix(
        "br",
        "this parameter doesn't matter",
        "",
        session,
    )
    assert suffix == BEDROCK_CONSOLE_URL
    assert context.session.region_name == "us-east-1"
    assert context.identity["Account"] == "111111111111"


def test_service_bedrock():
    session = make_session("fake-A-org")

    suffix, context = get_suffix(
        "bedrock",
        "this parameter doesn't matter",
        "",
        session,
    )
    assert suffix == BEDROCK_CONSOLE_URL
    assert context.session.region_name == "us-east-1"
    assert context.identity["Account"] == "111111111111"
