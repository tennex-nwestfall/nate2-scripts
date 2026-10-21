from nate2_scripts.console import get_suffix
from tests.console.resolvers import make_session

GLUE_CONSOLE_URL = "/gluestudio/home#/jobs"

# --------------------------------
# Service
# --------------------------------


def test_service_glue():
    session = make_session("fake-A-org")
    suffix, context = get_suffix(
        "glue",
        "this parameter doesn't matter",
        "",
        session,
    )
    assert suffix == f"{GLUE_CONSOLE_URL}"
    assert context.session.region_name == "us-east-1"
    assert context.identity["Account"] == "111111111111"
