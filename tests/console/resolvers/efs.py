from nate2_scripts.console import get_suffix
from tests.console.resolvers import make_session

EFS_CONSOLE_URL = "/efs/home#/file-system"

# --------------------------------
# Service
# --------------------------------


def test_service_efs():
    session = make_session("fake-A-org")
    suffix, context = get_suffix(
        "efs",
        "this parameter doesn't matter",
        "",
        session,
    )
    assert suffix == f"{EFS_CONSOLE_URL}"
    assert context.session.region_name == "us-east-1"
    assert context.identity["Account"] == "111111111111"
