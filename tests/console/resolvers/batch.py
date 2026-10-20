from nate2_scripts.console import get_suffix
from tests.console.resolvers import make_session

BATCH_CONSOLE_URL = "/batch/home"

# --------------------------------
# Service
# --------------------------------


def test_service_batch():
    session = make_session("fake-A-org")

    suffix, context = get_suffix(
        "batch",
        "this parameter doesn't matter",
        "",
        session,
    )
    assert suffix == BATCH_CONSOLE_URL
    assert context.session.region_name == "us-east-1"
    assert context.identity["Account"] == "111111111111"


def test_service_job():
    session = make_session("fake-A-org")

    suffix, context = get_suffix(
        "job",
        "this parameter doesn't matter",
        "",
        session,
    )
    assert suffix == BATCH_CONSOLE_URL
    assert context.session.region_name == "us-east-1"
    assert context.identity["Account"] == "111111111111"


def test_service_jobs():
    session = make_session("fake-B-org")

    suffix, context = get_suffix(
        "jobs",
        "this parameter doesn't matter",
        "",
        session,
    )
    assert suffix == BATCH_CONSOLE_URL
    assert context.session.region_name == "us-west-2"
    assert context.identity["Account"] == "444444444444"
