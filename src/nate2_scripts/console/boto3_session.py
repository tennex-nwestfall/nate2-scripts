import functools
import subprocess
import sys

import boto3

from nate2_scripts.console.types import Arn


@functools.cache
def get_email() -> str:
    result = subprocess.run(
        ["git", "config", "user.email"], capture_output=True, text=True, check=True
    )
    email = result.stdout.strip()
    if not email.__contains__("@"):
        print("Error: Git user email is not set or invalid.", file=sys.stderr)
        sys.exit(1)

    return email


def update_role_names(session: boto3.Session):
    """Set role_session_name to the user's email on every assume-role profile in the session's config.

    Must be called before the session resolves credentials (i.e. before the first client is created).
    """
    email = get_email()
    for profile in session._session.full_config.get("profiles", {}).values():
        if "role_arn" in profile:
            profile["role_session_name"] = email


def find_and_update_profile(
    session: boto3.Session, new_account: str
) -> boto3.Session | None:
    print(f"Found different account number in ARN: {new_account}")
    for name, profile in session._session.full_config.get("profiles", {}).items():
        if "role_arn" in profile:
            arn = Arn.try_parse(profile["role_arn"])
            if arn is not None and arn.account == new_account:
                print(f"Changed profile to: {name}")
                session = boto3.Session(
                    profile_name=name,
                    region_name=session.region_name,
                )
                update_role_names(session)
                return session

    print("Error: Could not find profile for the account")
    return None
