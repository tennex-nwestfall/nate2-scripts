# Refactor console resolvers into per-service `Resolver` classes

## Context

The `console` command (entry point `nate2_scripts.console:main`) turns a user argument
into an AWS console URL and opens it. Today the resolution logic lives in **three
monolithic resolvers** plus a static service map, each of which handles *every* AWS
service internally via large `match`/`if` ladders:

- [destitationResolver.py](src/nate2_scripts/console/destitationResolver.py) — orchestrator + `_get_services()` static keyword→URL map
- [arnResolver.py](src/nate2_scripts/console/arnResolver.py) — one class, ~15 `parse_*` methods for every ARN service
- [nameResolver.py](src/nate2_scripts/console/nameResolver.py) — one class, parallel cross-service/region name lookup
- [resourceIdResolver.py](src/nate2_scripts/console/resourceIdResolver.py) — one class, `match` over every id prefix

The new target shape already exists in [resolvers/s3.py](src/nate2_scripts/console/resolvers/s3.py):
a `Resolver` ABC ([resolvers/__init__.py](src/nate2_scripts/console/resolvers/__init__.py))
with four dimensions — `try_resolve_name`, `try_resolve_arn`, `try_resolve_service`,
`try_resolve_id` — and **one class per service** (`S3Resolver`) implementing all four,
each returning `None` when the input isn't theirs.

Goal: move all existing resolution logic into per-service `Resolver` subclasses following
the `S3Resolver` pattern, wire a dispatcher that iterates them, and delete the three old
monolith files. **Functionality stays the same** (same URLs, same parallel name search,
same priority tie-breaking).

## Key design points (settled)

- **Granularity:** one class per service, splitting the ec2 namespace into a separate
  `Ec2Resolver` (instances, AMIs, volumes, snapshots, launch templates, ENIs, security
  groups) and `VpcResolver` (vpc, subnet, route table, nat gateway, acl).
- **Static-only services** (cost, support, athena, ecr, bedrock, config, controltower,
  cognito, cloudfront, route53, kms-link, storagegateway, fsx, ssm, parameter, cloudtrail,
  tennex): each gets its **own** `Resolver` subclass. **No shared mixin/base** — every class
  implements all four methods explicitly, with the three unused ones written out as
  `return None`. `sns`, `sqs`, `ecs`, `eks` (and every other service) stay their own separate
  classes; none are combined.
