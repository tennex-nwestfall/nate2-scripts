import re
import urllib.parse
from unittest import case

from nate2_scripts.console.resolvers import Arn, Context, Resolver, split


class Ec2Resolver(Resolver):
    def get_service_names(self) -> list[str]:
        return ["ec2", "sg", "ami", "volume"]

    def try_resolve_name(self, context: Context, name: str) -> str | None:
        # TODO: implement
        return None
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
                    return f"console.aws.amazon.com/ec2/v2/home?region={region}#InstanceDetails:instanceId={instance_id}"
            except Exception:
                continue
        return None

    def try_resolve_arn(self, context: Context, arn: Arn) -> str | None:
        if arn.service != "ec2":
            return None
        # TODO: implement
        return None

        resource_type, resource_id = split(arn.resource, 1, "/")
        region = arn.region
        try:
            if resource_type == "instance":
                client = context.session.client("ec2", region_name=region)
                result = client.describe_instances(InstanceIds=[resource_id])
                if not result["Reservations"]:
                    return None
                return f"console.aws.amazon.com/ec2/home?region={region}#InstanceDetails:instanceId={resource_id}"
        except Exception:
            return None
        return None

    def try_resolve_service(
        self, context: Context, service: str, search: str
    ) -> str | None:
        if service not in self.get_service_names():
            return None

        if service == "ec2":
            if search:
                return f"/ec2/home#Instances:search={urllib.parse.quote(search)}"
            return "/ec2#Instances"
        if service == "sg":
            if search:
                return f"/vpcconsole/home#SecurityGroups:search={urllib.parse.quote(search)}"
            return "/vpcconsole/home#SecurityGroups"
        if service == "ami":
            if search:
                return f"/ec2/home#Images:visibility=owned-by-me;search={urllib.parse.quote(search)}"
            return "/ec2/home#Images:visibility=owned-by-me"
        if service == "volume":
            if search:
                return f"/ec2/home#Volumes:search={urllib.parse.quote(search)}"
            return "/ec2/home#Volumes"
        return None  # unreachable but satisfies return type

    def try_resolve_id(self, context: Context, id: str) -> str | None:
        if re.match(r"^i-[0-9a-f]{8,17}$", id):
            kind = "i"
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
                match kind:
                    case "i":
                        resp = client.describe_instances(InstanceIds=[id])[
                            "Reservations"
                        ]
                        if resp:
                            context.set_region(
                                resp[0]["Instances"][0]["Placement"][
                                    "AvailabilityZone"
                                ][:-1]
                            )
                            return f"/ec2/v2/home#InstanceDetails:instanceId={id}"
                    case "sg":
                        if client.describe_security_groups(GroupIds=[id])[
                            "SecurityGroups"
                        ]:
                            return f"/ec2/v2/home#SecurityGroup:groupId={id}"
                    case "ami":
                        if client.describe_images(ImageIds=[id])["Images"]:
                            return f"/ec2/home#ImageDetails:imageId={id}"
                    case "lt":
                        if client.describe_launch_templates(LaunchTemplateIds=[id])[
                            "LaunchTemplates"
                        ]:
                            return (
                                f"/ec2/home#LaunchTemplateDetails:launchTemplateId={id}"
                            )
                    case "vol":
                        if client.describe_volumes(VolumeIds=[id])["Volumes"]:
                            return f"/ec2/home#VolumeDetails:volumeId={id}"
                    case "snap":
                        if client.describe_snapshots(SnapshotIds=[id])["Snapshots"]:
                            return f"/ec2/home#SnapshotDetails:snapshotId={id}"
                    case "eni":
                        if client.describe_network_interfaces(NetworkInterfaceIds=[id])[
                            "NetworkInterfaces"
                        ]:
                            return f"/ec2/home#NetworkInterface:networkInterfaceId={id}"
            except Exception:  # noqa: BLE001, S112
                continue
        return None
