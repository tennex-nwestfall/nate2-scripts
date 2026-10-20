from nate2_scripts.console import get_suffix
from tests.console.resolvers import make_session

COGNITO_CONSOLE_URL = "/cognito/v2/idp/user-pools"

# --------------------------------
# Service
# --------------------------------


def test_service_cognito():
    session = make_session("fake-A-org")
    suffix, context = get_suffix(
        "cognito",
        "this parameter doesn't matter",
        "",
        session,
    )
    assert suffix == f"{COGNITO_CONSOLE_URL}"
    assert context.session.region_name == "us-east-1"
    assert context.identity["Account"] == "111111111111"


def test_service_cn():
    session = make_session("fake-A-org")
    suffix, context = get_suffix(
        "cn",
        "this parameter doesn't matter",
        "us-west-2",
        session,
    )
    assert suffix == f"{COGNITO_CONSOLE_URL}"
    assert context.session.region_name == "us-west-2"
    assert context.identity["Account"] == "111111111111"
