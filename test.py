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
from botocore.exceptions import ClientError


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
    try:
        return json.loads(result.stdout)["SigninToken"]
    except json.JSONDecodeError:
        print("Error: Failed to parse JSON response. You may not have credentials.")
        sys.exit(1)


creds = get_credentials()
print(creds)

signin_token = get_signin_token(creds)

print(signin_token)

# Build the federation login URL
destination = "https://us-east-1.console.aws.amazon.com/console/home?region=us-east-1"
dest_encoded = urllib.parse.quote(destination, safe="")
login_url = f"https://signin.aws.amazon.com/federation?Action=login&Issuer=&Destination={dest_encoded}&SigninToken={signin_token}"

# Follow redirects and capture the final URL
# print("\nFollowing federation redirect chain...")
# result = subprocess.run(
#     ["curl", "-s", "-L", "-o", "/dev/null", "-w", "%{url_effective}", login_url],
#     capture_output=True,
#     text=True,
# )
# final_url = result.stdout.strip()
# print(f"Final URL: {final_url}")

print(" ".join(["curl", "-s", "-L", "-v", login_url]))
sys.exit(0)
# Also check just the first redirect (without following)
signin_token2 = get_signin_token(creds)
login_url2 = f"https://signin.aws.amazon.com/federation?Action=login&Issuer=&Destination={dest_encoded}&SigninToken={signin_token2}"

result2 = subprocess.run(
    ["curl", "-s", "-o", "/dev/null", "-w", "%{redirect_url}", login_url2],
    capture_output=True,
    text=True,
)
first_redirect = result2.stdout.strip()
print(f"First redirect URL: {first_redirect}")

# Check if either contains the account-specific hash pattern
pattern = r"(\d{12})-([a-z0-9]+)\.[a-z0-9-]+\.console\.aws\.amazon\.com"
for label, url in [("Final", final_url), ("First redirect", first_redirect)]:
    match = re.search(pattern, url)
    if match:
        account_id, console_hash = match.groups()
        print(f"\n>>> Found hash in {label} URL!")
        print(f"    Account ID: {account_id}")
        print(f"    Console hash: {console_hash}")
        break
else:
    print("\n>>> No account-specific hash found in redirects.")
    print("    The rewrite is likely done client-side by JavaScript.")
