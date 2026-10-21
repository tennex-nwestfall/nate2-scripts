[![PyPI version](https://img.shields.io/pypi/v/nate2-scripts)](https://pypi.org/project/nate2-scripts/)
[![License](https://img.shields.io/github/license/tennex-nwestfall/nate2-scripts)](https://github.com/tennex-nwestfall/nate2-scripts/blob/main/LICENSE)

# Nate2's Scripts

Utility scripts for AWS development on macOS.

To install run:

```bash
pip install nate2-scripts
```

## Scripts

### `console`

Opens the AWS Management Console in your browser for a specific service, ARN, resource id, or resource name, using federated sign-in from your current AWS credentials. Supports multi-session via searching browser history sqlite databases.

**Requirements:**

- `AWS_PROFILE` set (e.g. via `asp`)
- `git config user.email` set — it is used as the `role_session_name` for every assume-role profile

**Example Alias:**

```bash
# noglob is so that one can paste in logs arns that end with :*
# otherwise zsh tries to see the log arn as a glob and fails
alias co="noglob console"
# needed for autocomplete
eval "$(register-python-argcomplete console)"
```

**Usage:**

```bash
console [service | arn | id | name] [search ...] [-r REGION] [-f]
```

```bash
# change to an account/role
asp my-aws-role

# open main page of the role/account
console
# open ec2 page of the role/account
console ec2
# open lambda page of the role/account in us-west-2
console lambda -r us-west-2
# open a service page filtered by search terms (multiple words are joined)
console lambda my-function
console logs /aws/lambda/my
console cf my stack
# open instance id page of the role/account in
# whatever region that instance is in
console i-0123456789abcdef
# open an S3 bucket, prefix, or object
console s3://my-bucket/some/prefix/
# open a resource by name (log group, S3 bucket, EC2 Name tag,
# CloudFormation stack, or Lambda function)
console my-function
# open the console page for the resource the ARN points to
console arn:aws:ec2:us-east-1:012345678967:instance/i-0123456789abcdef
# force a new federated sign-in (resets the session cache)
console -f
```

**Options:**

| Flag                    | Description                                                       |
| ----------------------- | ----------------------------------------------------------------- |
| `-r`, `--region <name>` | Region to open the console in; also added to the searched regions |
| `-f`, `--force`         | Reset the session cache and force a new federated sign-in         |

**Resolution order:**

1. **ARN** — if the first argument parses as an ARN
2. **Service** — if the first argument is a known service name or alias
3. **Resource id** — if the first argument matches a known id pattern
4. **Resource name** — looked up in parallel across all name-resolving services; the first match in priority order wins: CloudWatch log group → S3 bucket → EC2 `Name` tag → CloudFormation stack → Lambda function

**Supported services** (aliases after the `/`):

| Service                | Names                                     | Search terms |
| ---------------------- | ----------------------------------------- | ------------ |
| API Gateway            | `apigateway` / `api`                      |              |
| Artifact               | `artifact`                                |              |
| Athena                 | `athena`                                  |              |
| Batch                  | `batch` / `job` / `jobs`                  |              |
| Bedrock                | `bedrock` / `br`                          |              |
| CloudFormation         | `cloudformation` / `cf`                   | ✓            |
| CloudFront             | `cloudfront` / `front`                    |              |
| CloudHSM               | `cloudhsm` / `hsm`                        |              |
| CloudTrail             | `cloudtrail` / `ct`                       |              |
| CloudWatch             | `cloudwatch` / `cw`                       |              |
| CloudWatch Logs        | `logs`                                    | ✓            |
| Cognito                | `cognito` / `cn`                          |              |
| Config                 | `config` / `cfg`                          |              |
| Control Tower          | `controltower`                            |              |
| Cost Management        | `cost`                                    |              |
| DynamoDB               | `dynamodb` / `dynamo` / `dyn`             |              |
| EC2 instances          | `ec2`                                     | ✓            |
| EC2 AMIs (owned by me) | `ami`                                     | ✓            |
| ECR                    | `ecr` / `docker`                          |              |
| ECS                    | `ecs` / `cluster` / `task` / `tasks`      |              |
| EFS                    | `efs`                                     |              |
| EKS                    | `eks`                                     |              |
| Elastic Beanstalk      | `elasticbeanstalk` / `bean`               |              |
| Elastic Load Balancing | `elb` / `alb`                             |              |
| EventBridge            | `eventbridge` / `eb`                      |              |
| FSx                    | `fsx`                                     |              |
| Glue                   | `glue`                                    |              |
| GuardDuty              | `guardduty` / `guard`                     |              |
| IAM                    | `iam`                                     |              |
| Inspector              | `inspector`                               |              |
| KMS                    | `kms`                                     |              |
| Lambda                 | `lambda`                                  | ✓            |
| Lex                    | `lex`                                     |              |
| Lightsail              | `lightsail` / `ls`                        |              |
| Marketplace            | `marketplace` / `market` / `tennex`       | ✓            |
| Polly                  | `polly`                                   |              |
| RDS                    | `rds`                                     |              |
| Route 53               | `route53` / `53`                          |              |
| S3                     | `s3`                                      |              |
| SageMaker              | `sagemaker` / `sage`                      |              |
| Secrets Manager        | `secretsmanager` / `secretmanager` / `sm` |              |
| Security groups        | `sg`                                      | ✓            |
| SNS                    | `sns`                                     |              |
| SQS                    | `sqs`                                     |              |
| Step Functions         | `step`                                    |              |
| Storage Gateway        | `storagegateway` / `sgw`                  |              |
| Support                | `support`                                 |              |
| Systems Manager        | `ssm`                                     |              |
| SSM Parameter Store    | `parameter` / `ps`                        | ✓            |
| VPC                    | `vpc`                                     |              |
| VPC subnets            | `subnet`                                  |              |
| VPC network ACLs       | `acl` / `nacl`                            |              |
| VPC Elastic IPs        | `elasticip` / `eni`                       |              |
| VPC route tables       | `routetable` / `routes`                   |              |
| VPC internet gateways  | `internetgateway` / `internet` / `igw`    |              |
| VPC NAT gateways       | `nat`                                     |              |
| VPC endpoints          | `endpoints` / `end`                       |              |
| VPC transit gateways   | `transitgateway` / `transit` / `tgw`      |              |

`tennex` opens a Marketplace search for "tennex". Cost Management and Marketplace always open in `us-east-1`.

**Supported resource ids:** `i-*` (EC2 instance), `sg-*` (security group), `ami-*`, `lt-*` (launch template), `vol-*` (EBS volume), `snap-*` (EBS snapshot), `eni-*` (network interface), `s3://bucket[/key]`

**Supported ARNs:** `ec2` (instance), `lambda` (function), `logs` (log group, log stream), `s3` (bucket, prefix, object)

**Cross-account ARNs:** if an ARN's account differs from the current one, `console` switches to the first profile in your AWS config whose `role_arn` is in that account.

**Regions:** ids and names are searched across `us-east-1`, `us-east-2`, `us-west-1`, and `us-west-2`, plus the region passed with `-r`.

**Session cache:** federated session hashes are cached per profile for 59 minutes in `$XDG_STATE_HOME/console-sessions.json` (default `~/.local/state/console-sessions.json`). Use `-f` to reset it.

---

### `bing-wrapper`

A PTY wrapper that runs any command in a pseudo-terminal and plays a macOS system sound when a configurable output pattern is detected, and/or when the command finishes. Useful for long-running CLI tools (e.g. CDK deployments) that prompt for confirmation or take a while to complete.

**Requirements:** None

**Example Alias Usage:**

```bash
# wraps cdk to play Frog.aiff when done and play Glass.aiff (default) on "(y/n)" prompts
alias cdk="bing-wrapper --end --pattern \"(y/n)\" --sound-end /System/Library/Sounds/Frog.aiff -- cdk"

# wraps nextflow to play a sound when done
alias nextflow="bing-wrapper --end -- nextflow"

# needed for autocomplete of bing-wrapper and the inner command
eval "$(bing-wrapper --autocomplete)"
```

**Options:**

| Flag                     | Description                                               | Default      |
| ------------------------ | --------------------------------------------------------- | ------------ |
| `--end`                  | Play a sound when the command exits                       | off          |
| `--pattern <text>`       | Play a sound when `<text>` appears in output (repeatable) | none         |
| `--sound-end <path>`     | Sound file to play on exit                                | `Glass.aiff` |
| `--sound-pattern <path>` | Sound file to play on pattern match                       | `Glass.aiff` |
| `--sound-while <path>`   | Sound file to play on loop while the command runs         | none         |

---

## Development

```bash
pip install -e ".[dev]"
pytest
```

Resolver tests live in `tests/console/resolvers/`, one module per service, and use `moto` to mock AWS.
