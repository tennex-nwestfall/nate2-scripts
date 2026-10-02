# PYTHON_ARGCOMPLETE_OK

import argparse
import json
import os
import subprocess
import sys
import time
import urllib.parse
import webbrowser
from typing import Any

import argcomplete
import boto3
from argcomplete.completers import ChoicesCompleter

from nate2_scripts.console.boto3_session import update_role_names
from nate2_scripts.console.hash_grabber import HashGrabber
from nate2_scripts.console.resolvers import Context
from nate2_scripts.console.session_cache import SessionCache
from nate2_scripts.console.text_resolver import TextResolver

DEFAULT_REGIONS = ["us-east-1", "us-east-2", "us-west-1", "us-west-2"]


def get_signin_token(session: boto3.Session) -> str:
    creds = session.get_credentials()
    if creds is None:
        print("Error: No credentials found for this session.", file=sys.stderr)
        sys.exit(1)
    frozen = creds.get_frozen_credentials()
    session_json = json.dumps(
        {
            "sessionId": frozen.access_key,
            "sessionKey": frozen.secret_key,
            "sessionToken": frozen.token,
        }
    )
    sess = urllib.parse.quote(session_json)
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
        default=[],
        nargs="*",
        help="Optional search/filter terms applied to service or name resolution. Multiple words are joined with spaces.",
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
    args = parser.parse_intermixed_args()
    # collapse multi-word search into a single string for the resolvers
    args.search = " ".join(args.search)

    return args


def get_suffix(
    service: str,
    search: str,
    region: str | None,
    session: boto3.Session,
) -> tuple[str | None, Context]:

    # add region if it is not already in the default searchable regions list
    regions = DEFAULT_REGIONS.copy()
    if region:
        session._session.set_config_variable("region", region)
        if region not in regions:
            regions.append(region)

    # set up context
    context = Context()
    context.session = session
    context.regions = regions

    # get account data
    context.identity = context.session.client("sts").get_caller_identity()

    resolver = TextResolver(context)

    suffix = resolver.get_destination_suffix(service, search)
    return (suffix, context)


def build_signin_url(session: boto3.Session, suffix: str) -> str:
    region = session.region_name
    signin_token = get_signin_token(session)
    dest = urllib.parse.quote(f"https://{region}.{suffix}", safe="")
    return f"https://signin.aws.amazon.com/federation?Action=login&Issuer=&SigninToken={signin_token}&Destination={dest}"


def build_regular_url(session: boto3.Session, suffix: str, mdn: str) -> str:
    region = session.region_name
    return f"https://{mdn}.{region}.{suffix}"


def open_console(suffix: str, context: Context, session_cache: SessionCache):
    print(f"Opening console with suffix: {suffix} and context: {context}")

    hash = session_cache.get_session_hash(context.session.profile_name)
    if hash is None:
        print(
            f"{context.session.profile_name} has no cached session. Grabbing signin token."
        )
        url = build_signin_url(context.session, suffix)
        print(f"Opening console URL: {url}")
        webbrowser.open(url)
        hash = HashGrabber.get_hash(context.identity["Account"], time.time())
        if hash is None:
            print("Failed to grab hash.")
            sys.exit(1)
        print(f"Successfully grabbed hash for {context.session.profile_name}: {hash}")
        session_cache.record_valid_hash(context.session.profile_name, hash)

    else:
        multisession_domain_name = f"{context.identity['Account']}-{hash}"
        print(
            f"{context.session.profile_name} cache has cached multi session with domain: {multisession_domain_name}"
        )
        url = build_regular_url(context.session, suffix, multisession_domain_name)
        print(f"Opening console URL: {url}")
        webbrowser.open(url)


def main() -> None:
    ensure_profile()
    args = parse_args()

    session = boto3.Session()
    session_cache = SessionCache()
    update_role_names(session)

    if args.force:
        print("Force passed. Resetting session cache.")
        session_cache.reset()

    print("Default region is: ", session.region_name)

    suffix, context = get_suffix(args.service, args.search, args.region, session)
    if suffix:
        open_console(suffix, context, session_cache)
    else:
        print("Cannot open console page.")


if __name__ == "__main__":
    main()


# set user to OrganizationAccountAccessRole/nwestfall@tennex.io
