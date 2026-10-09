from pathlib import Path

import pytest
from moto import mock_aws

# Static AWS config + credentials files holding the fake profiles. Base
# profiles (no source_profile) get static fake credentials so boto3 has
# something to sign the moto-intercepted assume_role calls with; role profiles
# get their role_arn/source_profile wiring in the config file.
TEST_AWS_DIR = Path(__file__).parent.parent / "test_aws"
AWS_CONFIG_FILE = TEST_AWS_DIR / "config"
AWS_CREDENTIALS_FILE = TEST_AWS_DIR / "credentials"


@pytest.fixture(autouse=True, scope="module")
def aws_profiles():
    """Runs once per test module in this directory: points boto3 at the static
    AWS config in tests/console/test_aws, and activates moto so all
    session/STS/service calls hit the in-memory backend. The backend is shared
    by every test in a module, so resource-seeding fixtures should be
    module-scoped too.
    """
    with pytest.MonkeyPatch.context() as mp:
        mp.setenv("AWS_CONFIG_FILE", str(AWS_CONFIG_FILE))
        mp.setenv("AWS_SHARED_CREDENTIALS_FILE", str(AWS_CREDENTIALS_FILE))
        # Env credentials would short-circuit the profile assume-role chain, so
        # make sure none leak in from the real environment.
        for var in (
            "AWS_DEFAULT_PROFILE",
            "AWS_PROFILE",
            "AWS_DEFAULT_REGION",
            "AWS_REGION",
            "AWS_ACCESS_KEY_ID",
            "AWS_SECRET_ACCESS_KEY",
            "AWS_SESSION_TOKEN",
        ):
            mp.delenv(var, raising=False)

        with mock_aws():
            yield
