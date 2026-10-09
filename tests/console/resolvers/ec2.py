import boto3
import pytest

from nate2_scripts.console import get_suffix
from nate2_scripts.console.resolvers import Arn
from tests.console.resolvers import make_link, make_session

ACCOUNT = "111111111111"
EAST_1_INSTANCE_NAME = "exists-instance"
WEST_2_INSTANCE_NAME = "exists-instance-west"

# well-formed ids (match the resolver's id regex) that are never created
MISSING_IDS = {
    "ami": "ami-0123456789abcdef0",
    "eni": "eni-0123456789abcdef0",
    "i": "i-0123456789abcdef0",
    "lt": "lt-0123456789abcdef0",
    "sg": "sg-0123456789abcdef0",
    "snap": "snap-0123456789abcdef0",
    "vol": "vol-0123456789abcdef0",
}


def _run_named_instance(ec2, name: str) -> str:
    image_id = ec2.describe_images(Owners=["amazon"])["Images"][0]["ImageId"]
    return ec2.run_instances(
        ImageId=image_id,
        MaxCount=1,
        MinCount=1,
        TagSpecifications=[
            {"ResourceType": "instance", "Tags": [{"Key": "Name", "Value": name}]}
        ],
    )["Instances"][0]["InstanceId"]


@pytest.fixture(autouse=True, scope="module")
def ec2_resources() -> dict[str, str]:
    """Seed the moto backend (already active via the aws_profiles fixture) with
    one of each resource kind the id resolver handles. moto generates the ids,
    so they are returned keyed by kind (plus `west_i` for the us-west-2
    instance)."""
    session = boto3.Session(profile_name="fake-A-org", region_name="us-east-1")
    ec2 = session.client("ec2")
    instance_id = _run_named_instance(ec2, EAST_1_INSTANCE_NAME)
    volume_id = ec2.create_volume(AvailabilityZone="us-east-1a", Size=8)["VolumeId"]
    subnet_id = ec2.describe_subnets()["Subnets"][0]["SubnetId"]  # type: ignore
    resources = {
        "ami": ec2.create_image(InstanceId=instance_id, Name="exists-image")["ImageId"],
        "eni": ec2.create_network_interface(SubnetId=subnet_id)["NetworkInterface"][
            "NetworkInterfaceId"
        ],  # type: ignore
        "i": instance_id,
        "lt": ec2.create_launch_template(
            LaunchTemplateData={}, LaunchTemplateName="exists-template"
        )["LaunchTemplate"]["LaunchTemplateId"],  # type: ignore
        "sg": ec2.create_security_group(Description="exists", GroupName="exists-sg")[
            "GroupId"
        ],
        "snap": ec2.create_snapshot(VolumeId=volume_id)["SnapshotId"],
        "vol": volume_id,
    }

    session = boto3.Session(profile_name="fake-A-org", region_name="us-west-2")
    ec2 = session.client("ec2")
    resources["west_i"] = _run_named_instance(ec2, WEST_2_INSTANCE_NAME)

    return resources


# --------------------------------
# Service
# --------------------------------


def test_ec2_service():
    session = make_session("fake-A-org")
    suffix, context = get_suffix(
        "ec2",
        "",
        "",
        session,
    )
    assert suffix == "/ec2/home#Instances"
    assert context.session.region_name == "us-east-1"
    assert context.identity["Account"] == ACCOUNT


def test_ec2_service_west():
    session = make_session("fake-A-org")
    suffix, context = get_suffix(
        "ec2",
        "",
        "us-west-2",
        session,
    )
    assert suffix == "/ec2/home#Instances"
    assert context.session.region_name == "us-west-2"
    assert context.identity["Account"] == ACCOUNT


def test_ec2_service_search():
    session = make_session("fake-A-org")
    suffix, context = get_suffix(
        "ec2",
        "my instance",
        "us-west-2",
        session,
    )
    assert suffix == "/ec2/home#Instances:search=my%20instance"
    assert context.session.region_name == "us-west-2"
    assert context.identity["Account"] == ACCOUNT


# --------------------------------
# ARN
# --------------------------------


def test_ec2_arn(ec2_resources):
    session = make_session("fake-A-org")
    arn = Arn("ec2", "us-east-1", ACCOUNT, f"instance/{ec2_resources['i']}")
    suffix, context = get_suffix(
        arn.str(),
        "this parameter doesn't matter",
        "us-west-2",
        session,
    )
    assert suffix == make_link(arn)
    assert context.session.region_name == "us-east-1"
    assert context.identity["Account"] == ACCOUNT


