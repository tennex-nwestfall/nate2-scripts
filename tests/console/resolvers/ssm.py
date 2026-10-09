from nate2_scripts.console import get_suffix
from tests.console.resolvers import make_session

# --------------------------------
# Service
# --------------------------------


def test_base_ssm():
    session = make_session("fake-A-org")
    suffix, context = get_suffix(
        "ssm",
        "this parameter doesn't matter",
        "",
        session,
    )
    assert suffix == "/systems-manager/home"
    assert context.session.region_name == "us-east-1"
    assert context.identity["Account"] == "111111111111"


def test_base_ssm_west():
    session = make_session("fake-A-org")
    suffix, context = get_suffix(
        "ssm",
        "this parameter doesn't matter",
        "us-west-2",
        session,
    )
    assert suffix == "/systems-manager/home"
    assert context.session.region_name == "us-west-2"
    assert context.identity["Account"] == "111111111111"


def test_base_parameter():
    session = make_session("fake-A-org")
    suffix, context = get_suffix(
        "parameter",
        "",
        "",
        session,
    )
    assert suffix == "/systems-manager/parameters"
    assert context.session.region_name == "us-east-1"
    assert context.identity["Account"] == "111111111111"


def test_base_ps():
    session = make_session("fake-A-org")
    suffix, context = get_suffix(
        "ps",
        "",
        "",
        session,
    )
    assert suffix == "/systems-manager/parameters"
    assert context.session.region_name == "us-east-1"
    assert context.identity["Account"] == "111111111111"


def test_base_ps_search_1():
    session = make_session("fake-A-org")
    suffix, context = get_suffix(
        "ps",
        "secret",
        "",
        session,
    )
    assert (
        suffix == "/systems-manager/parameters#list_parameter_filters=Name:%3A:secret"
    )
    assert context.session.region_name == "us-east-1"
    assert context.identity["Account"] == "111111111111"


def test_base_ps_search_2():
    session = make_session("fake-A-org")
    suffix, context = get_suffix(
        "parameter",
        "my parameter",
        "",
        session,
    )
    assert (
        suffix
        == "/systems-manager/parameters#list_parameter_filters=Name:%3A:my%20parameter"
    )
    assert context.session.region_name == "us-east-1"
    assert context.identity["Account"] == "111111111111"
