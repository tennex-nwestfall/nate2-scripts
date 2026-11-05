from nate2_scripts.console import get_suffix
from tests.console.resolvers import make_session

DATASYNC_CONSOLE_URL = "/datasync/home#/tasks"

# --------------------------------
# Service
# --------------------------------


def test_service_datasync():
    session = make_session("fake-A-org")
    suffix, context = get_suffix(
        "datasync",
        "this parameter doesn't matter",
        "",
        session,
    )
    assert suffix == f"{DATASYNC_CONSOLE_URL}"
    assert context.session.region_name == "us-east-1"
    assert context.identity["Account"] == "111111111111"


def test_service_ds():
    session = make_session("fake-A-org")
    suffix, context = get_suffix(
        "ds",
        "this parameter doesn't matter",
        "us-west-2",
        session,
    )
    assert suffix == f"{DATASYNC_CONSOLE_URL}"
    assert context.session.region_name == "us-west-2"
    assert context.identity["Account"] == "111111111111"
