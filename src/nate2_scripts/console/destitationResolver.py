import argparse
import re
import sys
from dataclasses import dataclass
import boto3
from nate2_scripts.console.arnResolver import ArnResolver
from nate2_scripts.console.regionCache import DEFAULT_REGION, RegionCache
from botocore.exceptions import ClientError
import urllib.parse

from nate2_scripts.console.resourceIdResolver import ResourceIdResolver


class DestinationResolver:

    account: str
    region_cache: RegionCache
    mdn: str

    def __init__(self, account: str, region_cache: RegionCache, multisession_domain_name: str):
        self.account = account
        self.region_cache = region_cache
        self.mdn = multisession_domain_name

    @staticmethod
    def get_service_list() -> list[str]:
        return list(DestinationResolver._get_services("").keys())

    def parse_destination(self, service: str, region: str) -> str:
        default_region = (
            region if len(region) > 0 else self.region_cache.get_default_region()
        )

        service_urls = DestinationResolver._get_services(default_region, self.mdn)

        if not service:
            return f"https://{self.mdn}{default_region}.console.aws.amazon.com/"
        
        arn_dest = ArnResolver(self.account,self.mdn).try_parse_arn(service)
        if arn_dest:
            return arn_dest

        id_dest = ResourceIdResolver(self.region_cache, self.mdn).try_parse_resource_id(service)
        if id_dest:
            return id_dest
        
        if service.lower() not in service_urls:
            print(f"Error: Unknown service '{service}'.", file=sys.stderr)
            sys.exit(1)
        return service_urls[service.lower()]

    @staticmethod
    def _get_services(region: str, mdn: str = "") -> dict[str, str]:
        return {
            "ec2": f"https://{mdn}{region}.console.aws.amazon.com/ec2/",
            "lambda": f"https://{mdn}{region}.console.aws.amazon.com/lambda/",
            "s3": f"https://{mdn}{region}.console.aws.amazon.com/s3/",
            "iam": f"https://{mdn}{region}.console.aws.amazon.com/iam/",
            "cloudwatch": f"https://{mdn}{region}.console.aws.amazon.com/cloudwatch/",
            "cw": f"https://{mdn}{region}.console.aws.amazon.com/cloudwatch/",
            "logs": f"https://{mdn}{region}.console.aws.amazon.com/cloudwatch/home#logsV2:log-groups",
            "cloudformation": f"https://{mdn}{region}.console.aws.amazon.com/cloudformation/",
            "cf": f"https://{mdn}{region}.console.aws.amazon.com/cloudformation/",
            "rds": f"https://{mdn}{region}.console.aws.amazon.com/rds/",
            "ecs": f"https://{mdn}{region}.console.aws.amazon.com/ecs/",
            "eks": f"https://{mdn}{region}.console.aws.amazon.com/eks/",
            "vpc": f"https://{mdn}{region}.console.aws.amazon.com/vpc/",
            "sg": f"https://{mdn}{region}.console.aws.amazon.com/vpcconsole/home#SecurityGroups",
            "batch": f"https://{mdn}{region}.console.aws.amazon.com/batch/",
            "sns": f"https://{mdn}{region}.console.aws.amazon.com/sns/",
            "sqs": f"https://{mdn}{region}.console.aws.amazon.com/sqs/",
            "step": f"https://{mdn}{region}.console.aws.amazon.com/states/",
            "cost": f"https://{mdn}{region}.console.aws.amazon.com/costmanagement/",
            "tennex": f"https://{mdn}{region}.console.aws.amazon.com/marketplace/search?applicationId=AWS-Marketplace-Console&ref_=ucaf&text=tennex",
            "ecr": f"https://{mdn}{region}.console.aws.amazon.com/ecr/",
            "support": f"https://{mdn}{region}.console.aws.amazon.com/support",
            "dynamo": f"https://{mdn}{region}.console.aws.amazon.com/dynamodb/",
            "bedrock": f"https://{mdn}{region}.console.aws.amazon.com/bedrock/",
            "br": f"https://{mdn}{region}.console.aws.amazon.com/bedrock/",
            "config": f"https://{mdn}{region}.console.aws.amazon.com/config/",
            "controltower": f"https://{mdn}{region}.console.aws.amazon.com/controltower/",
            "cognito": f"https://{mdn}{region}.console.aws.amazon.com/cognito/",
            "cloudfront": f"https://{mdn}{region}.console.aws.amazon.com/cloudfront/",
            # cant use cf because it conflicts with cloudformation and I think thats more important
            "front": f"https://{mdn}{region}.console.aws.amazon.com/cloudfront/",
            "route53": f"https://{mdn}{region}.console.aws.amazon.com/route53/",
            "53": f"https://{mdn}{region}.console.aws.amazon.com/route53/",
            "kms": f"https://{mdn}{region}.console.aws.amazon.com/kms/",
            "secretsmanager": f"https://{mdn}{region}.console.aws.amazon.com/secretsmanager/",
            # I mistyped it enough that this is here now
            "secretmanager": f"https://{mdn}{region}.console.aws.amazon.com/secretsmanager/",
            "sm": f"https://{mdn}{region}.console.aws.amazon.com/secretsmanager/",
            "storagegateway": f"https://{mdn}{region}.console.aws.amazon.com/storagegateway/",
            "sgw": f"https://{mdn}{region}.console.aws.amazon.com/storagegateway/",
            "acl": f"https://{mdn}{region}.console.aws.amazon.com/vpcconsole/home#acls:",
            "ami": f"https://{mdn}{region}.console.aws.amazon.com/ec2/home#Images",
            "elb": f"https://{mdn}{region}.console.aws.amazon.com/ec2/home#LoadBalancers",
            "athena": f"https://{mdn}{region}.console.aws.amazon.com/athena/home#/query-editor",
            "cloudtrail": f"https://{mdn}{region}.console.aws.amazon.com/cloudtrailv2/",
            "ct": f"https://{mdn}{region}.console.aws.amazon.com/cloudtrailv2/",
            # unchecked
        }


