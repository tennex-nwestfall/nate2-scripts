from nate2_scripts.console import get_suffix
from tests.console.resolvers import make_session

ARTIFACT_CONSOLE_URL = "/artifact/v2/home"

# --------------------------------
# Service
# --------------------------------


def test_service_artifact():
    session = make_session("fake-A-org")
    suffix, context = get_suffix(
        "artifact",
        "this parameter doesn't matter",
        "",
        session,
    )
    assert suffix == f"{ARTIFACT_CONSOLE_URL}"
    assert context.session.region_name == "us-east-1"
    assert context.identity["Account"] == "111111111111"
