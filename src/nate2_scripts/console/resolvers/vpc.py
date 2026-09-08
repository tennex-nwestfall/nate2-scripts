import re

from nate2_scripts.console.resolvers import Arn, Context, Resolver, split


class VpcResolver(Resolver):
    def get_service_names(self) -> list[str]:
        return ["vpc", "subnet", "acl"]

    def try_resolve_name(self, context: Context, name: str, search: str) -> str | None:
        return None

    def try_resolve_arn(self, context: Context, arn: Arn) -> str | None:
        if arn.service != "ec2":
            return None

        resource_type, resource_id = split(arn.resource, 1, "/")
        region = arn.region
        try:
            client = context.session.client("ec2", region_name=region)
            if resource_type == "subnet":
                if client.describe_subnets(SubnetIds=[resource_id])["Subnets"]:
                    return f"{region}.console.aws.amazon.com/vpcconsole/home?region={region}#SubnetDetails:subnetId={resource_id}"
            elif resource_type == "natgateway":
                if client.describe_nat_gateways(NatGatewayIds=[resource_id])[
                    "NatGateways"
                ]:
                    return f"{region}.console.aws.amazon.com/vpcconsole/home?region={region}#NatGatewayDetails:natGatewayId={resource_id}"
        except Exception:
            return None
        return None

    def try_resolve_service(
        self, context: Context, service: str, search: str
    ) -> str | None:
        if service not in self.get_service_names():
            return None
        region = context.default_region
        if service == "vpc":
            return f"{region}.console.aws.amazon.com/vpc/"
        if service == "subnet":
            return f"{region}.console.aws.amazon.com/vpcconsole/home#subnets:"
        if service == "acl":
            return f"{region}.console.aws.amazon.com/vpcconsole/home#acls:"
        return None  # unreachable but satisfies return type

    def try_resolve_id(self, context: Context, id: str) -> str | None:
        kind = None
        if re.match(r"^vpc-[0-9a-f]{8,17}$", id):
            kind = "vpc"
        elif re.match(r"^subnet-[0-9a-f]{8,17}$", id):
            kind = "subnet"
        elif re.match(r"^rtb-[0-9a-f]{8,17}$", id):
            kind = "rtb"
        elif re.match(r"^nat-[0-9a-f]{8,17}$", id):
            kind = "nat"
        else:
            return None

        for region in context.regions:
            try:
                client = context.session.client("ec2", region_name=region)
                base = f"{region}.console.aws.amazon.com"
                if kind == "vpc":
                    if client.describe_vpcs(VpcIds=[id])["Vpcs"]:
                        return f"{base}/vpcconsole/home?region={region}#VpcDetails:VpcId={id}"
                elif kind == "subnet":
                    if client.describe_subnets(SubnetIds=[id])["Subnets"]:
                        return f"{base}/vpcconsole/home?region={region}#SubnetDetails:subnetId={id}"
                elif kind == "rtb":
                    if client.describe_route_tables(RouteTableIds=[id])["RouteTables"]:
                        return f"{base}/vpcconsole/home?region={region}#RouteTableDetails:RouteTableId={id}"
                elif kind == "nat":
                    if client.describe_nat_gateways(NatGatewayIds=[id])["NatGateways"]:
                        return f"{base}/vpcconsole/home?region={region}#NatGatewayDetails:natGatewayId={id}"
            except Exception:
                continue
        return None
