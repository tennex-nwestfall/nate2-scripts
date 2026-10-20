from nate2_scripts.console import get_suffix
from tests.console.resolvers import make_session

CLOUDTRAIL_CONSOLE_URL = "/cloudtrailv2/home"

# --------------------------------
# Service
# --------------------------------


def test_service_cloudtrail():
    session = make_session("fake-A-org")
    suffix, context = get_suffix(
        "cloudtrail",
        "this parameter doesn't matter",
        "",
        session,
    )
    assert suffix == f"{CLOUDTRAIL_CONSOLE_URL}"
    assert context.session.region_name == "us-east-1"
    assert context.identity["Account"] == "111111111111"


def test_service_ct():
    session = make_session("fake-A-org")
    suffix, context = get_suffix(
        "ct",
        "this parameter doesn't matter",
        "us-west-2",
        session,
    )
    assert suffix == f"{CLOUDTRAIL_CONSOLE_URL}"
    assert context.session.region_name == "us-west-2"
    assert context.identity["Account"] == "111111111111"
