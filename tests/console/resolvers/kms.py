from nate2_scripts.console import get_suffix
from tests.console.resolvers import make_session

KMS_CONSOLE_URL = "/kms/home#/kms/keys"

# --------------------------------
# Service
# --------------------------------


def test_service_kms():
    session = make_session("fake-A-org")
    suffix, context = get_suffix(
        "kms",
        "this parameter doesn't matter",
        "",
        session,
    )
    assert suffix == f"{KMS_CONSOLE_URL}"
    assert context.session.region_name == "us-east-1"
    assert context.identity["Account"] == "111111111111"
