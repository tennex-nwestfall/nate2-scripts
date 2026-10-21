from nate2_scripts.console import get_suffix
from tests.console.resolvers import make_session

SUPPORT_CONSOLE_URL = "/support/home#/"

# --------------------------------
# Service
# --------------------------------


def test_service_support():
    session = make_session("fake-A-org")
    suffix, context = get_suffix(
        "support",
        "",
        "us-east-1",
        session,
    )
    assert suffix == f"{SUPPORT_CONSOLE_URL}"
    # The region should be set to "support" for the support console URL
    assert context.session.region_name == "support"
    assert context.identity["Account"] == "111111111111"


def test_service_support_west():
    session = make_session("fake-A-org")
    suffix, context = get_suffix(
        "support",
        "",
        "us-west-2",
        session,
    )
    assert suffix == f"{SUPPORT_CONSOLE_URL}"
    # The region should be set to "support" for the support console URL
    assert context.session.region_name == "support"
    assert context.identity["Account"] == "111111111111"
