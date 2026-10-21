import pytest

from nate2_scripts.console import get_suffix
from tests.console.resolvers import make_session

VPC_CONSOLE_URL = "/vpcconsole/home"

# --------------------------------
# Service
# --------------------------------


@pytest.mark.parametrize(
    ("service", "expected"),
    [
        ("vpc", f"{VPC_CONSOLE_URL}"),
        ("subnet", f"{VPC_CONSOLE_URL}#subnets:"),
        ("acl", f"{VPC_CONSOLE_URL}#acls:"),
        ("nacl", f"{VPC_CONSOLE_URL}#acls:"),
        ("elasticip", f"{VPC_CONSOLE_URL}#Addresses:"),
        ("eni", f"{VPC_CONSOLE_URL}#Addresses:"),
        ("routetable", f"{VPC_CONSOLE_URL}#RouteTables:"),
        ("routes", f"{VPC_CONSOLE_URL}#RouteTables:"),
        ("internetgateway", f"{VPC_CONSOLE_URL}#igws:"),
        ("internet", f"{VPC_CONSOLE_URL}#igws:"),
        ("igw", f"{VPC_CONSOLE_URL}#igws:"),
        ("nat", f"{VPC_CONSOLE_URL}#NatGateways:"),
        ("endpoints", f"{VPC_CONSOLE_URL}#Endpoints:"),
        ("end", f"{VPC_CONSOLE_URL}#Endpoints:"),
        ("transitgateway", f"{VPC_CONSOLE_URL}#TransitGateways:"),
        ("transit", f"{VPC_CONSOLE_URL}#TransitGateways:"),
        ("tgw", f"{VPC_CONSOLE_URL}#TransitGateways:"),
    ],
)
def test_service_vpc(service, expected):
    session = make_session("fake-A-org")
    suffix, context = get_suffix(
        service,
        "this parameter doesn't matter",
        "",
        session,
    )
    assert suffix == expected
    assert context.session.region_name == "us-east-1"
    assert context.identity["Account"] == "111111111111"


def test_service_vpc_west():
    session = make_session("fake-A-org")
    suffix, context = get_suffix(
        "vpc",
        "this parameter doesn't matter",
        "us-west-2",
        session,
    )
    assert suffix == f"{VPC_CONSOLE_URL}"
    assert context.session.region_name == "us-west-2"
    assert context.identity["Account"] == "111111111111"
