from nate2_scripts.console import get_suffix
from tests.console.resolvers import make_session

APIGATEWAY_CONSOLE_URL = "/apigateway/main/apis"

# --------------------------------
# Service
# --------------------------------


def test_service_apigateway():
    session = make_session("fake-A-org")
    suffix, context = get_suffix(
        "apigateway",
        "this parameter doesn't matter",
        "",
        session,
    )
    assert suffix == f"{APIGATEWAY_CONSOLE_URL}"
    assert context.session.region_name == "us-east-1"
    assert context.identity["Account"] == "111111111111"


def test_service_api():
    session = make_session("fake-A-org")
    suffix, context = get_suffix(
        "api",
        "this parameter doesn't matter",
        "",
        session,
    )
    assert suffix == f"{APIGATEWAY_CONSOLE_URL}"
    assert context.session.region_name == "us-east-1"
    assert context.identity["Account"] == "111111111111"
