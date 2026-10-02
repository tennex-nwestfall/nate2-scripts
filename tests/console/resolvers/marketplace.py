import pytest

from nate2_scripts.console import get_suffix
from tests.console.resolvers import make_session

MARKETPLACE_CONSOLE_URL = "console.aws.amazon.com/marketplace/search"

# --------------------------------
# Service
# --------------------------------


def test_base_market():
    session = make_session("fake-A-org")
    suffix, context = get_suffix(
        "market",
        "",
        "us-east-1",
        session,
    )
    assert suffix == f"{MARKETPLACE_CONSOLE_URL}"
    assert context.session.region_name == "us-east-1"
    assert context.identity["Account"] == "111111111111"


def test_tennex_service():
    session = make_session("fake-A-org")
    suffix, context = get_suffix(
        "tennex",
        "this parameter doesn't matter",
        "us-west-2",
        session,
    )
    assert suffix == f"{MARKETPLACE_CONSOLE_URL}?text=tennex"
    assert context.session.region_name == "us-east-1"
    assert context.identity["Account"] == "111111111111"


def test_market_search():
    session = make_session("fake-A-org")
    suffix, context = get_suffix(
        "market",
        "boltz",
        "us-west-2",
        session,
    )
    assert suffix == f"{MARKETPLACE_CONSOLE_URL}?text=boltz"
    assert context.session.region_name == "us-east-1"
    assert context.identity["Account"] == "111111111111"


def test_marketplace_search():
    session = make_session("fake-A-org")
    suffix, context = get_suffix(
        "marketplace",
        "my cool product?",
        "us-east-1",
        session,
    )
    assert suffix == f"{MARKETPLACE_CONSOLE_URL}?text=my+cool+product%3F"
    assert context.session.region_name == "us-east-1"
    assert context.identity["Account"] == "111111111111"
