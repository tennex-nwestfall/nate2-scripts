from pathlib import Path

import pytest
from moto import mock_aws


def get_profiles() -> dict:
    return {
        "profiles": {
            "tennex-auth-tennex-support-fake-company-A": {
                "region": "us-east-1",
            },
            "tennex-auth-tennex-support-fake-company-B": {
                "region": "us-east-1",
            },
            "fake-A-org": {
                "region": "us-east-1",
                "role_arn": "arn:aws:iam::111111111111:role/tennex-support-fake-company-A",
                "source_profile": "tennex-auth-tennex-support-fake-company-A",
            },
            "fake-A-main": {
                "region": "us-east-1",
                "role_arn": "arn:aws:iam::222222222222:role/tennex-support-fake-company-A",
                "source_profile": "tennex-auth-tennex-support-fake-company-A",
            },
            "fake-A-west": {
                "region": "us-west-2",
                "role_arn": "arn:aws:iam::333333333333:role/tennex-support-fake-company-A",
                "source_profile": "tennex-auth-tennex-support-fake-company-A",
            },
            "fake-B-org": {
                "region": "us-west-2",
                "role_arn": "arn:aws:iam::444444444444:role/tennex-support-fake-company-B",
                "source_profile": "tennex-auth-tennex-support-fake-company-B",
            },
            "fake-B-main": {
                "region": "us-west-2",
                "role_arn": "arn:aws:iam::555555555555:role/tennex-support-fake-company-B",
                "source_profile": "tennex-auth-tennex-support-fake-company-B",
            },
            "fake-B-east": {
                "region": "us-east-1",
                "role_arn": "arn:aws:iam::666666666666:role/tennex-support-fake-company-B",
                "source_profile": "tennex-auth-tennex-support-fake-company-B",
            },
        }
    }


def _write_aws_files(tmp_path: Path, profiles: dict) -> tuple[Path, Path]:
    """Materialise the profiles from get_profiles() into an AWS config +
    credentials file pair that boto3 can resolve.

    Base profiles (no source_profile) get static fake credentials so boto3 has
    something to sign the moto-intercepted assume_role calls with; role profiles
    get their role_arn/source_profile wiring in the config file.
    """
    config_lines: list[str] = []
    cred_lines: list[str] = [
        "[default]",
        "aws_access_key_id = testing",
        "aws_secret_access_key = testing",
        "",
    ]

    for name, cfg in profiles["profiles"].items():
        config_lines.append(f"[profile {name}]")
        for key, value in cfg.items():
            config_lines.append(f"{key} = {value}")
        config_lines.append("")

        # source/base profiles need real (fake) static creds to resolve
        if "source_profile" not in cfg:
            cred_lines.append(f"[{name}]")
            cred_lines.append("aws_access_key_id = testing")
            cred_lines.append("aws_secret_access_key = testing")
            cred_lines.append("")

    config_path = tmp_path / "config"
    cred_path = tmp_path / "credentials"
    config_path.write_text("\n".join(config_lines))
    cred_path.write_text("\n".join(cred_lines))
    return config_path, cred_path


@pytest.fixture(autouse=True)
def aws_profiles(tmp_path, monkeypatch):
    """Runs before every test in this directory: points boto3 at a temp AWS
    config holding the get_profiles() profiles, and activates moto so all
    session/STS/service calls hit the in-memory backend.
    """
    config_path, cred_path = _write_aws_files(tmp_path, get_profiles())

    monkeypatch.setenv("AWS_CONFIG_FILE", str(config_path))
    monkeypatch.setenv("AWS_SHARED_CREDENTIALS_FILE", str(cred_path))
    monkeypatch.setenv("AWS_DEFAULT_REGION", "us-east-1")
    # Env credentials would short-circuit the profile assume-role chain, so
    # make sure none leak in from the real environment.
    for var in (
        "AWS_PROFILE",
        "AWS_ACCESS_KEY_ID",
        "AWS_SECRET_ACCESS_KEY",
        "AWS_SESSION_TOKEN",
    ):
        monkeypatch.delenv(var, raising=False)

    with mock_aws():
        yield
