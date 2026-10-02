import json
import os
import time
from pathlib import Path


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

    def get_session_hash(self, profile: str) -> None | str:
        """Return the cached session hash for a profile if it is still valid.

        A cached entry is considered invalid (returns None) when:
        - No entry exists for the profile.
        - The entry was federated more than 59 minutes ago (AWS console session limit).

        Args:
            profile: The AWS profile name used to look up the cache entry.

        Returns:
            The cached session hash string, or None if the cache is missing/expired.
        """
        cache = self._load_cache()
        entry = cache.get(profile)

        if not entry:
            return None

        if time.time() - entry["federated_at"] > 3600 - 60:  # expire after 59 minutes
            return None

        return entry.get("hash")

    def record_valid_hash(self, profile: str, hash: str) -> None:
        """Store a newly obtained session hash and evict entries older than 59 minutes.

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
            if time.time() - v.get("federated_at", 0) < 3600 - 60
        }
        self._save_cache(cache)

    def reset(self) -> None:
        """Clear the entire session cache."""
        self._save_cache({})
