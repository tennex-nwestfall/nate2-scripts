from nate2_scripts.console import get_suffix
from tests.console.resolvers import make_session

ROUTE53_CONSOLE_URL = "/route53/v2/home"

# --------------------------------
# Service
# --------------------------------


def test_base_53():
    session = make_session("fake-A-org")
    suffix, context = get_suffix(
        "53",
        "this parameter doesn't matter",
        "us-east-1",
        session,
    )
    assert suffix == f"{ROUTE53_CONSOLE_URL}"
    assert context.session.region_name == "us-east-1"
    assert context.identity["Account"] == "111111111111"


def test_base_route53():
    session = make_session("fake-A-org")
    suffix, context = get_suffix(
        "route53",
        "this parameter doesn't matter",
        "us-east-1",
        session,
    )
    assert suffix == f"{ROUTE53_CONSOLE_URL}"
    assert context.session.region_name == "us-east-1"
    assert context.identity["Account"] == "111111111111"
