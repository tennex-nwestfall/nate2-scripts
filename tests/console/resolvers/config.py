from nate2_scripts.console import get_suffix
from tests.console.resolvers import make_session

CONFIG_CONSOLE_URL = "/config#/dashboard"

# --------------------------------
# Service
# --------------------------------


def test_service_config():
    session = make_session("fake-A-org")
    suffix, context = get_suffix(
        "config",
        "this parameter doesn't matter",
        "",
        session,
    )
    assert suffix == f"{CONFIG_CONSOLE_URL}"
    assert context.session.region_name == "us-east-1"
    assert context.identity["Account"] == "111111111111"


def test_service_cfg():
    session = make_session("fake-A-org")
    suffix, context = get_suffix(
        "cfg",
        "this parameter doesn't matter",
        "us-west-2",
        session,
    )
    assert suffix == f"{CONFIG_CONSOLE_URL}"
    assert context.session.region_name == "us-west-2"
    assert context.identity["Account"] == "111111111111"
