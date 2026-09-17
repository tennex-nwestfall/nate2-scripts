import re
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import time
from pathlib import Path

SUPPORTED_BROWSERS = {
    "com.google.chrome": "chrome",
    "org.mozilla.firefox": "firefox",
}

WAIT_SECONDS = 10  # Time to wait for the browser to open and record the hash

ONLY_HASH_SECONDS = 5  # Time to wait for the browser to open and record the hash, but only return the hash if found


class HashGrabber:
    @staticmethod
    def _get_default_browser() -> str:
        """Return 'chrome' or 'firefox'. Prints to stderr and exits for unsupported browsers."""
        result = subprocess.run(
            [
                "defaults",
                "read",
                str(
                    Path.home()
                    / "Library/Preferences/com.apple.LaunchServices/com.apple.launchservices.secure"
                ),
                "LSHandlers",
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        # Find the block containing LSHandlerURLScheme = https and extract LSHandlerRoleAll
        match = re.search(
            r'LSHandlerRoleAll\s*=\s*"([^"]+)";\s*LSHandlerURLScheme\s*=\s*https;',
            result.stdout,
        )
        bundle_id = match.group(1).lower() if match else ""

        if bundle_id in SUPPORTED_BROWSERS:
            return SUPPORTED_BROWSERS[bundle_id]

        print(
            f"Unsupported default browser: {bundle_id or 'unknown'}. Only Chrome and Firefox are supported.",
            file=sys.stderr,
        )
        sys.exit(1)

    @staticmethod
    def get_hash(id: str, time_started: float) -> str:
        """Search the default browser's history for the most recent AWS console URL matching the account ID.

        Polls up to WAIT_SECONDS for a URL visited after time_started.
        Returns the hash portion from URLs like https://{id}-{hash}.{region}.console.aws.amazon.com/*
        or empty string for URLs like https://{region}.console.aws.amazon.com/*.

        Raises RuntimeError if no matching URL is found within the timeout.
        """
        default = HashGrabber._get_default_browser()

        pattern_with_hash = re.compile(
            rf"https://{re.escape(id)}-([a-z0-9]+)\.[a-z0-9-]+\.console\.aws\.amazon\.com"
        )
        pattern_without_hash = re.compile(
            r"https://[a-z0-9-]+\.console\.aws\.amazon\.com"
        )

        fetch_fn = {
            "chrome": HashGrabber._chrome_history,
            "firefox": HashGrabber._firefox_history,
        }[default]

        deadline = time_started + WAIT_SECONDS
        hash_only_deadline = time_started + ONLY_HASH_SECONDS
        time.sleep(0.5)

        while time.time() < deadline:
            try:
                print("-----------------------------------------")
                for url, visit_time in fetch_fn(id, time_started):
                    print(url, visit_time)
                    match = pattern_with_hash.search(url)
                    if match:
                        return match.group(1)
                    elif (
                        time.time() >= hash_only_deadline
                        and pattern_without_hash.search(url)
                    ):
                        return ""
            except (OSError, sqlite3.Error):
                pass

            time.sleep(0.5)

        raise RuntimeError(
            f"No AWS console URL found for account {id} within {WAIT_SECONDS}s"
        )

    @staticmethod
    def _chrome_history(
        account_id: str, time_started: float
    ) -> list[tuple[str, float]]:
        db_path = HashGrabber._chrome_sqlite_path()
        if not db_path.exists():
            return []

        # Chrome stores time as microseconds since 1601-01-01
        chrome_epoch_offset = 11644473600
        chrome_time_started = int((time_started + chrome_epoch_offset) * 1_000_000)

        with tempfile.NamedTemporaryFile(suffix=".sqlite") as tmp:
            shutil.copy2(db_path, tmp.name)
            conn = sqlite3.connect(tmp.name)
            try:
                cursor = conn.execute(
                    """
                    SELECT url, last_visit_time
                    FROM urls
                    WHERE (url LIKE ? OR url LIKE '%console.aws.amazon.com%')
                      AND last_visit_time > ?
                    ORDER BY last_visit_time DESC
                    LIMIT 10
                    """,
                    (f"%{account_id}%console.aws.amazon.com%", chrome_time_started),
                )
                return cursor.fetchall()
            finally:
                conn.close()

    @staticmethod
    def _firefox_history(
        account_id: str, time_started: float
    ) -> list[tuple[str, float]]:
        db_path = HashGrabber._firefox_sqlite_path()
        if not db_path or not db_path.exists():
            return []

        # Firefox stores time as microseconds since Unix epoch
        firefox_time_started = int(time_started * 1_000_000)

        with tempfile.NamedTemporaryFile(suffix=".sqlite") as tmp:
            shutil.copy2(db_path, tmp.name)
            conn = sqlite3.connect(tmp.name)
            try:
                cursor = conn.execute(
                    """
                    SELECT p.url, v.visit_date
                    FROM moz_places p
                    JOIN moz_historyvisits v ON v.place_id = p.id
                    WHERE (p.url LIKE ? OR p.url LIKE '%console.aws.amazon.com%')
                      AND v.visit_date > ?
                    ORDER BY v.visit_date DESC
                    LIMIT 10
                    """,
                    (f"%{account_id}%console.aws.amazon.com%", firefox_time_started),
                )
                return cursor.fetchall()
            finally:
                conn.close()

    @staticmethod
    def _chrome_sqlite_path() -> Path:
        return Path.home() / "Library/Application Support/Google/Chrome/Default/History"

    @staticmethod
    def _firefox_sqlite_path() -> Path | None:
        profiles_dir = Path.home() / "Library/Application Support/Firefox/Profiles"
        if not profiles_dir.exists():
            return None

        for pattern in ["*.default-release", "*.default"]:
            matches = list(profiles_dir.glob(pattern))
            if matches:
                db = matches[0] / "places.sqlite"
                if db.exists():
                    return db

        for profile in profiles_dir.iterdir():
            if profile.is_dir():
                db = profile / "places.sqlite"
                if db.exists():
                    return db

        return None
