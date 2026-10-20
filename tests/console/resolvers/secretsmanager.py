from nate2_scripts.console import get_suffix
from tests.console.resolvers import make_session

SECRETSMANAGER_CONSOLE_URL = "/secretsmanager/listsecrets"

# --------------------------------
# Service
# --------------------------------


def test_service_secretsmanager():
    session = make_session("fake-A-org")
    suffix, context = get_suffix(
        "secretsmanager",
        "this parameter doesn't matter",
        "",
        session,
    )
    assert suffix == f"{SECRETSMANAGER_CONSOLE_URL}"
    assert context.session.region_name == "us-east-1"
    assert context.identity["Account"] == "111111111111"


def test_service_secretmanager():
    session = make_session("fake-A-org")
    suffix, context = get_suffix(
        "secretmanager",
        "this parameter doesn't matter",
        "us-west-2",
        session,
    )
    assert suffix == f"{SECRETSMANAGER_CONSOLE_URL}"
    assert context.session.region_name == "us-west-2"
    assert context.identity["Account"] == "111111111111"


def test_service_sm():
    session = make_session("fake-B-org")
    suffix, context = get_suffix(
        "sm",
        "this parameter doesn't matter",
        "",
        session,
    )
    assert suffix == f"{SECRETSMANAGER_CONSOLE_URL}"
    assert context.session.region_name == "us-west-2"
    assert context.identity["Account"] == "444444444444"
