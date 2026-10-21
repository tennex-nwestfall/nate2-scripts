from nate2_scripts.console import get_suffix
from tests.console.resolvers import make_session

GUARDDUTY_CONSOLE_URL = "/guardduty/home#/summary"

# --------------------------------
# Service
# --------------------------------


def test_service_guardduty():
    session = make_session("fake-A-org")
    suffix, context = get_suffix(
        "guardduty",
        "this parameter doesn't matter",
        "",
        session,
    )
    assert suffix == f"{GUARDDUTY_CONSOLE_URL}"
    assert context.session.region_name == "us-east-1"
    assert context.identity["Account"] == "111111111111"


def test_service_guard():
    session = make_session("fake-A-org")
    suffix, context = get_suffix(
        "guard",
        "this parameter doesn't matter",
        "",
        session,
    )
    assert suffix == f"{GUARDDUTY_CONSOLE_URL}"
    assert context.session.region_name == "us-east-1"
    assert context.identity["Account"] == "111111111111"
