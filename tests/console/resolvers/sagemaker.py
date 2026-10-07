from nate2_scripts.console import get_suffix
from tests.console.resolvers import make_session

SAGEMAKER_CONSOLE_URL = "/sagemaker/home#/dashboard"

# --------------------------------
# Service
# --------------------------------


def test_base_sagemaker():
    session = make_session("fake-A-org")
    suffix, context = get_suffix(
        "sagemaker",
        "this parameter doesn't matter",
        "",
        session,
    )
    assert suffix == f"{SAGEMAKER_CONSOLE_URL}"
    assert context.session.region_name == "us-east-1"
    assert context.identity["Account"] == "111111111111"


def test_base_sage():
    session = make_session("fake-A-org")
    suffix, context = get_suffix(
        "sage",
        "this parameter doesn't matter",
        "us-west-2",
        session,
    )
    assert suffix == f"{SAGEMAKER_CONSOLE_URL}"
    assert context.session.region_name == "us-west-2"
    assert context.identity["Account"] == "111111111111"
