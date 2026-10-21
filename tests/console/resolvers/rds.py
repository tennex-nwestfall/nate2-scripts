from nate2_scripts.console import get_suffix
from tests.console.resolvers import make_session

RDS_CONSOLE_URL = "/rds"

# --------------------------------
# Service
# --------------------------------


def test_service_rds():
    session = make_session("fake-A-org")
    suffix, context = get_suffix(
        "rds",
        "this parameter doesn't matter",
        "",
        session,
    )
    assert suffix == f"{RDS_CONSOLE_URL}"
    assert context.session.region_name == "us-east-1"
    assert context.identity["Account"] == "111111111111"
