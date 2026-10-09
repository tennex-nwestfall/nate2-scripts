import re
import urllib.parse
from unittest import case

from nate2_scripts.console.resolvers import Arn, Context, Resolver, split


class Ec2Resolver(Resolver):
    def get_service_names(self) -> list[str]:
        return ["ec2", "sg", "ami"]

    def try_resolve_name(self, context: Context, name: str) -> str | None:
        # search is unused here; name lookup is an exact tag:Name match
        for region in context.regions:
            try:
                client = context.session.client("ec2", region_name=region)
                result = client.describe_instances(
                    Filters=[{"Name": "tag:Name", "Values": [name]}]
                )
                reservations = result.get("Reservations", [])
                if reservations:
                    instance_id = reservations[0]["Instances"][0]["InstanceId"]  # type: ignore
                    context.set_region(region)
                    arn = Arn(
                        "ec2",
                        region,
                        context.account,
                        f"instance/{instance_id}",
                    )
                    return self.get_arn_link(arn)
            except Exception:  # noqa: BLE001, S112
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
                result = client.describe_instances(InstanceIds=[resource_id or ""])
                if not result["Reservations"]:
                    return None
                return self.get_arn_link(arn)
        except Exception:
            return None
        return None

    def try_resolve_service(
        self, context: Context, service: str, search: str
    ) -> str | None:
        if service == "ec2":
            if search:
                return f"/ec2/home#Instances:search={urllib.parse.quote(search)}"
            return "/ec2/home#Instances"
        if service == "sg":
            if search:
                return f"/vpcconsole/home#SecurityGroups:search={urllib.parse.quote(search)}"
            return "/vpcconsole/home#SecurityGroups"
        if service == "ami":
            if search:
                return f"/ec2/home#Images:visibility=owned-by-me;search={urllib.parse.quote(search)}"
            return "/ec2/home#Images:visibility=owned-by-me"
        return None  # unreachable but satisfies return type

    def try_resolve_id(self, context: Context, id: str) -> str | None:
        m = re.match(r"^(i|sg|ami|lt|vol|snap|eni)-[0-9a-f]{8,17}$", id)
        if not m:
            return None
        kind = m.group(1)

        for region in context.regions:
            try:
                client = context.session.client("ec2", region_name=region)
                match kind:
                    case "i":
                        resp = client.describe_instances(InstanceIds=[id])[
                            "Reservations"
                        ]
                        if resp:
                            context.set_region(region)
                            return f"/ec2/v2/home#InstanceDetails:instanceId={id}"
                    case "sg":
                        if client.describe_security_groups(GroupIds=[id])[
                            "SecurityGroups"
                        ]:
                            context.set_region(region)
                            return f"/ec2/v2/home#SecurityGroup:groupId={id}"
                    case "ami":
                        if client.describe_images(ImageIds=[id])["Images"]:
                            context.set_region(region)
                            return f"/ec2/home#ImageDetails:imageId={id}"
                    case "lt":
                        if client.describe_launch_templates(LaunchTemplateIds=[id])[
                            "LaunchTemplates"
                        ]:
                            context.set_region(region)
                            return (
                                f"/ec2/home#LaunchTemplateDetails:launchTemplateId={id}"
                            )
                    case "vol":
                        if client.describe_volumes(VolumeIds=[id])["Volumes"]:
                            context.set_region(region)
                            return f"/ec2/home#VolumeDetails:volumeId={id}"
                    case "snap":
                        if client.describe_snapshots(SnapshotIds=[id])["Snapshots"]:
                            context.set_region(region)
                            return f"/ec2/home#SnapshotDetails:snapshotId={id}"
                    case "eni":
                        if client.describe_network_interfaces(NetworkInterfaceIds=[id])[
                            "NetworkInterfaces"
                        ]:
                            context.set_region(region)
                            return f"/ec2/home#NetworkInterface:networkInterfaceId={id}"
            except Exception:  # noqa: BLE001, S112
                continue
        return None
