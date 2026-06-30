#!/usr/bin/env python3
# PYTHON_ARGCOMPLETE_OK

import json
import subprocess
import sys
import urllib.parse
import webbrowser
import argparse
import argcomplete

DEFAULT_REGION = "us-east-1"


def get_services(region: str) -> dict[str, str]:
    return {
        "ec2": f"https://{region}.console.aws.amazon.com/ec2/",
        "lambda": f"https://{region}.console.aws.amazon.com/lambda/",
        "s3": f"https://{region}.console.aws.amazon.com/s3/",
        "iam": f"https://{region}.console.aws.amazon.com/iam/",
        "cloudwatch": f"https://{region}.console.aws.amazon.com/cloudwatch/",
        "rds": f"https://{region}.console.aws.amazon.com/rds/",
        "ecs": f"https://{region}.console.aws.amazon.com/ecs/",
        "eks": f"https://{region}.console.aws.amazon.com/eks/",
        "vpc": f"https://{region}.console.aws.amazon.com/vpc/",
        "batch": f"https://{region}.console.aws.amazon.com/batch/",
    }


def parse_destination(args: argparse.Namespace) -> str:
    region = args.region
    service = args.service
    SERVICE_URLS = get_services(region)

    if not service:
        return f"https://{region}.console.aws.amazon.com/"
    if service not in SERVICE_URLS:
        print(f"Error: Unknown service '{service}'.", file=sys.stderr)
        sys.exit(1)
    return SERVICE_URLS[service]


def get_credentials() -> dict:
    result = subprocess.run(
        ["aws", "configure", "export-credentials"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(f"Error: Failed to export credentials.\n{result.stderr}", file=sys.stderr)
        sys.exit(1)
    return json.loads(result.stdout)


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
    return json.loads(result.stdout)["SigninToken"]


def build_console_url(destination: str, signin_token: str) -> str:
    dest = urllib.parse.quote(destination, safe="")
    return f"https://signin.aws.amazon.com/federation?Action=login&Issuer=&Destination={dest}&SigninToken={signin_token}"


def get_regions() -> list[str]:
    # result = subprocess.run(
    #     "aws ec2 describe-regions --query \"Regions[].RegionName\" --output text",
    #     capture_output=True,
    #     text=True,
    #     shell=True,
    #     check=True,
    # )
    # return result.stdout.split()
    return ["us-east-1", "us-east-2", "us-west-1", "us-west-2"]


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Open AWS console for a specific service."
    )
    parser.add_argument(
        "service",
        type=str,
        default="",
        choices=get_services(DEFAULT_REGION).keys(),
        help="The AWS service to open in the console.",
    )
    parser.add_argument(
        "-r",
        "--region",
        type=str,
        default=DEFAULT_REGION,
        choices=get_regions(),
        help="The AWS region to use.",
    )
    argcomplete.autocomplete(parser)
    args = parser.parse_args()

    destination = parse_destination(args)

    creds = get_credentials()
    signin_token = get_signin_token(creds)
    console_url = build_console_url(destination, signin_token)

    webbrowser.open(console_url)


if __name__ == "__main__":
    main()
