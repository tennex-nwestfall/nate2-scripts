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

import argcomplete
import boto3

from nate2_scripts.console.destitationResolver import DestinationResolver
from nate2_scripts.console.hashGrabber import HashGrabber
from nate2_scripts.console.regionCache import RegionCache
from nate2_scripts.console.resolvers import Context
from nate2_scripts.console.sessionCache import SessionCache

sts = boto3.client("sts")


def get_email() -> str:
    result = subprocess.run(
        ["git", "config", "user.email"], capture_output=True, text=True
    )
    return result.stdout.strip()


def get_account_id() -> str:
    return sts.get_caller_identity()["Account"]


def get_credentials(account_id: str) -> dict:
    # Check if already in an assumed role with the correct session name
    identity = sts.get_caller_identity()
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


def get_profile() -> str:
    profile_name = os.environ.get("AWS_PROFILE", "")
    if not profile_name:
        print(
            "Error: AWS_PROFILE environment variable is not set. run asp.",
            file=sys.stderr,
        )
        sys.exit(1)
    return profile_name


def parse_args(region_cache: RegionCache) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Open AWS console for a specific service."
    )
    svc_arg = parser.add_argument(
        "service",
        type=str,
        default="",
        nargs="?",
        help="The AWS service to open in the console, or an AWS ARN.",
    )
    setattr(
        svc_arg,
        "completer",
        argcomplete.completers.ChoicesCompleter(
            list(DestinationResolver.get_service_list())
        ),
    )
    parser.add_argument(
        "search",
        type=str,
        default="",
        nargs="?",
        help="Optional search/filter term applied to service or name resolution.",
    )
    parser.add_argument(
        "-r",
        "--region",
        type=str,
        default="",
        choices=region_cache.get_regions(),
        help="The AWS region to use.",
    )
    parser.add_argument(
        "-f",
        "--force",
        action="store_true",
        help="Force new federations. This will reset the federations cache.",
    )
    argcomplete.autocomplete(parser)
    args = parser.parse_args()

    return args


def main() -> None:
    region_cache = RegionCache()
    args = parse_args(region_cache)

    profile_name = get_profile()
    session_cache = SessionCache()

    print("Loading regions from cache:", region_cache.get_regions())
    print("Loading default region from cache:", region_cache.get_default_region())

    if args.force:
        print("Force passed. Reseting session cache.")
        session_cache.reset()

    if args.region:
        print("Default region is now:", args.region)

    account_id = get_account_id()
    creds = get_credentials(account_id)
    hash = session_cache.get_session_hash(profile_name, creds)

    multisession_domain_name = ""
    signin_token = None
    if hash is None:
        print(f"{profile_name} has no cached session. Grabbing signin token.")
        signin_token = get_signin_token(creds)
    elif len(hash) == 0:
        print(f"{profile_name} cache is single session")
    else:
        multisession_domain_name = f"{account_id}-{hash}."
        print(
            f"{profile_name} cache is multi session with domain: {multisession_domain_name}"
        )

    session = boto3.Session(
        aws_access_key_id=creds["AccessKeyId"],
        aws_secret_access_key=creds["SecretAccessKey"],
        aws_session_token=creds["SessionToken"],
    )
    context = Context()
    context.session = session
    context.default_region = (
        args.region if args.region else region_cache.get_default_region()
    )
    context.regions = region_cache.get_regions()
    context.current_account = account_id
    context.profile = profile_name

    resolver = DestinationResolver(context, multisession_domain_name)

    destination = resolver.parse_destination(args.service, args.region, args.search)

    print("parsed destination:", destination)

    if signin_token is not None:
        print("Building signin url")
        console_url = build_console_url(destination, signin_token)
        webbrowser.open(console_url)
        start_time = time.time()
        print(
            "Waiting for up to 10 seconds to allow the browser to open before exiting..."
        )
        hash = HashGrabber.get_hash(account_id, start_time)
        print(f"Hash found: {hash}")
        session_cache.record_valid_hash(profile_name, hash)
    else:
        print("Opening url")
        webbrowser.open(destination)


if __name__ == "__main__":
    main()


# set user to OrganizationAccountAccessRole/nwestfall@tennex.io
