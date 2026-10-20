from nate2_scripts.console import get_suffix
from tests.console.resolvers import make_session

ELB_CONSOLE_URL = "/ec2/home#LoadBalancers:"

# --------------------------------
# Service
# --------------------------------


def test_service_elb():
    session = make_session("fake-A-org")
    suffix, context = get_suffix(
        "elb",
        "this parameter doesn't matter",
        "",
        session,
    )
    assert suffix == f"{ELB_CONSOLE_URL}"
    assert context.session.region_name == "us-east-1"
    assert context.identity["Account"] == "111111111111"


def test_service_alb():
    session = make_session("fake-A-org")
    suffix, context = get_suffix(
        "alb",
        "this parameter doesn't matter",
        "",
        session,
    )
    assert suffix == f"{ELB_CONSOLE_URL}"
    assert context.session.region_name == "us-east-1"
    assert context.identity["Account"] == "111111111111"
