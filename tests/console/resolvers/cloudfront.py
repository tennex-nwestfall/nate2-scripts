from nate2_scripts.console import get_suffix
from tests.console.resolvers import make_session

CLOUDFRONT_CONSOLE_URL = "/cloudfront/v4/home#/distributions"

# --------------------------------
# Service
# --------------------------------


def test_service_cloudfront():
    session = make_session("fake-A-org")
    suffix, context = get_suffix(
        "cloudfront",
        "this parameter doesn't matter",
        "",
        session,
    )
    assert suffix == f"{CLOUDFRONT_CONSOLE_URL}"
    assert context.session.region_name == "us-east-1"
    assert context.identity["Account"] == "111111111111"


def test_service_front():
    session = make_session("fake-A-org")
    suffix, context = get_suffix(
        "front",
        "this parameter doesn't matter",
        "us-west-2",
        session,
    )
    assert suffix == f"{CLOUDFRONT_CONSOLE_URL}"
    assert context.session.region_name == "us-west-2"
    assert context.identity["Account"] == "111111111111"
