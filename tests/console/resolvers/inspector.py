from nate2_scripts.console import get_suffix
from tests.console.resolvers import make_session

INSPECTOR_CONSOLE_URL = "/inspector/v2/home#/dashboard"

# --------------------------------
# Service
# --------------------------------


def test_service_inspector():
    session = make_session("fake-A-org")
    suffix, context = get_suffix(
        "inspector",
        "this parameter doesn't matter",
        "",
        session,
    )
    assert suffix == f"{INSPECTOR_CONSOLE_URL}"
    assert context.session.region_name == "us-east-1"
    assert context.identity["Account"] == "111111111111"
