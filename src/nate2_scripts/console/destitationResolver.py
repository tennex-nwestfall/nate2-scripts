import argparse
import re
import sys
from dataclasses import dataclass
import boto3
from nate2_scripts.console.arnResolver import ArnResolver
from nate2_scripts.console.regionCache import DEFAULT_REGION, RegionCache
from botocore.exceptions import ClientError
import urllib.parse


class DestinationResolver:

    region_cache: RegionCache
    mdn: str

    def __init__(self, region_cache: RegionCache, multisession_domain_name: str):
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
        
        # arn_dest = ArnResolver().try_parse_arn(service)
        # if arn_dest:
        #     return arn_dest

        # url = ResourceIdResolver.to_console_url(service, default_region)
        # if url:
        #     ResourceIdResolver.verify(service, default_region)
        #     return url
        
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
            "ct": f"https://{mdn}{region}.console.aws.amazon.com/controltower/",
            "cognito": f"https://{mdn}{region}.console.aws.amazon.com/cognito/",
            "cloudfront": f"https://{mdn}{region}.console.aws.amazon.com/cloudfront/",
            # cant use cf because it conflicts with cloudformation and I think thats more important
            "front": f"https://{mdn}{region}.console.aws.amazon.com/cloudfront/",
            "route": f"https://{mdn}{region}.console.aws.amazon.com/route53/",
            "53": f"https://{mdn}{region}.console.aws.amazon.com/route53/",
            "kms": f"https://{mdn}{region}.console.aws.amazon.com/kms/",
            "secretsmanager": f"https://{mdn}{region}.console.aws.amazon.com/secretsmanager/",
            "sm": f"https://{mdn}{region}.console.aws.amazon.com/secretsmanager/",
            "storagegateway": f"https://{mdn}{region}.console.aws.amazon.com/storagegateway/",
            "sgw": f"https://{mdn}{region}.console.aws.amazon.com/storagegateway/",
            "acl": f"https://{mdn}{region}.console.aws.amazon.com/vpcconsole/home#acls:",
            "ami": f"https://{mdn}{region}.console.aws.amazon.com/ec2/home#Images",
            "elb": f"https://{mdn}{region}.console.aws.amazon.com/ec2/home#LoadBalancers",
            # unchecked
        }


class ResourceIdResolver:
    _KMS_UUID = re.compile(
        r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
    )
    _KMS_MRK = re.compile(r"^mrk-[0-9a-f]{32}$")

    @staticmethod
    def to_console_url(resource_id: str, region: str) -> str | None:
        if re.match(r"^i-[0-9a-f]{8,17}$", resource_id):
            return f"https://{region}.console.aws.amazon.com/ec2/v2/home?region={region}#Instances:instanceId={resource_id}"
        if re.match(r"^vpc-[0-9a-f]{8,17}$", resource_id):
            return f"https://{region}.console.aws.amazon.com/vpcconsole/home?region={region}#VpcDetails:VpcId={resource_id}"
        if re.match(r"^subnet-[0-9a-f]{8,17}$", resource_id):
            return f"https://{region}.console.aws.amazon.com/vpcconsole/home?region={region}#SubnetDetails:subnetId={resource_id}"
        if re.match(r"^sg-[0-9a-f]{8,17}$", resource_id):
            return f"https://{region}.console.aws.amazon.com/ec2/v2/home?region={region}#SecurityGroups:groupId={resource_id}"
        if re.match(r"^ami-[0-9a-f]{8,17}$", resource_id):
            return f"https://{region}.console.aws.amazon.com/ec2/home?region={region}#Images:imageId={resource_id}"
        if re.match(r"^lt-[0-9a-f]{8,17}$", resource_id):
            return f"https://{region}.console.aws.amazon.com/ec2/home?region={region}#LaunchTemplates:launchTemplateId={resource_id}"
        if re.match(r"^rtb-[0-9a-f]{8,17}$", resource_id):
            return f"https://{region}.console.aws.amazon.com/vpcconsole/home?region={region}#RouteTable:routeTableId={resource_id}"
        if ResourceIdResolver._KMS_UUID.match(
            resource_id
        ) or ResourceIdResolver._KMS_MRK.match(resource_id):
            return f"https://{region}.console.aws.amazon.com/kms/home?region={region}#/kms/keys/{resource_id}"
        return None

    @staticmethod
    def verify(resource_id: str, region: str) -> None:
        ec2 = boto3.client("ec2", region_name=region)
        try:
            if resource_id.startswith("i-"):
                result = ec2.describe_instances(InstanceIds=[resource_id])
                if not result["Reservations"]:
                    raise ValueError(f"Instance '{resource_id}' not found.")
            elif resource_id.startswith("vpc-"):
                result = ec2.describe_vpcs(VpcIds=[resource_id])
                if not result["Vpcs"]:
                    raise ValueError(f"VPC '{resource_id}' not found.")
            elif resource_id.startswith("subnet-"):
                result = ec2.describe_subnets(SubnetIds=[resource_id])
                if not result["Subnets"]:
                    raise ValueError(f"Subnet '{resource_id}' not found.")
            elif resource_id.startswith("sg-"):
                result = ec2.describe_security_groups(GroupIds=[resource_id])
                if not result["SecurityGroups"]:
                    raise ValueError(f"Security group '{resource_id}' not found.")
            elif resource_id.startswith("ami-"):
                result = ec2.describe_images(ImageIds=[resource_id])
                if not result["Images"]:
                    raise ValueError(f"AMI '{resource_id}' not found.")
            elif resource_id.startswith("lt-"):
                result = ec2.describe_launch_templates(LaunchTemplateIds=[resource_id])
                if not result["LaunchTemplates"]:
                    raise ValueError(f"Launch template '{resource_id}' not found.")
            elif resource_id.startswith("rtb-"):
                result = ec2.describe_route_tables(RouteTableIds=[resource_id])
                if not result["RouteTables"]:
                    raise ValueError(f"Route table '{resource_id}' not found.")
            elif ResourceIdResolver._KMS_UUID.match(
                resource_id
            ) or ResourceIdResolver._KMS_MRK.match(resource_id):
                boto3.client("kms", region_name=region).describe_key(KeyId=resource_id)
            elif resource_id.startswith("db/"):
                boto3.client("rds", region_name=region).describe_db_instances(
                    DBInstanceIdentifier=resource_id[3:]
                )
            elif resource_id.startswith("role/"):
                boto3.client("iam").get_role(RoleName=resource_id[5:])
            elif resource_id.startswith("usr/"):
                boto3.client("iam").get_user(UserName=resource_id[4:])
        except ClientError as e:
            print(f"Error: {e.response['Error']['Message']}", file=sys.stderr)
            sys.exit(1)
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
