from nate2_scripts.console import get_suffix
from tests.console.resolvers import make_session

LIGHTSAIL_CONSOLE_URL = "/lightsail/webapp/home/instances"

# --------------------------------
# Service
# --------------------------------


def test_service_lightsail():
    session = make_session("fake-A-org")
    suffix, context = get_suffix(
        "lightsail",
        "this parameter doesn't matter",
        "",
        session,
    )
    assert suffix == f"{LIGHTSAIL_CONSOLE_URL}"
    assert context.session.region_name == "us-east-1"
    assert context.identity["Account"] == "111111111111"


def test_service_ls():
    session = make_session("fake-A-org")
    suffix, context = get_suffix(
        "ls",
        "this parameter doesn't matter",
        "us-west-2",
        session,
    )
    assert suffix == f"{LIGHTSAIL_CONSOLE_URL}"
    assert context.session.region_name == "us-west-2"
    assert context.identity["Account"] == "111111111111"
