from nate2_scripts.console import get_suffix
from tests.console.resolvers import make_session

CONTROLTOWER_CONSOLE_URL = "/controltower/home/landing"

# --------------------------------
# Service
# --------------------------------


def test_service_controltower():
    session = make_session("fake-A-org")
    suffix, context = get_suffix(
        "controltower",
        "this parameter doesn't matter",
        "",
        session,
    )
    assert suffix == f"{CONTROLTOWER_CONSOLE_URL}"
    assert context.session.region_name == "us-east-1"
    assert context.identity["Account"] == "111111111111"
