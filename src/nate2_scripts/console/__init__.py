# PYTHON_ARGCOMPLETE_OK

import argparse
import json
import os
import re
import subprocess
import sys
import time
import urllib.parse
import webbrowser
from dataclasses import dataclass
from pathlib import Path
from typing import Any, TypedDict

import argcomplete
import boto3
from argcomplete.completers import ChoicesCompleter

from nate2_scripts.console.hashGrabber import HashGrabber
from nate2_scripts.console.regionCache import RegionCache
from nate2_scripts.console.resolvers import Context
from nate2_scripts.console.sessionCache import SessionCache
from nate2_scripts.console.textResolver import TextResolver
from nate2_scripts.console.types import CallerIdentity

DEFAULT_REGIONS = ["us-east-1", "us-east-2", "us-west-1", "us-west-2"]


def get_email() -> str:
    result = subprocess.run(
        ["git", "config", "user.email"], capture_output=True, text=True, check=True
    )
    return result.stdout.strip()


def get_credentials(account_id: str) -> dict:
    # Check if already in an assumed role with the correct session name
    identity = boto3.client("sts").get_caller_identity()
    arn = identity.get("Arn", "")
    email = get_email()
    if "assumed-role/" in arn and arn.endswith(f"/{email}"):
        result = subprocess.run(
            ["aws", "configure", "export-credentials"],
            capture_output=True,
            text=True,
            check=True,
        )
        if result.returncode == 0:
            return json.loads(result.stdout)

    profile = os.environ.get("AWS_PROFILE", "default")
    session = boto3.Session(profile_name=profile)
    config = session._session.get_scoped_config()

    role_arn = config.get(
        "role_arn", f"arn:aws:iam::{account_id}:role/OrganizationAccountAccessRole"
    )
    source_profile = config.get("source_profile")

    if source_profile:
        source_sts = boto3.Session(profile_name=source_profile).client("sts")
    else:
        source_sts = sts

    try:
        response = source_sts.assume_role(
            RoleArn=role_arn,
            RoleSessionName=email,
        )
    except Exception as e:
        print(f"Error: Failed to assume role {role_arn}.\n{e}", file=sys.stderr)
        sys.exit(1)
    return response["Credentials"]


def get_signin_token(creds: dict) -> str:
    session = json.dumps(
        {
            "sessionId": creds["AccessKeyId"],
            "sessionKey": creds["SecretAccessKey"],
            "sessionToken": creds["SessionToken"],
        }
    )
    sess = urllib.parse.quote(session)
    token_url = (
        f"https://signin.aws.amazon.com/federation?Action=getSigninToken&Session={sess}"
    )
    result = subprocess.run(
        ["curl", "-s", token_url], capture_output=True, text=True, check=True
    )
    try:
        return json.loads(result.stdout)["SigninToken"]
    except json.JSONDecodeError:
        print("Error: Failed to parse JSON response. You may not have credentials.")
        sys.exit(1)


def build_console_url(destination: str, signin_token: str) -> str:
    dest = urllib.parse.quote(destination, safe="")
    return f"https://signin.aws.amazon.com/federation?Action=login&Issuer=&Destination={dest}&SigninToken={signin_token}"


def ensure_profile():
    profile_name = os.environ.get("AWS_PROFILE", "")
    if not profile_name:
        print(
            "Error: AWS_PROFILE environment variable is not set. run asp.",
            file=sys.stderr,
        )
        sys.exit(1)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Open AWS console for a specific service."
    )
    svc_arg: Any = parser.add_argument(
        "service",
        type=str,
        default="",
        nargs="?",
        help="The AWS service to open in the console, or an AWS ARN.",
    )
    svc_arg.completer = ChoicesCompleter(TextResolver.get_service_list())
    parser.add_argument(
        "search",
        type=str,
        default="",
        nargs="?",
        help="Optional search/filter term applied to service or name resolution.",
    )
    regions_arg: Any = parser.add_argument(
        "-r",
        "--region",
        type=str,
        default="",
        help="The AWS region to use.",
    )
    regions_arg.completer = argcomplete.completers.ChoicesCompleter(DEFAULT_REGIONS)

    parser.add_argument(
        "-f",
        "--force",
        action="store_true",
        help="Force new federations. This will reset the federations cache.",
    )
    argcomplete.autocomplete(parser)
    args = parser.parse_args()

    return args


def get_suffix(
    service: str,
    search: str,
    region: str,
    session: boto3.Session,
    regions: list[str] = DEFAULT_REGIONS,
) -> tuple[str | None, Context]:
    # set up context
    context = Context()
    if region != session.region_name:
        context.session = boto3.Session(
            profile_name=session.profile_name, region_name=region
        )
    else:
        context.session = session
    context.regions = regions
    context.current_region = context.session.region_name

    # get account data
    context.identity = context.session.client("sts").get_caller_identity()

    resolver = TextResolver(context)

    suffix = resolver.get_destination_suffix(service, search)
    return (suffix, context)


# profile_name = session.profile_name
# hash = session_cache.get_session_hash(profile_name, creds)

# multisession_domain_name = ""
# signin_token = None
# if hash is None:
#     print(f"{profile_name} has no cached session. Grabbing signin token.")
#     signin_token = get_signin_token(creds)
# elif len(hash) == 0:
#     print(f"{profile_name} cache is single session")
# else:
#     multisession_domain_name = f"{identity['Account']}-{hash}."
#     print(
#         f"{profile_name} cache is multi session with domain: {multisession_domain_name}"
#     )

# creds = get_credentials(identity["Account"])
# session = boto3.Session()

# context.session = session
# context.default_region = (
#     args.region if args.region else region_cache.get_default_region()
# )
# context.regions = region_cache.get_regions()
# context.current_account = identity["Account"]
# context.profile = profile_name

# resolver = TextResolver(context, multisession_domain_name)

# destination = resolver.parse_destination(args.service, args.region, args.search)

# print("parsed destination:", destination)

# if signin_token is not None:
#     print("Building signin url")
#     console_url = build_console_url(destination, signin_token)
#     webbrowser.open(console_url)
#     start_time = time.time()
#     print(
#         "Waiting for up to 10 seconds to allow the browser to open before exiting..."
#     )
#     hash = HashGrabber.get_hash(identity["Account"], start_time)
#     print(f"Hash found: {hash}")
#     session_cache.record_valid_hash(profile_name, hash)
# else:
#     print("Opening url")
#     webbrowser.open(destination)


def main() -> None:
    ensure_profile()
    args = parse_args()

    session = boto3.Session()
    session_cache = SessionCache()

    # add region if it is not already in the default searchable regions list
    regions = DEFAULT_REGIONS.copy()
    if args.region and args.region not in regions:
        regions.append(args.region)

    if args.force:
        print("Force passed. Reseting session cache.")
        session_cache.reset()

    region = args.region or session.region_name
    print("Default region is: ", region)

    suffix, context = get_suffix(args.service, args.search, region, session, regions)


if __name__ == "__main__":
    main()


# set user to OrganizationAccountAccessRole/nwestfall@tennex.io
