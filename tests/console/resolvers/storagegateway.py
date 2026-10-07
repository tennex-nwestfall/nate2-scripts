from nate2_scripts.console import get_suffix
from tests.console.resolvers import make_session

STORAGEGATEWAY_CONSOLE_URL = "/storagegateway/home#/gateways"

# --------------------------------
# Service
# --------------------------------


def test_base_storagegateway():
    session = make_session("fake-A-org")
    suffix, context = get_suffix(
        "storagegateway",
        "this parameter doesn't matter",
        "",
        session,
    )
    assert suffix == f"{STORAGEGATEWAY_CONSOLE_URL}"
    assert context.session.region_name == "us-east-1"
    assert context.identity["Account"] == "111111111111"


def test_base_sgw():
    session = make_session("fake-A-org")
    suffix, context = get_suffix(
        "sgw",
        "this parameter doesn't matter",
        "us-west-2",
        session,
    )
    assert suffix == f"{STORAGEGATEWAY_CONSOLE_URL}"
    assert context.session.region_name == "us-west-2"
    assert context.identity["Account"] == "111111111111"
