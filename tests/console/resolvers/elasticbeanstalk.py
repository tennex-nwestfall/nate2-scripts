from nate2_scripts.console import get_suffix
from tests.console.resolvers import make_session

ELASTICBEANSTALK_CONSOLE_URL = "/elasticbeanstalk/applications"

# --------------------------------
# Service
# --------------------------------


def test_service_elasticbeanstalk():
    session = make_session("fake-A-org")
    suffix, context = get_suffix(
        "elasticbeanstalk",
        "this parameter doesn't matter",
        "",
        session,
    )
    assert suffix == f"{ELASTICBEANSTALK_CONSOLE_URL}"
    assert context.session.region_name == "us-east-1"
    assert context.identity["Account"] == "111111111111"


def test_service_bean():
    session = make_session("fake-A-org")
    suffix, context = get_suffix(
        "bean",
        "this parameter doesn't matter",
        "us-west-2",
        session,
    )
    assert suffix == f"{ELASTICBEANSTALK_CONSOLE_URL}"
    assert context.session.region_name == "us-west-2"
    assert context.identity["Account"] == "111111111111"
