from nate2_scripts.console import get_suffix
from tests.console.resolvers import make_session

STEPFUNCTIONS_CONSOLE_URL = "/states/home#/statemachines"

# --------------------------------
# Service
# --------------------------------


def test_base_step():
    session = make_session("fake-A-org")
    suffix, context = get_suffix(
        "step",
        "this parameter doesn't matter",
        "",
        session,
    )
    assert suffix == f"{STEPFUNCTIONS_CONSOLE_URL}"
    assert context.session.region_name == "us-east-1"
    assert context.identity["Account"] == "111111111111"
