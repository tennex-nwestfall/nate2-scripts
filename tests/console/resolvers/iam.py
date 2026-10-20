from nate2_scripts.console import get_suffix
from tests.console.resolvers import make_session

IAM_CONSOLE_URL = "/iam#/home"

# --------------------------------
# Service
# --------------------------------


def test_service_iam():
    session = make_session("fake-A-org")
    suffix, context = get_suffix(
        "iam",
        "this parameter doesn't matter",
        "",
        session,
    )
    assert suffix == f"{IAM_CONSOLE_URL}"
    assert context.session.region_name == "us-east-1"
    assert context.identity["Account"] == "111111111111"
