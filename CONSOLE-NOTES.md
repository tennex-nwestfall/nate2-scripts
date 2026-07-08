# Console Script — Session Investigation Notes

## The Problem

Running `co lambda` then `co ec2` (same account) signs out the Lambda tab.

## Root Cause

The session cache keys by `AccessKeyId`, which rotates every time Okta refreshes STS credentials (~1 hour). After rotation, the cache misses and re-federates, creating a new browser session that invalidates the previous one.

## How Federation Works

1. CLI credentials (AccessKeyId/SecretAccessKey/SessionToken) are sent to `signin.aws.amazon.com/federation?Action=getSigninToken` → returns a one-time SigninToken
2. Browser opens `signin.aws.amazon.com/federation?Action=login&SigninToken=...` → AWS creates a browser console session (cookies) and redirects to destination
3. The browser session lasts **12 hours** (script uses 11hr buffer)
4. Each `Action=login` call for the **same account** replaces the previous session → other tabs for that account become invalid
5. Different accounts get isolated sessions (multi-session console, 2024+) — no conflict

## Key Findings

- **Federation does NOT require existing browser cookies** — it creates a session from scratch using CLI creds
- **Multi-session console** isolates different accounts but NOT multiple sessions within the same account
- **Re-federating same account** kills existing tabs for that account
- **The account-specific URL hash** (e.g., `lh2nfmmd` in `905502466771-lh2nfmmd.us-east-1.console.aws.amazon.com`) is per-browser-session, changes on every sign-in, and is NOT retrievable via any AWS API. It's assigned client-side by JavaScript after login.
- **The hash is NOT cacheable** — it's tied to the browser session lifetime, not the account
- **DNS lookups** won't help — `*.console.aws.amazon.com` is a wildcard record; the hash is resolved by cookies/frontend

## The Fix

Key the session cache by **profile name** (or account ID) instead of `AccessKeyId`:

- The browser session is tied to the account, not the specific credential set
- Even after Okta rotates creds (new AccessKeyId), the browser session from the previous federation is still alive
- Cache should prevent re-federation as long as it's within 11 hours of the last federation for that profile

## Approaches Considered & Rejected

| Approach | Why rejected |
|----------|-------------|
| Always federate | Signs out other tabs for same account |
| Account-specific URL hash (cached) | Hash is per-session, not stable |
| Selenium/Playwright to discover hash | Hash from WebDriver session ≠ real browser session |
| AppleScript to read browser URL | Hash is session-bound, same lifecycle as session cache |
| Browser profiles (Chrome/Firefox) | Still can't open 2nd tab without re-federation within same profile |
| DNS lookup for hash | Wildcard DNS — hash is cookie-routed, not DNS-routed |
| Capture hash from federation redirect | Redirect goes to the generic URL; hash rewrite is client-side JS |

## Current Architecture

```
co <service>
  → check AWS_PROFILE is set
  → parse destination URL
  → get CLI creds (aws configure export-credentials)
  → check session cache
    → valid: open raw URL (webbrowser.open)
    → expired/missing: federate → open federation URL → record cache
```

## What Needs to Change

```python
# Before (buggy): keyed by AccessKeyId which rotates
cache[creds["AccessKeyId"]] = {"federated_at": time.time()}

# After: keyed by profile name which is stable
cache[profile_name] = {"federated_at": time.time()}
```

This ensures that within the 11-hour window, `co` opens the raw URL without re-federating, keeping other same-account tabs alive.
