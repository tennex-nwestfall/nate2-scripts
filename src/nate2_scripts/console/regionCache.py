import json
import os
from pathlib import Path

DEFAULT_REGION = "us-east-1"
DEFAULT_REGIONS = ["us-east-1", "us-east-2", "us-west-1", "us-west-2"]


class RegionCache:
    """Loads and persists the list of AWS regions and the default region.

    Configuration is read from XDG_STATE_HOME/console-regions.json
    (defaulting to ~/.local/state/console-regions.json). If the file is
    absent or invalid it is recreated with the built-in defaults.
    """

    # Resolve the config file path from XDG_STATE_HOME or the default ~/.local/state
    PATH = (
        Path(os.environ.get("XDG_STATE_HOME", Path.home() / ".local" / "state"))
        / "console-regions.json"
    )

    # Class-level defaults; overwritten per-instance when the config file is loaded
    regions: list[str] = DEFAULT_REGIONS
    default: str = DEFAULT_REGION

    def __init__(self):
        """Load region config from disk, falling back to defaults if unavailable."""
        if self.PATH.exists():
            try:
                file = json.loads(self.PATH.read_text())
                if file.get("regions"):
                    self.regions = file["regions"]
                if file.get("default"):
                    self.default = file["default"]
                return
            except (json.JSONDecodeError, OSError):
                pass

        # File is missing or corrupt — write defaults so subsequent reads succeed
        self.PATH.parent.mkdir(parents=True, exist_ok=True)
        self.PATH.write_text(json.dumps({"regions": DEFAULT_REGIONS, "default": DEFAULT_REGION}))

    def get_regions(self) -> list[str]:
        """Return the list of configured AWS regions."""
        return self.regions

    def get_default_region(self) -> str:
        """Return the default AWS region."""
        return self.default