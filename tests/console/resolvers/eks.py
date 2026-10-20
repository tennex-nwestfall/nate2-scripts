from nate2_scripts.console import get_suffix
from tests.console.resolvers import make_session

EKS_CONSOLE_URL = "/eks/clusters"

# --------------------------------
# Service
# --------------------------------


def test_service_eks():
    session = make_session("fake-A-org")
    suffix, context = get_suffix(
        "eks",
        "this parameter doesn't matter",
        "",
        session,
    )
    assert suffix == f"{EKS_CONSOLE_URL}"
    assert context.session.region_name == "us-east-1"
    assert context.identity["Account"] == "111111111111"