- **Name lookup stays parallel + priority-ordered:** logs > s3 > ec2 > cloudformation >
  lambda (existing order in [nameResolver.py:24](src/nate2_scripts/console/nameResolver.py#L24)).
- **URL wrapping:** resolvers return a **bare host+path** (e.g. `console.aws.amazon.com/s3/...`
  for global, `{region}.console.aws.amazon.com/...` for regional), exactly as `S3Resolver`
  does. The **dispatcher** prepends `https://{mdn}`. `mdn` (multisession domain name) stays
  out of `Context` — it's the dispatcher's concern.

## Context object

Extend `Context` in [resolvers/__init__.py](src/nate2_scripts/console/resolvers/__init__.py)
so resolvers have what the monoliths used to pull from constructor args:

```python
class Context:
    session: boto3.Session      # built from assumed creds in main()
    default_region: str
    regions: list[str]          # NEW — from RegionCache, for multi-region name/id search
    current_account: str        # for arn.account access checks
    profile: str
```

`session` replaces the bare `boto3.client(...)` calls in the old resolvers — every
resolver uses `context.session.client(svc, region_name=region)`. In
[console/__init__.py](src/nate2_scripts/console/__init__.py) `main()`, build the session
from the `creds` already obtained via `get_credentials()` and populate `Context`.

## New files (under `resolvers/`)

Resource-resolving services (port the matching `parse_*` / `_resolve_*` bodies verbatim,
swapping `boto3.client` → `context.session.client` and dropping the `https://{mdn}` prefix
from returned strings so the dispatcher adds it):

| File | Class | Dimensions ported from |
|---|---|---|
| `ec2.py` | `Ec2Resolver` | arn `instance`; ids `i-,sg-,ami-,lt-,vol-,snap-,eni-`; name tag:Name; service `ec2`,`sg`,`ami`,`elb`* |
| `vpc.py` | `VpcResolver` | arn `subnet`,`natgateway`; ids `vpc-,subnet-,rtb-,nat-`; service `vpc`,`subnet`,`acl` |
| `iam.py` | `IamResolver` | arn `role`,`user`; ids `role/`,`usr/`; service `iam` (global, us-east-1) |
| `lambda.py` | `LambdaResolver` | arn `function`; name function; service `lambda` |
| `logs.py` | `LogsResolver` | arn `log-group`; name log-group; service `logs`,`cw`,`cloudwatch` |
| `cloudformation.py` | `CloudFormationResolver` | name stack; service `cf`,`cloudformation` |
| `rds.py` | `RdsResolver` | arn `db`,`cluster`; service `rds` |
| `secretsmanager.py` | `SecretsManagerResolver` | arn `secret`; service `sm`,`secretsmanager`,`secretmanager` |
| `ecs.py` | `EcsResolver` | arn `cluster`,`service`,`task`,`task-definition`; service `ecs` |
| `eks.py` | `EksResolver` | arn `cluster`; service `eks` |
| `sns.py` | `SnsResolver` | arn topic; service `sns` |
| `sqs.py` | `SqsResolver` | arn queue; service `sqs` |
| `batch.py` | `BatchResolver` | arn `job-queue`,`compute-environment`,`job-definition`,`job`; service `batch` |
| `dynamodb.py` | `DynamoDbResolver` | arn `table`; service `dynamo` |
| `stepfunctions.py` | `StepFunctionsResolver` | arn `stateMachine`,`execution`; service `step` |
| `elb.py` | `ElbResolver` | arn `loadbalancer`,`targetgroup`; service `elb` |

*`elb`/`acl`/`ami`/`sg` service keywords are static list-view links — keep them on the
resolver that owns that resource where natural, or in a static resolver; either is fine.

Static-only resolvers (one class each): `cost.py`, `support.py`, `athena.py`, `ecr.py`,
`bedrock.py`, `config.py`, `controltower.py`, `cognito.py`, `cloudfront.py`, `route53.py`,
`kms.py`, `storagegateway.py`, `fsx.py`, `ssm.py`, `cloudtrail.py`, `tennex.py` — seeded
from the remaining entries of `_get_services()` in
[destitationResolver.py:60](src/nate2_scripts/console/destitationResolver.py#L60).
**No shared base/mixin.** Each class implements `try_resolve_service` (matching its own
keyword aliases) and writes out `try_resolve_name`, `try_resolve_arn`, `try_resolve_id` as
explicit `return None`.

## Dispatcher

Rewrite [destitationResolver.py](src/nate2_scripts/console/destitationResolver.py)
`parse_destination` (keep `DestinationResolver` name + `get_service_list()` so
[console/__init__.py](src/nate2_scripts/console/__init__.py) callers are untouched) to hold
an ordered `list[Resolver]` and dispatch:

1. Empty arg → `https://{mdn}{default_region}.console.aws.amazon.com/`.
2. `Arn.try_parse(arg)` succeeds → **ARN input is terminal.** Try each resolver's
   `try_resolve_arn`; return the first non-None. If none resolve it, print an
   ARN-specific error to stderr and `sys.exit(1)` — **do not** fall through to the
   service/id/name steps below.
3. `try_resolve_service(ctx, arg, search)` across resolvers → first non-None.
4. Else `try_resolve_id(ctx, arg)` across resolvers → first non-None.
5. Else **name** search: run each name-capable resolver's `try_resolve_name` concurrently
   (`ThreadPoolExecutor`, reuse `MAX_THREADS`), collect by each resolver's priority index,
   return the lowest-priority winner — preserving [nameResolver.py:33-48](src/nate2_scripts/console/nameResolver.py#L33-L48).
   Each regional resolver loops `context.regions` internally.
6. None matched → same stderr error + `sys.exit(1)`.

Every returned bare path is wrapped as `https://{mdn}{path}` before returning.
`get_service_list()` returns the union of every resolver's known service keywords (for
argcomplete in [console/__init__.py:129](src/nate2_scripts/console/__init__.py#L129)).

- **`search` is a real second positional CLI arg.** Add a `search` positional (`nargs="?"`,
  default `""`) to `parse_args` in
  [console/__init__.py:115](src/nate2_scripts/console/__init__.py#L115), pass it into
  `parse_destination(service, region, search)`, and thread it through to
  `try_resolve_service` and `try_resolve_name`. Usage becomes `console <service> <search>`
  (e.g. `console ec2 <filter>`).
- **Apply `search` to the URL when given and the target console supports it.** When
  `search` is non-empty and the resolver's console view accepts a filter/search query
  param, the resolver appends it (URL-encoded) so the console opens pre-filtered — e.g.
  EC2 instances `...#Instances:search=<term>`, Lambda `...#/functions?fo=and&k0=...&v0=<term>`,
  CloudWatch log-groups list, S3 object/bucket search, etc. Where a console view has no such
  param (as noted in the `S3Resolver` comments), the resolver ignores `search` and returns
  the plain URL. Each ported resolver decides per-view; an empty `search` always yields the
  current (unfiltered) URL, preserving today's behavior. The exact query-param syntax per
  service is verified against the live console during implementation.
- `try_resolve_*` methods **return `None`** on any failure (matching `S3Resolver`), rather
  than `sys.exit` mid-resolve as the old monoliths did. Net effect: the final "not found"
  error is emitted once by the dispatcher. This drops a few service-specific error strings
  (e.g. "current account X cannot access Y") in favor of the unified message — a deliberate
  simplification consistent with the target pattern.

## Cleanup

Delete [arnResolver.py](src/nate2_scripts/console/arnResolver.py),
[nameResolver.py](src/nate2_scripts/console/nameResolver.py),
[resourceIdResolver.py](src/nate2_scripts/console/resourceIdResolver.py) once their logic
is ported. Move the `split()` helper from arnResolver into `resolvers/__init__.py` (shared
by several resolvers). Keep `Arn` in `resolvers/__init__.py` as the single ARN parser
(replaces `ParsedArn` + `split`-based parsing).

## Verification

No test suite exists, so verify by running the CLI against a real profile:

1. `asp <profile>` then reinstall/link: `pip install -e .` (or `uv pip install -e .`).
2. Exercise each dimension and confirm the same URL opens as before the refactor:
   - **service keyword:** `console s3`, `console ec2`, `console cost`, `console logs`, `console sm`
   - **arn:** `console arn:aws:s3:::<bucket>`, `console arn:aws:lambda:us-east-1:<acct>:function:<fn>`,
     `console arn:aws:iam::<acct>:role/<role>`
   - **resource id:** `console i-<id>`, `console vpc-<id>`, `console subnet-<id>`
   - **name:** `console <bucket-name>`, `console <stack-name>`, `console <lambda-name>`,
     `console <ec2-Name-tag>` — confirm priority tie-break still favors logs > s3 > ec2 > cfn > lambda.
   - **search arg:** `console ec2 <term>` — confirm the second positional is accepted and
     threaded through (no crash; ignored by resolvers that don't use it yet).
   - **empty:** `console` → region landing page.
   - **unknown:** `console zzzzz` → stderr "Unknown service" + exit 1.
3. Confirm argcomplete still lists services: `console <TAB>` (or inspect `get_service_list()`).
4. Spot-check that the multisession domain prefix (`{mdn}`) still appears in generated URLs
   when a multi-session hash is cached (the `-f` path vs cached path in
   [console/__init__.py:174-185](src/nate2_scripts/console/__init__.py#L174-L185)).
