from nate2_scripts.console import get_suffix
from tests.console.resolvers import make_session

COST_CONSOLE_URL = "/costmanagement/home"

# --------------------------------
# Service
# --------------------------------


def test_service_cost():
    session = make_session("fake-A-org")
    suffix, context = get_suffix(
        "cost",
        "this parameter doesn't matter",
        "us-west-2",
        session,
    )
    assert suffix == f"{COST_CONSOLE_URL}"
    # cost is only is available in the us-east-1 region
    assert context.session.region_name == "us-east-1"
    assert context.identity["Account"] == "111111111111"
