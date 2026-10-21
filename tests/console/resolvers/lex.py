from nate2_scripts.console import get_suffix
from tests.console.resolvers import make_session

LEX_CONSOLE_URL = "/lexv2/home#bots"

# --------------------------------
# Service
# --------------------------------


def test_service_lex():
    session = make_session("fake-A-org")
    suffix, context = get_suffix(
        "lex",
        "this parameter doesn't matter",
        "",
        session,
    )
    assert suffix == f"{LEX_CONSOLE_URL}"
    assert context.session.region_name == "us-east-1"
    assert context.identity["Account"] == "111111111111"
