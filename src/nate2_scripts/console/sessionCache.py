from pathlib import Path
import os
import json
import time
from datetime import datetime, timezone


class SessionCache:
    """Persists AWS console federation session hashes to avoid redundant federated sign-ins.

    The cache is stored as a JSON file at XDG_STATE_HOME/console-sessions.json
    (defaulting to ~/.local/state/console-sessions.json). Each entry maps an AWS
    profile name to its federated_at timestamp and session hash.
    """

    # Resolve the cache file path from XDG_STATE_HOME or the default ~/.local/state
    PATH = (
        Path(os.environ.get("XDG_STATE_HOME", Path.home() / ".local" / "state"))
        / "console-sessions.json"
    )

    def _load_cache(self) -> dict:
        """Read the cache file and return its contents as a dict.

        Returns an empty dict if the file does not exist or is unreadable/corrupt.
        """
        if self.PATH.exists():
            try:
                return json.loads(self.PATH.read_text())
            except (json.JSONDecodeError, OSError):
                return {}
        return {}

    def _save_cache(self, cache: dict) -> None:
        """Persist the cache dict to disk, creating parent directories as needed."""
        self.PATH.parent.mkdir(parents=True, exist_ok=True)
        self.PATH.write_text(json.dumps(cache))

    def get_session_hash(self, profile: str, creds: dict) -> None | str:
        """Return the cached session hash for a profile if it is still valid.

        A cached entry is considered invalid (returns None) when:
        - No entry exists for the profile.
        - The STS credential Expiration timestamp has already passed.
        - The entry was federated more than 11 hours ago (AWS console session limit).

        Args:
            profile: The AWS profile name used to look up the cache entry.
            creds: STS credentials dict; may contain an "Expiration" ISO-8601 string.

        Returns:
            The cached session hash string, or None if the cache is missing/expired.
        """
        cache = self._load_cache()
        entry = cache.get(profile)

        if not entry:
            return None

        # Honour the STS credential expiration if present
        expiration = creds.get("Expiration")
        if expiration:
            try:
                exp_time = datetime.fromisoformat(expiration.replace("Z", "+00:00"))
                if datetime.now(timezone.utc) >= exp_time:
                    return None
            except ValueError:
                return None

        # AWS federated console sessions expire after 12 hours; evict after 11 to be safe
        if time.time() - entry["federated_at"] > 11 * 3600:
            return None

        return entry.get("hash")

    def record_valid_hash(self, profile: str, hash: str) -> None:
        """Store a newly obtained session hash and evict entries older than 12 hours.

        Args:
            profile: The AWS profile name to associate with the hash.
            hash: The session hash returned after a successful federation sign-in.
        """
        cache = self._load_cache()
        # Record the new entry with the current epoch time
        cache[profile] = {"federated_at": time.time(), "hash": hash}
        # Prune stale entries to keep the cache file small
        cache = {
            k: v
            for k, v in cache.items()
            if time.time() - v.get("federated_at", 0) < 12 * 3600
        }
        self._save_cache(cache)

    def reset(self) -> None:
        """Clear the entire session cache."""
        self._save_cache({})