from nate2_scripts.console import get_suffix
from tests.console.resolvers import make_session

ECR_CONSOLE_URL = "/ecr/private-registry/repositories"

# --------------------------------
# Service
# --------------------------------


def test_service_ecr():
    session = make_session("fake-A-org")
    suffix, context = get_suffix(
        "ecr",
        "this parameter doesn't matter",
        "",
        session,
    )
    assert suffix == f"{ECR_CONSOLE_URL}"
    assert context.session.region_name == "us-east-1"
    assert context.identity["Account"] == "111111111111"


def test_service_docker():
    session = make_session("fake-A-org")
    suffix, context = get_suffix(
        "docker",
        "this parameter doesn't matter",
        "us-west-2",
        session,
    )
    assert suffix == f"{ECR_CONSOLE_URL}"
    assert context.session.region_name == "us-west-2"
    assert context.identity["Account"] == "111111111111"
