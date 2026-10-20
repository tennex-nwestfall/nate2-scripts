from nate2_scripts.console import get_suffix
from tests.console.resolvers import make_session

CLOUDHSM_CONSOLE_URL = "/cloudhsm/home#/clusters"

# --------------------------------
# Service
# --------------------------------


def test_service_cloudhsm():
    session = make_session("fake-A-org")
    suffix, context = get_suffix(
        "cloudhsm",
        "this parameter doesn't matter",
        "",
        session,
    )
    assert suffix == f"{CLOUDHSM_CONSOLE_URL}"
    assert context.session.region_name == "us-east-1"
    assert context.identity["Account"] == "111111111111"


def test_service_hsm():
    session = make_session("fake-A-org")
    suffix, context = get_suffix(
        "hsm",
        "this parameter doesn't matter",
        "us-west-2",
        session,
    )
    assert suffix == f"{CLOUDHSM_CONSOLE_URL}"
    assert context.session.region_name == "us-west-2"
    assert context.identity["Account"] == "111111111111"
