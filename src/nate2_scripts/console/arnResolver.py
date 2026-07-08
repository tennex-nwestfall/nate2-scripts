import argparse
import re
import sys
from dataclasses import dataclass
import boto3
from botocore.exceptions import ClientError
import urllib.parse


@dataclass
class ParsedArn:
    arn: str
    partition: str
    service: str
    region: str
    account: str
    resource_type: str
    resource_id: str


class ArnResolver:
    # arn:aws:elasticloadbalancing:us-east-1:905502466771:loadbalancer/net/nate2-smb-port-forward/08360f60575c36cd
    account: str
    mdn: str

    def __init__(self, account: str, mdn: str):
        self.account = account
        self.mdn = mdn

    def try_parse_arn(self, service: str) -> str | None:
        arn, rest = service.split(":", 1)
        if arn != "arn":
            return None

        return self._parse_aws(rest)

    def _parse_aws(self, arn: str) -> str:
        aws_loc, rest = arn.split(":", 1)
        if aws_loc == "aws":
            return self._parse_region(rest)

        print(f"Error: Invalid ARN format: 'arn:{aws_loc}:*'", file=sys.stderr)
        sys.exit(1)

    def _parse_region(self, arn: str) -> str:
        service, region, account, rest = arn.split(":", 3)

        # global resources like S3 dont have a region or account
        match service:
            case "s3":
                return self.parse_s3(rest)
        
        if account != self.account:
            print(
                f"Error: current account {self.account} cannot access: 'arn:aws:{service}:{region}:{account}:*'",
                file=sys.stderr,
            )
            sys.exit(1)

        match service:
            case "iam":
                return self.parse_iam(account, rest)

        if not region:
            print(f"Error: Invalid ARN format: 'arn:aws:{service}::*'", file=sys.stderr)
            sys.exit(1)

        match service:
            case "ec2":
                resource_type, resource_id = rest.split("/", 1)
            case "lambda":
                resource_type, resource_id = rest.split(":", 1)
            case _:
                print(
                    f"Error: Unsupported service '{service}' in ARN: 'arn:aws:{service}:*",
                    file=sys.stderr,
                )
                sys.exit(1)

        return region

    def parse_s3(self, rest) -> str:
        resource_id = rest
        try:
            boto3.client("s3").head_bucket(Bucket=resource_id)
            return f"https://{self.mdn}us-east-1.console.aws.amazon.com/s3/buckets/{resource_id}"
        except ClientError as e:
            print(f"Error: Unable to access S3 bucket '{resource_id}': {e}", file=sys.stderr)
            sys.exit(1)

    def parse_iam(self,  account, rest) -> str:
        resource_id = rest
        try:
            boto3.client("s3").head_bucket(Bucket=resource_id)
            return f"https://s3.console.aws.amazon.com/s3/buckets/{resource_id}"
        except ClientError as e:
            print(f"Error: Unable to access S3 bucket '{resource_id}': {e}", file=sys.stderr)
            sys.exit(1)


    def verify(self, arn: ParsedArn) -> None:
        region = arn.region
        key = (arn.service, arn.resource_type)

        try:
            if key == ("s3", ""):
                boto3.client("s3").head_ucket(Bucket=arn.resource_id)
            elif key == ("lambda", "function"):
                boto3.client("lambda", region_name=region).get_function(
                    FunctionName=arn.resource_id
                )
            elif key == ("ec2", "instance"):
                result = boto3.client("ec2", region_name=region).describe_instances(
                    InstanceIds=[arn.resource_id]
                )
                if not result["Reservations"]:
                    raise ValueError(f"Instance '{arn.resource_id}' not found.")
            elif key == ("ec2", "vpc"):
                result = boto3.client("ec2", region_name=region).describe_vpcs(
                    VpcIds=[arn.resource_id]
                )
                if not result["Vpcs"]:
                    raise ValueError(f"VPC '{arn.resource_id}' not found.")
            elif key == ("ec2", "subnet"):
                result = boto3.client("ec2", region_name=region).describe_subnets(
                    SubnetIds=[arn.resource_id]
                )
                if not result["Subnets"]:
                    raise ValueError(f"Subnet '{arn.resource_id}' not found.")
            elif key == ("ec2", "security-group"):
                result = boto3.client(
                    "ec2", region_name=region
                ).describe_security_groups(GroupIds=[arn.resource_id])
                if not result["SecurityGroups"]:
                    raise ValueError(f"Security group '{arn.resource_id}' not found.")
            elif key == ("iam", "role"):
                boto3.client("iam").get_role(RoleName=arn.resource_id)
            elif key == ("iam", "user"):
                boto3.client("iam").get_user(UserName=arn.resource_id)
            elif key == ("rds", "db"):
                boto3.client("rds", region_name=region).describe_db_instances(
                    DBInstanceIdentifier=arn.resource_id
                )
            elif key == ("rds", "cluster"):
                boto3.client("rds", region_name=region).describe_db_clusters(
                    DBClusterIdentifier=arn.resource_id
                )
            elif key == ("ecs", "cluster"):
                result = boto3.client("ecs", region_name=region).describe_clusters(
                    clusters=[arn.resource_id]
                )
                active = [
                    c for c in result.get("clusters", []) if c["status"] == "ACTIVE"
                ]
                if not active:
                    raise ValueError(
                        f"ECS cluster '{arn.resource_id}' not found or not active."
                    )
            elif key == ("ecs", "service"):
                cluster, service_name = arn.resource_id.split("/", 1)
                result = boto3.client("ecs", region_name=region).describe_services(
                    cluster=cluster, services=[service_name]
                )
                active = [
                    s for s in result.get("services", []) if s["status"] == "ACTIVE"
                ]
                if not active:
                    raise ValueError(
                        f"ECS service '{service_name}' in cluster '{cluster}' not found or not active."
                    )
            elif key == ("eks", "cluster"):
                boto3.client("eks", region_name=region).describe_cluster(
                    name=arn.resource_id
                )
            elif key == ("secretsmanager", "secret"):
                boto3.client("secretsmanager", region_name=region).describe_secret(
                    SecretId=arn.arn
                )
            elif key == ("logs", "log-group"):
                result = boto3.client("logs", region_name=region).describe_log_groups(
                    logGroupNamePrefix=arn.resource_id
                )
                matches = [
                    lg
                    for lg in result.get("logGroups", [])
                    if lg["logGroupName"] == arn.resource_id
                ]
                if not matches:
                    raise ValueError(f"Log group '{arn.resource_id}' not found.")
            else:
                print(
                    f"Error: Unsupported ARN type '{arn.service}/{arn.resource_type}'. "
                    "Supported: s3 buckets, lambda functions, ec2 instances/vpcs/subnets/security-groups, "
                    "iam roles/users, rds db/clusters, ecs clusters/services, eks clusters, "
                    "secretsmanager secrets, cloudwatch log groups.",
                    file=sys.stderr,
                )
                sys.exit(1)
        except ClientError as e:
            print(f"Error: {e.response['Error']['Message']}", file=sys.stderr)
            sys.exit(1)
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

    def to_console_url(self, arn: ParsedArn) -> str:
        region = arn.region
        key = (arn.service, arn.resource_type)

        if key == ("s3", ""):
            return f"https://s3.console.aws.amazon.com/s3/buckets/{arn.resource_id}"
        if key == ("lambda", "function"):
            return f"https://{region}.console.aws.amazon.com/lambda/home?region={region}#/functions/{arn.resource_id}"
        if key == ("ec2", "instance"):
            return f"https://{region}.console.aws.amazon.com/ec2/v2/home?region={region}#Instances:instanceId={arn.resource_id}"
        if key == ("ec2", "vpc"):
            return f"https://{region}.console.aws.amazon.com/vpcconsole/home?region={region}#VpcDetails:VpcId={arn.resource_id}"
        if key == ("ec2", "subnet"):
            return f"https://{region}.console.aws.amazon.com/vpcconsole/home?region={region}#SubnetDetails:subnetId={arn.resource_id}"
        if key == ("ec2", "security-group"):
            return f"https://{region}.console.aws.amazon.com/ec2/v2/home?region={region}#SecurityGroups:groupId={arn.resource_id}"
        if key == ("iam", "role"):
            return f"https://us-east-1.console.aws.amazon.com/iam/home#/roles/{arn.resource_id}"
        if key == ("iam", "user"):
            return f"https://us-east-1.console.aws.amazon.com/iam/home#/users/{arn.resource_id}"
        if key == ("rds", "db"):
            return f"https://{region}.console.aws.amazon.com/rds/home?region={region}#database:id={arn.resource_id}"
        if key == ("rds", "cluster"):
            return f"https://{region}.console.aws.amazon.com/rds/home?region={region}#database:id={arn.resource_id};is-cluster=true"
        if key == ("ecs", "cluster"):
            return f"https://{region}.console.aws.amazon.com/ecs/v2/clusters/{arn.resource_id}"
        if key == ("ecs", "service"):
            cluster, service_name = arn.resource_id.split("/", 1)
            return f"https://{region}.console.aws.amazon.com/ecs/v2/clusters/{cluster}/services/{service_name}"
        if key == ("eks", "cluster"):
            return f"https://{region}.console.aws.amazon.com/eks/home?region={region}#/clusters/{arn.resource_id}"
        if key == ("secretsmanager", "secret"):
            name = re.sub(r"-[A-Za-z0-9]{6}$", "", arn.resource_id)
            return f"https://{region}.console.aws.amazon.com/secretsmanager/home?region={region}#!/secret?name={urllib.parse.quote(name, safe='')}"
        if key == ("logs", "log-group"):
            encoded = urllib.parse.quote(arn.resource_id, safe="")
            return f"https://{region}.console.aws.amazon.com/cloudwatch/home?region={region}#logsV2:log-groups/log-group/{encoded}"
        # verify catches unsupported types first, but guard just in case
        print(
            f"Error: Unsupported ARN type '{arn.service}/{arn.resource_type}'.",
            file=sys.stderr,
        )
        sys.exit(1)
