
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

Opens the AWS Management Console in your browser for a specific service, arn, or resource id, using federated sign-in from your current AWS credentials. Supports multi-session via searching browser history sqlite databases.

**Requirements:**

`argcomplete`, (`pip install argcomplete`)

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
# change to an account/role 
asp my-aws-role

# open main page of the role/account
console
# open ec2 page of the role/account
console ec2
# open s3 page of the role/account
console s3
# open lambda page of the role/account in us-west-2
console lambda -r us-west-2
# open instance id page of the role/account in  
# whatever region that instance is in 
console i-0123456789abcdef
# open the console page for the resource the ARN points to
console arn:aws:ec2:us-east-1:012345678967:instance/i-0123456789abcdef
```

**Supported services:** `ec2`, `lambda`, `s3`, `iam`, `cloudwatch` / `cw`, `logs`, `cloudformation` / `cf`, `rds`, `ecs`, `eks`, `ecr`, `vpc`, `sg`, `acl`, `batch`, `sns`, `sqs`, `step` (Step Functions), `dynamo`, `bedrock` / `br`, `kms`, `secretsmanager` / `sm`, `elb`, `ami`, `athena`, `cloudfront` / `front`, `route` / `53` (Route 53), `cognito`, `config`, `controltower` / `ct`, `storagegateway` / `sgw`, `cost`, `support`

**Supported Instance Ids:** `i-*` (EC2), `vpc-*`, `subnet-*`, `sg-*` (security group), `ami-*`, `lt-*` (launch template), `rtb-*` (route table), `db/*` (RDS), `role/*` (IAM role), `usr/*` (IAM user), KMS key UUID, KMS MRK (`mrk-*`)

**Supported ARNs:** `ec2`, `iam` (role, user), `lambda`, `logs` (CloudWatch Logs), `rds`, `s3`, `secretsmanager`, `ecs`, `eks`, `sns`, `sqs`, `batch`, `dynamodb`, `states` (Step Functions), `elasticloadbalancing`

**All Regions Supported:**
Edit `~/.local/state/console-regions.json` to change which regions are evaluated and to set the default one

---

### `bing-wrapper.py`

A PTY wrapper that runs any command in a pseudo-terminal and plays a macOS system sound when a configurable output pattern is detected, and/or when the command finishes. Useful for long-running CLI tools (e.g. CDK deployments) that prompt for confirmation or take a while to complete.

**Requirements:** None

**Example Alias Usage:**

```bash
# wraps cdk to play Frog.aiff when done and play Glass.aiff (default) on "(y/n)" prompts
alias cdk="bing-wrapper.py --end --pattern \"(y/n)\" --sound-end /System/Library/Sounds/Frog.aiff -- cdk"

# wraps nextflow to play a sound when done
alias nextflow="bing-wrapper.py --end -- nextflow"

# needed for autocomplete of bing-wrapper and the inner command
eval "$(bing-wrapper --autocomplete)"
```

**Options:**

| Flag | Description | Default |
| --- | --- | --- |
| `--end` | Play a sound when the command exits | off |
| `--pattern <text>` | Play a sound when `<text>` appears in output (repeatable) | none |
| `--sound-end <path>` | Sound file to play on exit | `Glass.aiff` |
| `--sound-pattern <path>` | Sound file to play on pattern match | `Glass.aiff` |
