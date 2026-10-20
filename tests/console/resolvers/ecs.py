from nate2_scripts.console import get_suffix
from tests.console.resolvers import make_session

ECS_CONSOLE_URL = "/ecs/v2/"

# --------------------------------
# Service
# --------------------------------


def test_service_ecs():
    session = make_session("fake-A-org")
    suffix, context = get_suffix(
        "ecs",
        "this parameter doesn't matter",
        "",
        session,
    )
    assert suffix == f"{ECS_CONSOLE_URL}task-definitions"
    assert context.session.region_name == "us-east-1"
    assert context.identity["Account"] == "111111111111"


def test_service_task():
    session = make_session("fake-A-org")
    suffix, context = get_suffix(
        "task",
        "this parameter doesn't matter",
        "us-west-2",
        session,
    )
    assert suffix == f"{ECS_CONSOLE_URL}task-definitions"
    assert context.session.region_name == "us-west-2"
    assert context.identity["Account"] == "111111111111"


def test_service_tasks():
    session = make_session("fake-A-org")
    suffix, context = get_suffix(
        "tasks",
        "this parameter doesn't matter",
        "us-west-2",
        session,
    )
    assert suffix == f"{ECS_CONSOLE_URL}task-definitions"
    assert context.session.region_name == "us-west-2"
    assert context.identity["Account"] == "111111111111"


def test_service_cluster():
    session = make_session("fake-A-org")
    suffix, context = get_suffix(
        "cluster",
        "this parameter doesn't matter",
        "us-west-2",
        session,
    )
    assert suffix == f"{ECS_CONSOLE_URL}clusters"
    assert context.session.region_name == "us-west-2"
    assert context.identity["Account"] == "111111111111"
