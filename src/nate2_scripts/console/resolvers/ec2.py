import re
import urllib.parse

from nate2_scripts.console.resolvers import Arn, Context, Resolver, split


class Ec2Resolver(Resolver):
    def get_service_names(self) -> list[str]:
        return ["ec2", "sg", "ami"]

    def try_resolve_name(self, context: Context, name: str, search: str) -> str | None:
        # search is unused here; name lookup is an exact tag:Name match
        for region in context.regions:
            try:
                client = context.session.client("ec2", region_name=region)
                result = client.describe_instances(
                    Filters=[{"Name": "tag:Name", "Values": [name]}]
                )
                reservations = result.get("Reservations", [])
                if reservations:
                    instance_id = reservations[0]["Instances"][0]["InstanceId"]
                    return f"{region}.console.aws.amazon.com/ec2/v2/home?region={region}#InstanceDetails:instanceId={instance_id}"
            except Exception:
                continue
        return None

    def try_resolve_arn(self, context: Context, arn: Arn) -> str | None:
        if arn.service != "ec2":
            return None

        resource_type, resource_id = split(arn.resource, 1, "/")
        region = arn.region
        try:
            if resource_type == "instance":
                client = context.session.client("ec2", region_name=region)
                result = client.describe_instances(InstanceIds=[resource_id])
                if not result["Reservations"]:
                    return None
                return f"{region}.console.aws.amazon.com/ec2/home?region={region}#InstanceDetails:instanceId={resource_id}"
        except Exception:
            return None
        return None

    def try_resolve_service(
        self, context: Context, service: str, search: str
    ) -> str | None:
        if service not in self.get_service_names():
            return None
        region = context.default_region
        if service == "ec2":
            if search:
                return f"{region}.console.aws.amazon.com/ec2/home?region={region}#Instances:search={urllib.parse.quote(search)}"
            return f"{region}.console.aws.amazon.com/ec2/"
        if service == "sg":
            return f"{region}.console.aws.amazon.com/vpcconsole/home#SecurityGroups"
        if service == "ami":
            return f"{region}.console.aws.amazon.com/ec2/home#Images"
        return None  # unreachable but satisfies return type

    def try_resolve_id(self, context: Context, id: str) -> str | None:
        kind = None
        if re.match(r"^i-[0-9a-f]{8,17}$", id):
            kind = "instance"
        elif re.match(r"^sg-[0-9a-f]{8,17}$", id):
            kind = "sg"
        elif re.match(r"^ami-[0-9a-f]{8,17}$", id):
            kind = "ami"
        elif re.match(r"^lt-[0-9a-f]{8,17}$", id):
            kind = "lt"
        elif re.match(r"^vol-[0-9a-f]{8,17}$", id):
            kind = "vol"
        elif re.match(r"^snap-[0-9a-f]{8,17}$", id):
            kind = "snap"
        elif re.match(r"^eni-[0-9a-f]{8,17}$", id):
            kind = "eni"
        else:
            return None

        for region in context.regions:
            try:
                client = context.session.client("ec2", region_name=region)
                base = f"{region}.console.aws.amazon.com"
                if kind == "instance":
                    if client.describe_instances(InstanceIds=[id])["Reservations"]:
                        return f"{base}/ec2/v2/home?region={region}#InstanceDetails:instanceId={id}"
                elif kind == "sg":
                    if client.describe_security_groups(GroupIds=[id])["SecurityGroups"]:
                        return f"{base}/ec2/v2/home?region={region}#SecurityGroup:groupId={id}"
                elif kind == "ami":
                    if client.describe_images(ImageIds=[id])["Images"]:
                        return (
                            f"{base}/ec2/home?region={region}#ImageDetails:imageId={id}"
                        )
                elif kind == "lt":
                    if client.describe_launch_templates(LaunchTemplateIds=[id])[
                        "LaunchTemplates"
                    ]:
                        return f"{base}/ec2/home?region={region}#LaunchTemplateDetails:launchTemplateId={id}"
                elif kind == "vol":
                    if client.describe_volumes(VolumeIds=[id])["Volumes"]:
                        return f"{base}/ec2/home?region={region}#VolumeDetails:volumeId={id}"
                elif kind == "snap":
                    if client.describe_snapshots(SnapshotIds=[id])["Snapshots"]:
                        return f"{base}/ec2/home?region={region}#SnapshotDetails:snapshotId={id}"
                elif kind == "eni":
                    if client.describe_network_interfaces(NetworkInterfaceIds=[id])[
                        "NetworkInterfaces"
                    ]:
                        return f"{base}/ec2/home?region={region}#NetworkInterface:networkInterfaceId={id}"
            except Exception:
                continue
        return None
