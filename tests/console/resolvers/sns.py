from nate2_scripts.console import get_suffix
from tests.console.resolvers import make_session

SNS_CONSOLE_URL = "/sns/v3/home"

# --------------------------------
# Service
# --------------------------------


def test_service_sns():
    session = make_session("fake-A-org")
    suffix, context = get_suffix(
        "sns",
        "this parameter doesn't matter",
        "",
        session,
    )
    assert suffix == f"{SNS_CONSOLE_URL}"
    assert context.session.region_name == "us-east-1"
    assert context.identity["Account"] == "111111111111"
