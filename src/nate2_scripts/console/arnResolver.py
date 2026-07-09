import argparse
import re
import sys
from dataclasses import dataclass
from typing import NoReturn
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


def split(arn: str | None, num: int, chr=":") -> list[str | None]:
    return ((arn.split(chr, num) if arn else []) + [None] * 10)[: num + 1]


class ArnResolver:
    # arn:aws:elasticloadbalancing:us-east-1:905502466771:loadbalancer/net/nate2-smb-port-forward/08360f60575c36cd
    account: str
    mdn: str

    def __init__(self, account: str, mdn: str):
        self.account = account
        self.mdn = mdn

    def try_parse_arn(self, service: str) -> str | None:
        arn, rest = split(service, 1)
        if arn != "arn" or not rest:
            return None

        return self._parse_aws(rest)

    def _parse_aws(self, arn: str) -> str:
        aws_loc, rest = arn.split(":", 1)
        if aws_loc == "aws" and rest:
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

        # require both region and account
        match service:
            case "ec2":
                return self.parse_ec2(account, region, rest)
            case "lambda":
                return self.parse_lambda(account, region, rest)
            case "logs":
                return self.parse_logs(account, region, rest)
            case "rds":
                return self.parse_rds(account, region, rest)
            case "secretsmanager":
                return self.parse_secretsmanager(account, region, rest)
            case "ecs":
                return self.parse_ecs(account, region, rest)
            case "eks":
                return self.parse_eks(account, region, rest)
            case "sns":
                return self.parse_sns(account, region, rest)
            case "sqs":
                return self.parse_sqs(account, region, rest)
            case "batch":
                return self.parse_batch(account, region, rest)
            case "dynamodb":
                return self.parse_dynamodb(account, region, rest)
            case "states":
                return self.parse_states(account, region, rest)
            case "elasticloadbalancing":
                return self.parse_elb(account, region, rest)
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
            print(
                f"Error: Unable to access S3 bucket '{resource_id}' on account {self.account}: {e}",
                file=sys.stderr,
            )
            sys.exit(1)

    def parse_iam(self, account, rest) -> str:
        resource_type, resource_id = split(rest, 1, "/")
        match resource_type:
            case "role":
                try:
                    boto3.client("iam").get_role(RoleName=resource_id)
                    return f"https://{self.mdn}us-east-1.console.aws.amazon.com/iam/home#/roles/{resource_id}"
                except ClientError as e:
                    print(
                        f"Error: Unable to access IAM role '{resource_id}' on account {self.account}: {e}",
                        file=sys.stderr,
                    )
                    sys.exit(1)
            # TODO test
            case "user":
                try:
                    boto3.client("iam").get_user(UserName=resource_id)
                    return f"https://{self.mdn}us-east-1.console.aws.amazon.com/iam/home#/users/{resource_id}"
                except ClientError as e:
                    print(
                        f"Error: Unable to access IAM user '{resource_id}' on account {self.account}: {e}",
                        file=sys.stderr,
                    )
                    sys.exit(1)
            case _:
                print(
                    f"Error: Unsupported IAM resource type '{resource_type}' in ARN: 'arn:aws:iam::{account}:{resource_type}/{resource_id}'",
                    file=sys.stderr,
                )
                sys.exit(1)

    def _access_fail(self, what: str, err) -> NoReturn:
        print(
            f"Error: Unable to access {what} on account {self.account}: {err}",
            file=sys.stderr,
        )
        sys.exit(1)

    def _unsupported(self, service: str, resource_type, rest) -> NoReturn:
        print(
            f"Error: Unsupported {service} resource type '{resource_type}' in ARN: 'arn:aws:{service}:*:{rest}'",
            file=sys.stderr,
        )
        sys.exit(1)

    def parse_ec2(self, account, region, rest) -> str:
        resource_type, resource_id = split(rest, 1, "/")
        client = boto3.client("ec2", region_name=region)
        base = f"https://{self.mdn}{region}.console.aws.amazon.com"
        try:
            match resource_type:
                case "instance":
                    result = client.describe_instances(InstanceIds=[resource_id])
                    if not result["Reservations"]:
                        raise ValueError(f"Instance '{resource_id}' not found.")
                    return f"{base}/ec2/home?region={region}#InstanceDetails:instanceId={resource_id}"
                case "vpc":
                    result = client.describe_vpcs(VpcIds=[resource_id])
                    if not result["Vpcs"]:
                        raise ValueError(f"VPC '{resource_id}' not found.")
                    return f"{base}/vpcconsole/home?region={region}#VpcDetails:VpcId={resource_id}"
                case "subnet":
                    result = client.describe_subnets(SubnetIds=[resource_id])
                    if not result["Subnets"]:
                        raise ValueError(f"Subnet '{resource_id}' not found.")
                    return f"{base}/vpcconsole/home?region={region}#SubnetDetails:subnetId={resource_id}"
                case "security-group":
                    result = client.describe_security_groups(GroupIds=[resource_id])
                    if not result["SecurityGroups"]:
                        raise ValueError(f"Security group '{resource_id}' not found.")
                    return f"{base}/ec2/home?region={region}#SecurityGroup:groupId={resource_id}"
                case "volume":
                    result = client.describe_volumes(VolumeIds=[resource_id])
                    if not result["Volumes"]:
                        raise ValueError(f"Volume '{resource_id}' not found.")
                    return f"{base}/ec2/home?region={region}#VolumeDetails:volumeId={resource_id}"
                case "image":
                    result = client.describe_images(ImageIds=[resource_id])
                    if not result["Images"]:
                        raise ValueError(f"AMI '{resource_id}' not found.")
                    return f"{base}/ec2/home?region={region}#ImageDetails:imageId={resource_id}"
                case "snapshot":
                    result = client.describe_snapshots(SnapshotIds=[resource_id])
                    if not result["Snapshots"]:
                        raise ValueError(f"Snapshot '{resource_id}' not found.")
                    return f"{base}/ec2/home?region={region}#SnapshotDetails:snapshotId={resource_id}"
                case "launch-template":
                    result = client.describe_launch_templates(
                        LaunchTemplateIds=[resource_id]
                    )
                    if not result["LaunchTemplates"]:
                        raise ValueError(f"Launch template '{resource_id}' not found.")
                    return f"{base}/ec2/home?region={region}#LaunchTemplateDetails:launchTemplateId={resource_id}"
                case "route-table":
                    result = client.describe_route_tables(RouteTableIds=[resource_id])
                    if not result["RouteTables"]:
                        raise ValueError(f"Route table '{resource_id}' not found.")
                    return f"{base}/vpcconsole/home?region={region}#RouteTableDetails:RouteTableId={resource_id}"
                case "network-interface":
                    result = client.describe_network_interfaces(
                        NetworkInterfaceIds=[resource_id]
                    )
                    if not result["NetworkInterfaces"]:
                        raise ValueError(
                            f"Network interface '{resource_id}' not found."
                        )
                    return f"{base}/ec2/home?region={region}#NetworkInterface:networkInterfaceId={resource_id}"
                case "natgateway":
                    result = client.describe_nat_gateways(NatGatewayIds=[resource_id])
                    if not result["NatGateways"]:
                        raise ValueError(f"NAT gateway '{resource_id}' not found.")
                    return f"{base}/vpcconsole/home?region={region}#NatGatewayDetails:natGatewayId={resource_id}"
                case _:
                    self._unsupported("ec2", resource_type, rest)
        except ClientError as e:
            self._access_fail(f"EC2 {resource_type} '{resource_id}'", e)
        except ValueError as e:
            self._access_fail(f"EC2 {resource_type} '{resource_id}'", e)

    def parse_lambda(self, account, region, rest) -> str:
        resource_type, resource_id = split(rest, 1, ":")
        if resource_type != "function":
            self._unsupported("lambda", resource_type, rest)
        try:
            boto3.client("lambda", region_name=region).get_function(
                FunctionName=resource_id
            )
            return f"https://{self.mdn}{region}.console.aws.amazon.com/lambda/home?region={region}#/functions/{resource_id}"
        except ClientError as e:
            self._access_fail(f"Lambda function '{resource_id}'", e)

    def parse_logs(self, account, region, rest) -> str:
        resource_type, resource_id = split(rest, 1, ":")
        if resource_type != "log-group":
            self._unsupported("logs", resource_type, rest)
        # log-group arns often carry a trailing ':*' wildcard
        name = resource_id or ""
        if name.endswith(":*"):
            name = name[:-2]
        try:
            result = boto3.client("logs", region_name=region).describe_log_groups(
                logGroupNamePrefix=name
            )
            if not any(
                lg["logGroupName"] == name for lg in result.get("logGroups", [])
            ):
                raise ValueError(f"Log group '{name}' not found.")
            encoded = urllib.parse.quote(name, safe="")
            return f"https://{self.mdn}{region}.console.aws.amazon.com/cloudwatch/home?region={region}#logsV2:log-groups/log-group/{encoded}"
        except ClientError as e:
            self._access_fail(f"log group '{name}'", e)
        except ValueError as e:
            self._access_fail(f"log group '{name}'", e)

    def parse_rds(self, account, region, rest) -> str:
        resource_type, resource_id = split(rest, 1, ":")
        client = boto3.client("rds", region_name=region)
        base = f"https://{self.mdn}{region}.console.aws.amazon.com/rds/home?region={region}"
        try:
            match resource_type:
                case "db":
                    result = client.describe_db_instances(
                        DBInstanceIdentifier=resource_id
                    )
                    if not result["DBInstances"]:
                        raise ValueError(f"RDS instance '{resource_id}' not found.")
                    return f"{base}#database:id={resource_id};is-cluster=false"
                case "cluster":
                    result = client.describe_db_clusters(
                        DBClusterIdentifier=resource_id
                    )
                    if not result["DBClusters"]:
                        raise ValueError(f"RDS cluster '{resource_id}' not found.")
                    return f"{base}#database:id={resource_id};is-cluster=true"
                case _:
                    self._unsupported("rds", resource_type, rest)
        except ClientError as e:
            self._access_fail(f"RDS {resource_type} '{resource_id}'", e)
        except ValueError as e:
            self._access_fail(f"RDS {resource_type} '{resource_id}'", e)

    def parse_secretsmanager(self, account, region, rest) -> str:
        resource_type, resource_id = split(rest, 1, ":")
        if resource_type != "secret":
            self._unsupported("secretsmanager", resource_type, rest)
        arn = f"arn:aws:secretsmanager:{region}:{account}:secret:{resource_id}"
        try:
            boto3.client("secretsmanager", region_name=region).describe_secret(
                SecretId=arn
            )
            # secret arns end with a random 6-char suffix that the console omits
            name = re.sub(r"-[A-Za-z0-9]{6}$", "", resource_id or "")
            encoded = urllib.parse.quote(name, safe="")
            return f"https://{self.mdn}{region}.console.aws.amazon.com/secretsmanager/home?region={region}#!/secret?name={encoded}"
        except ClientError as e:
            self._access_fail(f"secret '{resource_id}'", e)

    def parse_ecs(self, account, region, rest) -> str:
        resource_type, resource_id = split(rest, 1, "/")
        client = boto3.client("ecs", region_name=region)
        base = f"https://{self.mdn}{region}.console.aws.amazon.com/ecs/v2/clusters"
        try:
            match resource_type:
                case "cluster":
                    result = client.describe_clusters(clusters=[resource_id])
                    active = [
                        c for c in result.get("clusters", []) if c["status"] == "ACTIVE"
                    ]
                    if not active:
                        raise ValueError(
                            f"ECS cluster '{resource_id}' not found or not active."
                        )
                    return f"{base}/{resource_id}/services?region={region}"
                case "service":
                    cluster, service_name = split(resource_id, 1, "/")
                    result = client.describe_services(
                        cluster=cluster, services=[service_name]
                    )
                    active = [
                        s for s in result.get("services", []) if s["status"] == "ACTIVE"
                    ]
                    if not active:
                        raise ValueError(
                            f"ECS service '{service_name}' in cluster '{cluster}' not found or not active."
                        )
                    return f"{base}/{cluster}/services/{service_name}?region={region}"
                case "task":
                    cluster, task_id = split(resource_id, 1, "/")
                    result = client.describe_tasks(cluster=cluster, tasks=[task_id])
                    if not result.get("tasks"):
                        raise ValueError(
                            f"ECS task '{task_id}' in cluster '{cluster}' not found."
                        )
                    return f"{base}/{cluster}/tasks/{task_id}?region={region}"
                case _:
                    self._unsupported("ecs", resource_type, rest)
        except ClientError as e:
            self._access_fail(f"ECS {resource_type} '{resource_id}'", e)
        except ValueError as e:
            self._access_fail(f"ECS {resource_type} '{resource_id}'", e)

    def parse_eks(self, account, region, rest) -> str:
        resource_type, resource_id = split(rest, 1, "/")
        if resource_type != "cluster":
            self._unsupported("eks", resource_type, rest)
        try:
            boto3.client("eks", region_name=region).describe_cluster(name=resource_id)
            return f"https://{self.mdn}{region}.console.aws.amazon.com/eks/home?region={region}#/clusters/{resource_id}"
        except ClientError as e:
            self._access_fail(f"EKS cluster '{resource_id}'", e)

    def parse_sns(self, account, region, rest) -> str:
        topic = rest
        arn = f"arn:aws:sns:{region}:{account}:{topic}"
        try:
            boto3.client("sns", region_name=region).get_topic_attributes(TopicArn=arn)
            return f"https://{self.mdn}{region}.console.aws.amazon.com/sns/v3/home?region={region}#/topic/{arn}"
        except ClientError as e:
            self._access_fail(f"SNS topic '{topic}'", e)

    def parse_sqs(self, account, region, rest) -> str:
        queue = rest
        try:
            url = boto3.client("sqs", region_name=region).get_queue_url(
                QueueName=queue, QueueOwnerAWSAccountId=account
            )["QueueUrl"]
            encoded = urllib.parse.quote(url, safe="")
            return f"https://{self.mdn}{region}.console.aws.amazon.com/sqs/v3/home?region={region}#/queues/{encoded}"
        except ClientError as e:
            self._access_fail(f"SQS queue '{queue}'", e)

    def parse_batch(self, account, region, rest) -> str:
        resource_type, resource_id = split(rest, 1, "/")
        client = boto3.client("batch", region_name=region)
        base = f"https://{self.mdn}{region}.console.aws.amazon.com/batch/home?region={region}"
        try:
            match resource_type:
                case "job-queue":
                    result = client.describe_job_queues(jobQueues=[resource_id])
                    if not result.get("jobQueues"):
                        raise ValueError(f"Batch job queue '{resource_id}' not found.")
                    arn = f"arn:aws:batch:{region}:{account}:job-queue/{resource_id}"
                    return f"{base}#queues/detail/{arn}"
                case "compute-environment":
                    result = client.describe_compute_environments(
                        computeEnvironments=[resource_id]
                    )
                    if not result.get("computeEnvironments"):
                        raise ValueError(
                            f"Batch compute environment '{resource_id}' not found."
                        )
                    arn = f"arn:aws:batch:{region}:{account}:compute-environment/{resource_id}"
                    return f"{base}#compute-environments/detail/{arn}"
                case "job-definition":
                    arn = (
                        f"arn:aws:batch:{region}:{account}:job-definition/{resource_id}"
                    )
                    result = client.describe_job_definitions(jobDefinitions=[arn])
                    if not result.get("jobDefinitions"):
                        raise ValueError(
                            f"Batch job definition '{resource_id}' not found."
                        )
                    return f"{base}#job-definition/detail/{arn}"
                case "job":
                    result = client.describe_jobs(jobs=[resource_id])
                    if not result.get("jobs"):
                        raise ValueError(f"Batch job '{resource_id}' not found.")
                    return f"{base}#jobs/detail/{resource_id}"
                case _:
                    self._unsupported("batch", resource_type, rest)
        except ClientError as e:
            self._access_fail(f"Batch {resource_type} '{resource_id}'", e)
        except ValueError as e:
            self._access_fail(f"Batch {resource_type} '{resource_id}'", e)

    def parse_dynamodb(self, account, region, rest) -> str:
        resource_type, resource_id = split(rest, 1, "/")
        if resource_type != "table":
            self._unsupported("dynamodb", resource_type, rest)
        try:
            boto3.client("dynamodb", region_name=region).describe_table(
                TableName=resource_id
            )
            return f"https://{self.mdn}{region}.console.aws.amazon.com/dynamodbv2/home?region={region}#table?name={resource_id}"
        except ClientError as e:
            self._access_fail(f"DynamoDB table '{resource_id}'", e)

    def parse_states(self, account, region, rest) -> str:
        resource_type, resource_id = split(rest, 1, ":")
        client = boto3.client("stepfunctions", region_name=region)
        base = f"https://{self.mdn}{region}.console.aws.amazon.com/states/home?region={region}"
        try:
            match resource_type:
                case "stateMachine":
                    arn = (
                        f"arn:aws:states:{region}:{account}:stateMachine:{resource_id}"
                    )
                    client.describe_state_machine(stateMachineArn=arn)
                    return (
                        f"{base}#/statemachines/view/{urllib.parse.quote(arn, safe='')}"
                    )
                case "execution":
                    arn = f"arn:aws:states:{region}:{account}:execution:{resource_id}"
                    client.describe_execution(executionArn=arn)
                    return f"{base}#/v2/executions/details/{urllib.parse.quote(arn, safe='')}"
                case _:
                    self._unsupported("states", resource_type, rest)
        except ClientError as e:
            self._access_fail(f"Step Functions {resource_type} '{resource_id}'", e)

    def parse_elb(self, account, region, rest) -> str:
        resource_type, resource_id = split(rest, 1, "/")
        client = boto3.client("elbv2", region_name=region)
        base = f"https://{self.mdn}{region}.console.aws.amazon.com/ec2/home?region={region}"
        arn = f"arn:aws:elasticloadbalancing:{region}:{account}:{rest}"
        try:
            match resource_type:
                case "loadbalancer":
                    result = client.describe_load_balancers(LoadBalancerArns=[arn])
                    if not result.get("LoadBalancers"):
                        raise ValueError(f"Load balancer '{resource_id}' not found.")
                    return f"{base}#LoadBalancers:loadBalancerArn={arn}"
                case "targetgroup":
                    result = client.describe_target_groups(TargetGroupArns=[arn])
                    if not result.get("TargetGroups"):
                        raise ValueError(f"Target group '{resource_id}' not found.")
                    return f"{base}#TargetGroup:targetGroupArn={arn}"
                case _:
                    self._unsupported("elasticloadbalancing", resource_type, rest)
        except ClientError as e:
            self._access_fail(f"ELB {resource_type} '{resource_id}'", e)
        except ValueError as e:
            self._access_fail(f"ELB {resource_type} '{resource_id}'", e)

    # def verify(self, arn: ParsedArn) -> None:
    #     region = arn.region
    #     key = (arn.service, arn.resource_type)

    #     try:
    #         if key == ("s3", ""):
    #             boto3.client("s3").head_ucket(Bucket=arn.resource_id)
    #         elif key == ("lambda", "function"):
    #             boto3.client("lambda", region_name=region).get_function(
    #                 FunctionName=arn.resource_id
    #             )
    #         elif key == ("ec2", "instance"):
    #             result = boto3.client("ec2", region_name=region).describe_instances(
    #                 InstanceIds=[arn.resource_id]
    #             )
    #             if not result["Reservations"]:
    #                 raise ValueError(f"Instance '{arn.resource_id}' not found.")
    #         elif key == ("ec2", "vpc"):
    #             result = boto3.client("ec2", region_name=region).describe_vpcs(
    #                 VpcIds=[arn.resource_id]
    #             )
    #             if not result["Vpcs"]:
    #                 raise ValueError(f"VPC '{arn.resource_id}' not found.")
    #         elif key == ("ec2", "subnet"):
    #             result = boto3.client("ec2", region_name=region).describe_subnets(
    #                 SubnetIds=[arn.resource_id]
    #             )
    #             if not result["Subnets"]:
    #                 raise ValueError(f"Subnet '{arn.resource_id}' not found.")
    #         elif key == ("ec2", "security-group"):
    #             result = boto3.client(
    #                 "ec2", region_name=region
    #             ).describe_security_groups(GroupIds=[arn.resource_id])
    #             if not result["SecurityGroups"]:
    #                 raise ValueError(f"Security group '{arn.resource_id}' not found.")
    #         elif key == ("iam", "role"):
    #             boto3.client("iam").get_role(RoleName=arn.resource_id)
    #         elif key == ("iam", "user"):
    #             boto3.client("iam").get_user(UserName=arn.resource_id)
    #         elif key == ("rds", "db"):
    #             boto3.client("rds", region_name=region).describe_db_instances(
    #                 DBInstanceIdentifier=arn.resource_id
    #             )
    #         elif key == ("rds", "cluster"):
    #             boto3.client("rds", region_name=region).describe_db_clusters(
    #                 DBClusterIdentifier=arn.resource_id
    #             )
    #         elif key == ("ecs", "cluster"):
    #             result = boto3.client("ecs", region_name=region).describe_clusters(
    #                 clusters=[arn.resource_id]
    #             )
    #             active = [
    #                 c for c in result.get("clusters", []) if c["status"] == "ACTIVE"
    #             ]
    #             if not active:
    #                 raise ValueError(
    #                     f"ECS cluster '{arn.resource_id}' not found or not active."
    #                 )
    #         elif key == ("ecs", "service"):
    #             cluster, service_name = arn.resource_id.split("/", 1)
    #             result = boto3.client("ecs", region_name=region).describe_services(
    #                 cluster=cluster, services=[service_name]
    #             )
    #             active = [
    #                 s for s in result.get("services", []) if s["status"] == "ACTIVE"
    #             ]
    #             if not active:
    #                 raise ValueError(
    #                     f"ECS service '{service_name}' in cluster '{cluster}' not found or not active."
    #                 )
    #         elif key == ("eks", "cluster"):
    #             boto3.client("eks", region_name=region).describe_cluster(
    #                 name=arn.resource_id
    #             )
    #         elif key == ("secretsmanager", "secret"):
    #             boto3.client("secretsmanager", region_name=region).describe_secret(
    #                 SecretId=arn.arn
    #             )
    #         elif key == ("logs", "log-group"):
    #             result = boto3.client("logs", region_name=region).describe_log_groups(
    #                 logGroupNamePrefix=arn.resource_id
    #             )
    #             matches = [
    #                 lg
    #                 for lg in result.get("logGroups", [])
    #                 if lg["logGroupName"] == arn.resource_id
    #             ]
    #             if not matches:
    #                 raise ValueError(f"Log group '{arn.resource_id}' not found.")
    #         else:
    #             print(
    #                 f"Error: Unsupported ARN type '{arn.service}/{arn.resource_type}'. "
    #                 "Supported: s3 buckets, lambda functions, ec2 instances/vpcs/subnets/security-groups, "
    #                 "iam roles/users, rds db/clusters, ecs clusters/services, eks clusters, "
    #                 "secretsmanager secrets, cloudwatch log groups.",
    #                 file=sys.stderr,
    #             )
    #             sys.exit(1)
    #     except ClientError as e:
    #         print(f"Error: {e.response['Error']['Message']}", file=sys.stderr)
    #         sys.exit(1)
    #     except ValueError as e:
    #         print(f"Error: {e}", file=sys.stderr)
    #         sys.exit(1)

    # def to_console_url(self, arn: ParsedArn) -> str:
    #     region = arn.region
    #     key = (arn.service, arn.resource_type)

    #     if key == ("s3", ""):
    #         return f"https://s3.console.aws.amazon.com/s3/buckets/{arn.resource_id}"
    #     if key == ("lambda", "function"):
    #         return f"https://{region}.console.aws.amazon.com/lambda/home?region={region}#/functions/{arn.resource_id}"
    #     if key == ("ec2", "instance"):
    #         return f"https://{region}.console.aws.amazon.com/ec2/v2/home?region={region}#Instances:instanceId={arn.resource_id}"
    #     if key == ("ec2", "vpc"):
    #         return f"https://{region}.console.aws.amazon.com/vpcconsole/home?region={region}#VpcDetails:VpcId={arn.resource_id}"
    #     if key == ("ec2", "subnet"):
    #         return f"https://{region}.console.aws.amazon.com/vpcconsole/home?region={region}#SubnetDetails:subnetId={arn.resource_id}"
    #     if key == ("ec2", "security-group"):
    #         return f"https://{region}.console.aws.amazon.com/ec2/v2/home?region={region}#SecurityGroups:groupId={arn.resource_id}"
    #     if key == ("iam", "role"):
    #         return f"https://us-east-1.console.aws.amazon.com/iam/home#/roles/{arn.resource_id}"
    #     if key == ("iam", "user"):
    #         return f"https://us-east-1.console.aws.amazon.com/iam/home#/users/{arn.resource_id}"
    #     if key == ("rds", "db"):
    #         return f"https://{region}.console.aws.amazon.com/rds/home?region={region}#database:id={arn.resource_id}"
    #     if key == ("rds", "cluster"):
    #         return f"https://{region}.console.aws.amazon.com/rds/home?region={region}#database:id={arn.resource_id};is-cluster=true"
    #     if key == ("ecs", "cluster"):
    #         return f"https://{region}.console.aws.amazon.com/ecs/v2/clusters/{arn.resource_id}"
    #     if key == ("ecs", "service"):
    #         cluster, service_name = arn.resource_id.split("/", 1)
    #         return f"https://{region}.console.aws.amazon.com/ecs/v2/clusters/{cluster}/services/{service_name}"
    #     if key == ("eks", "cluster"):
    #         return f"https://{region}.console.aws.amazon.com/eks/home?region={region}#/clusters/{arn.resource_id}"
    #     if key == ("secretsmanager", "secret"):
    #         name = re.sub(r"-[A-Za-z0-9]{6}$", "", arn.resource_id)
    #         return f"https://{region}.console.aws.amazon.com/secretsmanager/home?region={region}#!/secret?name={urllib.parse.quote(name, safe='')}"
    #     if key == ("logs", "log-group"):
    #         encoded = urllib.parse.quote(arn.resource_id, safe="")
    #         return f"https://{region}.console.aws.amazon.com/cloudwatch/home?region={region}#logsV2:log-groups/log-group/{encoded}"
    #     # verify catches unsupported types first, but guard just in case
    #     print(
    #         f"Error: Unsupported ARN type '{arn.service}/{arn.resource_type}'.",
    #         file=sys.stderr,
    #     )
    #     sys.exit(1)
