from nate2_scripts.console import get_suffix
from tests.console.resolvers import make_session

SCHEDULER_CONSOLE_URL = "/scheduler/home#schedules"

# --------------------------------
# Service
# --------------------------------


def test_service_scheduler():
    session = make_session("fake-A-org")
    suffix, context = get_suffix(
        "scheduler",
        "this parameter doesn't matter",
        "",
        session,
    )
    assert suffix == f"{SCHEDULER_CONSOLE_URL}"
    assert context.session.region_name == "us-east-1"
    assert context.identity["Account"] == "111111111111"


def test_service_sch():
    session = make_session("fake-A-org")
    suffix, context = get_suffix(
        "sch",
        "this parameter doesn't matter",
        "us-west-2",
        session,
    )
    assert suffix == f"{SCHEDULER_CONSOLE_URL}"
    assert context.session.region_name == "us-west-2"
    assert context.identity["Account"] == "111111111111"
