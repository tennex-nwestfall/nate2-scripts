# Nate2's Scripts

Utility scripts for AWS development on macOS.

To run the scripts, move the script into a folder on your path.
Nate2 has them in `~/.local/bin`.

Make sure it is on your path:

```bash
export PATH="$HOME/.local/bin:$PATH"
```

## Scripts

### `console.py`

Opens the AWS Management Console in your browser for a specific service, using federated sign-in from your current AWS credentials.

**Requirements:**

`argcomplete`, (`pip install argcomplete`)

**Example Alias:**

```bash
alias console="console.py"
# needed for autocomplete
eval "$(register-python-argcomplete console.py)"
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
console ec2
# open lambda page of the role/account in us-west-2
console lambda -r us-west-2
```

**Supported services:** `ec2`, `lambda`, `s3`, `iam`, `cloudwatch`, `rds`, `ecs`, `eks`, `vpc`, `batch`

**All Regions Supported:** autocomplete contains `us-east-1`, `us-east-2`, `us-west-1`, `us-west-2`

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
```

**Options:**

| Flag | Description | Default |
| --- | --- | --- |
| `--end` | Play a sound when the command exits | off |
| `--pattern <text>` | Play a sound when `<text>` appears in output (repeatable) | none |
| `--sound-end <path>` | Sound file to play on exit | `Glass.aiff` |
| `--sound-pattern <path>` | Sound file to play on pattern match | `Glass.aiff` |
