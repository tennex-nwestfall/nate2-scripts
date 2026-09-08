import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

from nate2_scripts.console.resolvers import Arn, Context, Resolver
from nate2_scripts.console.resolvers.athena import AthenaResolver
from nate2_scripts.console.resolvers.batch import BatchResolver
from nate2_scripts.console.resolvers.bedrock import BedrockResolver
from nate2_scripts.console.resolvers.cloudformation import CloudFormationResolver
from nate2_scripts.console.resolvers.cloudfront import CloudFrontResolver
from nate2_scripts.console.resolvers.cloudtrail import CloudTrailResolver
from nate2_scripts.console.resolvers.cognito import CognitoResolver
from nate2_scripts.console.resolvers.config import ConfigResolver
from nate2_scripts.console.resolvers.controltower import ControlTowerResolver
from nate2_scripts.console.resolvers.cost import CostResolver
from nate2_scripts.console.resolvers.dynamodb import DynamoDbResolver
from nate2_scripts.console.resolvers.ec2 import Ec2Resolver
from nate2_scripts.console.resolvers.ecr import EcrResolver
from nate2_scripts.console.resolvers.ecs import EcsResolver
from nate2_scripts.console.resolvers.eks import EksResolver
from nate2_scripts.console.resolvers.elb import ElbResolver
from nate2_scripts.console.resolvers.fsx import FsxResolver
from nate2_scripts.console.resolvers.iam import IamResolver
from nate2_scripts.console.resolvers.kms import KmsResolver
from nate2_scripts.console.resolvers.lambda_ import LambdaResolver
from nate2_scripts.console.resolvers.logs import LogsResolver
from nate2_scripts.console.resolvers.parameter import ParameterResolver
from nate2_scripts.console.resolvers.rds import RdsResolver
from nate2_scripts.console.resolvers.route53 import Route53Resolver
from nate2_scripts.console.resolvers.s3 import S3Resolver
from nate2_scripts.console.resolvers.secretsmanager import SecretsManagerResolver
from nate2_scripts.console.resolvers.sns import SnsResolver
from nate2_scripts.console.resolvers.sqs import SqsResolver
from nate2_scripts.console.resolvers.ssm import SsmResolver
from nate2_scripts.console.resolvers.stepfunctions import StepFunctionsResolver
from nate2_scripts.console.resolvers.storagegateway import StorageGatewayResolver
from nate2_scripts.console.resolvers.support import SupportResolver
from nate2_scripts.console.resolvers.tennex import TennexResolver
from nate2_scripts.console.resolvers.vpc import VpcResolver

MAX_THREADS = 10

RESOLVERS: list[Resolver] = [
    # have name-resolution
    LogsResolver(),
    S3Resolver(),
    Ec2Resolver(),
    CloudFormationResolver(),
    LambdaResolver(),
    # no name-resolution
    VpcResolver(),
    IamResolver(),
    RdsResolver(),
    SecretsManagerResolver(),
    EcsResolver(),
    EksResolver(),
    SnsResolver(),
    SqsResolver(),
    BatchResolver(),
    DynamoDbResolver(),
    StepFunctionsResolver(),
    ElbResolver(),
    CostResolver(),
    SupportResolver(),
    AthenaResolver(),
    EcrResolver(),
    BedrockResolver(),
    ConfigResolver(),
    ControlTowerResolver(),
    CognitoResolver(),
    CloudFrontResolver(),
    Route53Resolver(),
    KmsResolver(),
    StorageGatewayResolver(),
    FsxResolver(),
    SsmResolver(),
    ParameterResolver(),
    CloudTrailResolver(),
    TennexResolver(),
]

# keywords accepted by try_resolve_service across all resolvers, for argcomplete
SERVICE_KEYWORDS = [
    "ec2",
    "sg",
    "ami",
    "elb",
    "vpc",
    "subnet",
    "acl",
    "iam",
    "lambda",
    "logs",
    "cw",
    "cloudwatch",
    "cloudformation",
    "cf",
    "rds",
    "secretsmanager",
    "secretmanager",
    "sm",
    "ecs",
    "eks",
    "sns",
    "sqs",
    "batch",
    "dynamo",
    "step",
    "s3",
    "cost",
    "support",
    "athena",
    "ecr",
    "bedrock",
    "br",
    "config",
    "controltower",
    "cognito",
    "cloudfront",
    "front",
    "route53",
    "53",
    "kms",
    "storagegateway",
    "sgw",
    "fsx",
    "ssm",
    "parameter",
    "ps",
    "cloudtrail",
    "ct",
    "tennex",
]


class DestinationResolver:
    context: Context
    mdn: str

    def __init__(self, context: Context, multisession_domain_name: str):
        self.context = context
        self.mdn = multisession_domain_name

    @staticmethod
    def get_service_list() -> list[str]:
        return list(SERVICE_KEYWORDS)

    def parse_destination(self, service: str, region: str, search: str = "") -> str:
        if region:
            self.context.default_region = region

        if not service:
            return f"https://{self.mdn}{self.context.default_region}.console.aws.amazon.com/"

        arn = Arn.try_parse(service)
        if arn is not None:
            for resolver in RESOLVERS:
                result = resolver.try_resolve_arn(self.context, arn)
                if result is not None:
                    return f"https://{self.mdn}{result}"
            print(f"Error: Unable to resolve ARN '{service}'.", file=sys.stderr)
            sys.exit(1)

        for resolver in RESOLVERS:
            result = resolver.try_resolve_service(self.context, service.lower(), search)
            if result is not None:
                return f"https://{self.mdn}{result}"

        for resolver in RESOLVERS:
            result = resolver.try_resolve_id(self.context, service)
            if result is not None:
                return f"https://{self.mdn}{result}"

        name_result = self._resolve_name(service, search)
        if name_result is not None:
            return f"https://{self.mdn}{name_result}"

        print(f"Error: Unknown service '{service}'.", file=sys.stderr)
        sys.exit(1)

    def _resolve_name(self, name: str, search: str) -> str | None:
        results: dict[int, str] = {}
        with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
            future_to_priority = {
                executor.submit(
                    resolver.try_resolve_name, self.context, name, search
                ): priority
                for priority, resolver in enumerate(RESOLVERS)
            }
            for future in as_completed(future_to_priority):
                priority = future_to_priority[future]
                url = future.result()
                if url is not None and priority not in results:
                    results[priority] = url

        for priority in sorted(results):
            return results[priority]
        return None
