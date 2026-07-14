import re
import urllib.parse
from concurrent.futures import ThreadPoolExecutor, as_completed

import boto3
from botocore.exceptions import ClientError

from nate2_scripts.console.regionCache import RegionCache

MAX_THREADS = 10


class NameResolver:
    region_cache: RegionCache
    mdn: str

    def __init__(self, region_cache: RegionCache, multisession_domain_name: str):
        self.region_cache = region_cache
        self.mdn = multisession_domain_name

    def resolve_name(self, name: str) -> str | None:
        regions = self.region_cache.get_regions()

        # Priority: 0=logs, 1=ec2, 2=s3, 3=cloudformation
        tasks: list[tuple] = []
        for region in regions:
            tasks.append((0, self._resolve_log_group, name, region))
            tasks.append((1, self._resolve_ec2_instance, name, region))
            tasks.append((3, self._resolve_cloudformation_stack, name, region))
        tasks.append((2, self._resolve_s3_bucket, name))

        results: dict[int, str] = {}

        with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
            future_to_priority = {
                executor.submit(fn, *args): priority
                for priority, fn, *args in tasks
            }
            for future in as_completed(future_to_priority):
                priority = future_to_priority[future]
                url = future.result()
                if url is not None and priority not in results:
                    results[priority] = url

        for priority in sorted(results):
            return results[priority]
        return None

    def _resolve_log_group(self, name: str, region: str) -> str | None:
        try:
            result = boto3.client("logs", region_name=region).describe_log_groups(
                logGroupNamePrefix=name
            )
            if any(lg["logGroupName"] == name for lg in result.get("logGroups", [])):
                base = f"https://{self.mdn}{region}.console.aws.amazon.com"
                encoded = urllib.parse.quote(name, safe="")
                return f"{base}/cloudwatch/home?region={region}#logsV2:log-groups/log-group/{encoded}"
        except ClientError:
            pass
        return None

    def _resolve_ec2_instance(self, name: str, region: str) -> str | None:
        try:
            result = boto3.client("ec2", region_name=region).describe_instances(
                Filters=[{"Name": "tag:Name", "Values": [name]}]
            )
            reservations = result.get("Reservations", [])
            if reservations:
                base = f"https://{self.mdn}{region}.console.aws.amazon.com"
                instance_id = reservations[0]["Instances"][0]["InstanceId"]
                return f"{base}/ec2/v2/home?region={region}#InstanceDetails:instanceId={instance_id}"
        except ClientError:
            pass
        return None

    def _resolve_cloudformation_stack(self, name: str, region: str) -> str | None:
        try:
            result = boto3.client("cloudformation", region_name=region).describe_stacks(
                StackName=name
            )
            stacks = result.get("Stacks", [])
            if stacks:
                base = f"https://{self.mdn}{region}.console.aws.amazon.com"
                stack_id = urllib.parse.quote(stacks[0]["StackId"], safe="")
                return f"{base}/cloudformation/home?region={region}#/stacks/stackinfo?stackId={stack_id}"
        except ClientError:
            pass
        return None

    def _resolve_s3_bucket(self, name: str) -> str | None:
        try:
            boto3.client("s3").head_bucket(Bucket=name)
            return f"https://{self.mdn}us-east-1.console.aws.amazon.com/s3/buckets/{name}"
        except Exception:
            pass
        return None
    


