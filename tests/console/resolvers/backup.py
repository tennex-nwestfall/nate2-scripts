from nate2_scripts.console import get_suffix
from tests.console.resolvers import make_session

BACKUP_CONSOLE_URL = "/backup/home#/dashboard/activity/backup/"

# --------------------------------
# Service
# --------------------------------


def test_service_backup():
    session = make_session("fake-A-org")

    suffix, context = get_suffix(
        "backup",
        "this parameter doesn't matter",
        "",
        session,
    )
    assert suffix == BACKUP_CONSOLE_URL
    assert context.session.region_name == "us-east-1"
    assert context.identity["Account"] == "111111111111"


def test_service_bp():
    session = make_session("fake-A-org")

    suffix, context = get_suffix(
        "bp",
        "this parameter doesn't matter",
        "",
        session,
    )
    assert suffix == BACKUP_CONSOLE_URL
    assert context.session.region_name == "us-east-1"
    assert context.identity["Account"] == "111111111111"
