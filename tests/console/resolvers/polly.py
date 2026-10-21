from nate2_scripts.console import get_suffix
from tests.console.resolvers import make_session

POLLY_CONSOLE_URL = "/polly/home"

# --------------------------------
# Service
# --------------------------------


def test_service_polly():
    session = make_session("fake-A-org")
    suffix, context = get_suffix(
        "polly",
        "this parameter doesn't matter",
        "",
        session,
    )
    assert suffix == f"{POLLY_CONSOLE_URL}"
    assert context.session.region_name == "us-east-1"
    assert context.identity["Account"] == "111111111111"
