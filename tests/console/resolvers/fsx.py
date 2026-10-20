from nate2_scripts.console import get_suffix
from tests.console.resolvers import make_session

FSX_CONSOLE_URL = "/fsx#file-systems"

# --------------------------------
# Service
# --------------------------------


def test_service_fsx():
    session = make_session("fake-A-org")
    suffix, context = get_suffix(
        "fsx",
        "this parameter doesn't matter",
        "",
        session,
    )
    assert suffix == f"{FSX_CONSOLE_URL}"
    assert context.session.region_name == "us-east-1"
    assert context.identity["Account"] == "111111111111"
