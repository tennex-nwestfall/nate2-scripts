from pathlib import Path

import boto3
import pytest

from nate2_scripts.console.resolvers import Arn
from nate2_scripts.console.text_resolver import RESOLVERS

TEST_DIR = Path(__file__).parent
from tests.console import resolvers


def make_session(profile_name: str, region: str | None = None):
    return boto3.Session(
        profile_name=profile_name,
        region_name=region,
    )


def make_link(arn: Arn) -> str:
    return f"/go/view?arn={arn.encode()}"


@pytest.mark.parametrize("resolver", RESOLVERS, ids=lambda r: type(r).__name__)
def test_resolver_has_test_file(resolver):
    module_name = type(resolver).__module__.rsplit(".", 1)[-1]
    assert (TEST_DIR / f"{module_name}.py").is_file(), (
        f"{type(resolver).__name__} has no tests/console/resolvers/{module_name}.py"
    )
