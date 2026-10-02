import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

import boto3

from nate2_scripts.console.boto3_session import find_and_update_profile
from nate2_scripts.console.resolvers import Context, Resolver
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
from nate2_scripts.console.resolvers.marketplace import MarketplaceResolver
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
from nate2_scripts.console.resolvers.vpc import VpcResolver
from nate2_scripts.console.types import Arn, Context

MAX_THREADS = 10

RESOLVERS: list[Resolver] = [
    # have name-resolution so it must be listed first / in this order
    LogsResolver(),
    S3Resolver(),
    Ec2Resolver(),
    CloudFormationResolver(),
    LambdaResolver(),
    # no name-resolution
    # VpcResolver(),
    # IamResolver(),
    # RdsResolver(),
    # SecretsManagerResolver(),
    # EcsResolver(),
    # EksResolver(),
    # SnsResolver(),
    # SqsResolver(),
    # BatchResolver(),
    # DynamoDbResolver(),
    # StepFunctionsResolver(),
    # ElbResolver(),
    # CostResolver(),
    # SupportResolver(),
    # AthenaResolver(),
    # EcrResolver(),
    # BedrockResolver(),
    # ConfigResolver(),
    # ControlTowerResolver(),
    # CognitoResolver(),
    # CloudFrontResolver(),
    # Route53Resolver(),
    # KmsResolver(),
    # StorageGatewayResolver(),
    # FsxResolver(),
    # SsmResolver(),
    # ParameterResolver(),
    # CloudTrailResolver(),
    MarketplaceResolver(),
]


class TextResolver:
    context: Context

    def __init__(self, context: Context):
        self.context = context

    @staticmethod
    def get_service_list() -> list[str]:
        return [name for resolver in RESOLVERS for name in resolver.get_service_names()]

    def get_destination_suffix(self, service: str, search: str = "") -> str | None:
        if not service:
            return "console.aws.amazon.com"

        arn = Arn.try_parse(service)
        if arn is not None:
            return self.__resolve_arn(arn)
        else:
            return self.__resolve_not_arn(service, search)

    def __resolve_arn2(self, arn: Arn) -> str | None:
        if arn.account and arn.account != self.context.account:  # noqa: SIM102
            new_session = find_and_update_profile(self.context.session, arn.account)
            if new_session:
                self.context.session = new_session
                self.context.identity = self.context.session.client(
                    "sts"
                ).get_caller_identity()
            else:
                return None

        if arn.region:
            self.context.set_region(arn.region)

        for resolver in RESOLVERS:
            result = resolver.try_resolve_arn(self.context, arn)
            if result is not None:
                return result

    def __resolve_arn(self, arn: Arn) -> str | None:
        result = self.__resolve_arn2(arn)
        if result is not None:
            return result

        print(f"Error: Unable to resolve ARN '{arn.str()}'.", file=sys.stderr)
        return None

    def __resolve_not_arn(self, service: str, search: str = "") -> str | None:
        for resolver in RESOLVERS:
            result = resolver.try_resolve_service(self.context, service.lower(), search)
            if result is not None:
                return result

        for resolver in RESOLVERS:
            result = resolver.try_resolve_id(self.context, service)
            if result is not None:
                return result

        name_result = self.__resolve_name(service, search)
        if name_result is not None:
            return name_result
        print(
            f"Error: Unable to resolve service '{service}' with search '{search}'.",
            file=sys.stderr,
        )
        return None

    def __resolve_name(self, name: str, search: str) -> str | None:
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