def test_ec2_arn_west(ec2_resources):
    session = make_session("fake-A-org")
    arn = Arn("ec2", "us-west-2", ACCOUNT, f"instance/{ec2_resources['west_i']}")
    suffix, context = get_suffix(
        arn.str(),
        "this parameter doesn't matter",
        "us-east-1",
        session,
    )
    assert suffix == make_link(arn)
    assert context.session.region_name == "us-west-2"
    assert context.identity["Account"] == ACCOUNT


def test_ec2_arn_nonexistent():
    session = make_session("fake-A-org")
    arn = Arn("ec2", "us-east-1", ACCOUNT, f"instance/{MISSING_IDS['i']}")
    suffix, _context = get_suffix(
        arn.str(),
        "this parameter doesn't matter",
        "us-east-1",
        session,
    )
    assert suffix == None


def test_ec2_arn_wrong_region(ec2_resources):
    session = make_session("fake-A-org")
    arn = Arn("ec2", "us-west-2", ACCOUNT, f"instance/{ec2_resources['i']}")
    suffix, _context = get_suffix(
        arn.str(),
        "this parameter doesn't matter",
        "us-east-1",
        session,
    )
    assert suffix == None


# --------------------------------
# Name
# --------------------------------


def test_ec2_instance_name(ec2_resources):
    session = make_session("fake-A-org")
    suffix, context = get_suffix(
        EAST_1_INSTANCE_NAME,
        "this parameter doesn't matter",
        "us-west-2",
        session,
    )
    arn = Arn("ec2", "us-east-1", ACCOUNT, f"instance/{ec2_resources['i']}")
    assert suffix == make_link(arn)
    assert context.session.region_name == "us-east-1"
    assert context.identity["Account"] == ACCOUNT


def test_ec2_instance_name_west(ec2_resources):
    session = make_session("fake-A-org")
    suffix, context = get_suffix(
        WEST_2_INSTANCE_NAME,
        "this parameter doesn't matter",
        "us-east-1",
        session,
    )
    arn = Arn("ec2", "us-west-2", ACCOUNT, f"instance/{ec2_resources['west_i']}")
    assert suffix == make_link(arn)
    assert context.session.region_name == "us-west-2"
    assert context.identity["Account"] == ACCOUNT


def test_ec2_instance_name_missing():
    session = make_session("fake-A-org")
    suffix, _context = get_suffix(
        "thisinstancedoesntexist",
        "this parameter doesn't matter",
        "us-west-2",
        session,
    )
    assert suffix == None


# --------------------------------
# Id
# --------------------------------


@pytest.mark.parametrize(
    ("kind", "expected"),
    [
        ("ami", "/ec2/home#ImageDetails:imageId={id}"),
        ("eni", "/ec2/home#NetworkInterface:networkInterfaceId={id}"),
        ("i", "/ec2/v2/home#InstanceDetails:instanceId={id}"),
        ("lt", "/ec2/home#LaunchTemplateDetails:launchTemplateId={id}"),
        ("sg", "/ec2/v2/home#SecurityGroup:groupId={id}"),
        ("snap", "/ec2/home#SnapshotDetails:snapshotId={id}"),
        ("vol", "/ec2/home#VolumeDetails:volumeId={id}"),
    ],
)
def test_ec2_id_exists(ec2_resources, kind, expected):
    session = make_session("fake-A-org")
    resource_id = ec2_resources[kind]
    suffix, context = get_suffix(
        resource_id,
        "this parameter doesn't matter",
        "us-west-2",
        session,
    )
    assert suffix == expected.format(id=resource_id)
    assert context.session.region_name == "us-east-1"
    assert context.identity["Account"] == ACCOUNT


def test_ec2_id_exists_west(ec2_resources):
    session = make_session("fake-A-org")
    resource_id = ec2_resources["west_i"]
    suffix, context = get_suffix(
        resource_id,
        "this parameter doesn't matter",
        "us-east-1",
        session,
    )
    assert suffix == f"/ec2/v2/home#InstanceDetails:instanceId={resource_id}"
    assert context.session.region_name == "us-west-2"
    assert context.identity["Account"] == ACCOUNT


@pytest.mark.parametrize("kind", sorted(MISSING_IDS))
def test_ec2_id_doesnt_exist(kind):
    session = make_session("fake-A-org")
    suffix, _context = get_suffix(
        MISSING_IDS[kind],
        "this parameter doesn't matter",
        "us-west-2",
        session,
    )
    assert suffix == None
