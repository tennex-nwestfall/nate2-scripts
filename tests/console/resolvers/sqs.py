from nate2_scripts.console import get_suffix
from tests.console.resolvers import make_session

SQS_CONSOLE_URL = "/sqs/v3/home"

# --------------------------------
# Service
# --------------------------------


def test_service_sqs():
    session = make_session("fake-A-org")
    suffix, context = get_suffix(
        "sqs",
        "this parameter doesn't matter",
        "",
        session,
    )
    assert suffix == f"{SQS_CONSOLE_URL}"
    assert context.session.region_name == "us-east-1"
    assert context.identity["Account"] == "111111111111"
