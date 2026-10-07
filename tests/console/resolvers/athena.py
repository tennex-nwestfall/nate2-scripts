from nate2_scripts.console import get_suffix
from tests.console.resolvers import make_session

ATHENA_CONSOLE_URL = "/athena/home#/query-editor"

# --------------------------------
# Service
# --------------------------------


def test_base_athena():
    session = make_session("fake-A-org")
    suffix, context = get_suffix(
        "athena",
        "this parameter doesn't matter",
        "",
        session,
    )
    assert suffix == f"{ATHENA_CONSOLE_URL}"
    assert context.session.region_name == "us-east-1"
    assert context.identity["Account"] == "111111111111"


def test_base_athena_west():
    session = make_session("fake-A-org")
    suffix, context = get_suffix(
        "athena",
        "this parameter doesn't matter",
        "us-west-2",
        session,
    )
    assert suffix == f"{ATHENA_CONSOLE_URL}"
    assert context.session.region_name == "us-west-2"
    assert context.identity["Account"] == "111111111111"
