import re
import sys
from typing import NoReturn
import boto3
from botocore.exceptions import ClientError

from nate2_scripts.console.regionCache import RegionCache


class ResourceIdResolver:

    region_cache: RegionCache
    mdn: str

    def __init__(self, region_cache: RegionCache, multisession_domain_name: str):
        self.region_cache = region_cache
        self.mdn = multisession_domain_name

    _KMS_UUID = re.compile(
        r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
    )
    _KMS_MRK = re.compile(r"^mrk-[0-9a-f]{32}$")

    def try_parse_resource_id(self, resource_id: str) -> str | None:
        kind = self._kind(resource_id)
        if kind is None:
            return None

        # IAM resources are global — no region search needed
        if kind == "role":
            name = resource_id[5:]
            try:
                boto3.client("iam").get_role(RoleName=name)
            except ClientError:
                self._not_found(resource_id)
            return f"https://{self.mdn}us-east-1.console.aws.amazon.com/iam/home#/roles/{name}"
        if kind == "user":
            name = resource_id[4:]
            try:
                boto3.client("iam").get_user(UserName=name)
            except ClientError:
                self._not_found(resource_id)
            return f"https://{self.mdn}us-east-1.console.aws.amazon.com/iam/home#/users/{name}"

        # regional resources — find the region that actually holds the resource
        for region in self.region_cache.get_regions():
            url = self._resolve_in_region(kind, resource_id, region)
            if url:
                return url

        self._not_found(resource_id)

    def _kind(self, resource_id: str) -> str | None:
        if re.match(r"^i-[0-9a-f]{8,17}$", resource_id):
            return "instance"
        if re.match(r"^vpc-[0-9a-f]{8,17}$", resource_id):
            return "vpc"
        if re.match(r"^subnet-[0-9a-f]{8,17}$", resource_id):
            return "subnet"
        if re.match(r"^sg-[0-9a-f]{8,17}$", resource_id):
            return "sg"
        if re.match(r"^ami-[0-9a-f]{8,17}$", resource_id):
            return "ami"
        if re.match(r"^lt-[0-9a-f]{8,17}$", resource_id):
            return "lt"
        if re.match(r"^rtb-[0-9a-f]{8,17}$", resource_id):
            return "rtb"
        if re.match(r"^vol-[0-9a-f]{8,17}$", resource_id):
            return "vol"
        if re.match(r"^snap-[0-9a-f]{8,17}$", resource_id):
            return "snap"
        if re.match(r"^eni-[0-9a-f]{8,17}$", resource_id):
            return "eni"
        if re.match(r"^nat-[0-9a-f]{8,17}$", resource_id):
            return "nat"
        # no idea where this is supposed to go, but it's a thing that exists
        # keeping it here in case I figure out later
        # if re.match(r"^fl-[0-9a-f]{8,17}$", resource_id):
        #     return "fl"
        if self._KMS_UUID.match(resource_id) or self._KMS_MRK.match(resource_id):
            return "kms"
        if resource_id.startswith("db/"):
            return "rds"
        if resource_id.startswith("role/"):
            return "role"
        if resource_id.startswith("usr/"):
            return "user"
        return None

    def _resolve_in_region(
        self, kind: str, resource_id: str, region: str
    ) -> str | None:
        base = f"https://{self.mdn}{region}.console.aws.amazon.com"
        try:
            match kind:
                case "instance":
                    ec2 = boto3.client("ec2", region_name=region)
                    if ec2.describe_instances(InstanceIds=[resource_id])["Reservations"]:
                        return f"{base}/ec2/v2/home?region={region}#InstanceDetails:instanceId={resource_id}"
                case "vpc":
                    ec2 = boto3.client("ec2", region_name=region)
                    if ec2.describe_vpcs(VpcIds=[resource_id])["Vpcs"]:
                        return f"{base}/vpcconsole/home?region={region}#VpcDetails:VpcId={resource_id}"
                case "subnet":
                    ec2 = boto3.client("ec2", region_name=region)
                    if ec2.describe_subnets(SubnetIds=[resource_id])["Subnets"]:
                        return f"{base}/vpcconsole/home?region={region}#SubnetDetails:subnetId={resource_id}"
                case "sg":
                    ec2 = boto3.client("ec2", region_name=region)
                    if ec2.describe_security_groups(GroupIds=[resource_id])[
                        "SecurityGroups"
                    ]:
                        return f"{base}/ec2/v2/home?region={region}#SecurityGroup:groupId={resource_id}"
                case "ami":
                    ec2 = boto3.client("ec2", region_name=region)
                    if ec2.describe_images(ImageIds=[resource_id])["Images"]:
                        return f"{base}/ec2/home?region={region}#ImageDetails:imageId={resource_id}"
                case "lt":
                    ec2 = boto3.client("ec2", region_name=region)
                    if ec2.describe_launch_templates(LaunchTemplateIds=[resource_id])[
                        "LaunchTemplates"
                    ]:
                        return f"{base}/ec2/home?region={region}#LaunchTemplateDetails:launchTemplateId={resource_id}"
                case "rtb":
                    ec2 = boto3.client("ec2", region_name=region)
                    if ec2.describe_route_tables(RouteTableIds=[resource_id])[
                        "RouteTables"
                    ]:
                        return f"{base}/vpcconsole/home?region={region}#RouteTableDetails:RouteTableId={resource_id}"
                case "vol":
                    ec2 = boto3.client("ec2", region_name=region)
                    if ec2.describe_volumes(VolumeIds=[resource_id])["Volumes"]:
                        return f"{base}/ec2/home?region={region}#VolumeDetails:volumeId={resource_id}"
                case "snap":
                    ec2 = boto3.client("ec2", region_name=region)
                    if ec2.describe_snapshots(SnapshotIds=[resource_id])["Snapshots"]:
                        return f"{base}/ec2/home?region={region}#SnapshotDetails:snapshotId={resource_id}"
                case "eni":
                    ec2 = boto3.client("ec2", region_name=region)
                    if ec2.describe_network_interfaces(NetworkInterfaceIds=[resource_id])["NetworkInterfaces"]:
                        return f"{base}/ec2/home?region={region}#NetworkInterface:networkInterfaceId={resource_id}"
                case "nat":
                    ec2 = boto3.client("ec2", region_name=region)
                    if ec2.describe_nat_gateways(NatGatewayIds=[resource_id])["NatGateways"]:
                        return f"{base}/vpcconsole/home?region={region}#NatGatewayDetails:natGatewayId={resource_id}"
                # case "fl":
                #     ec2 = boto3.client("ec2", region_name=region)
                #     if ec2.describe_flow_logs(FlowLogIds=[resource_id])["FlowLogs"]:
                #         return f"{base}/vpcconsole/home?region={region}#FlowLogs:flowLogId={resource_id}"
                case "kms":
                    boto3.client("kms", region_name=region).describe_key(
                        KeyId=resource_id
                    )
                    return f"{base}/kms/home?region={region}#/kms/keys/{resource_id}"
                # TODO test this
                case "rds":
                    name = resource_id[3:]
                    if boto3.client("rds", region_name=region).describe_db_instances(
                        DBInstanceIdentifier=name
                    )["DBInstances"]:
                        return f"{base}/rds/home?region={region}#database:id={name};is-cluster=false"
        except ClientError:
            # not present (or not accessible) in this region — try the next one
            return None
        return None

    def _not_found(self, resource_id: str) -> NoReturn:
        regions = ", ".join(self.region_cache.get_regions())
        print(
            f"Error: '{resource_id}' not found or not accessible in regions: {regions}",
            file=sys.stderr,
        )
        sys.exit(1)

