import sys

if sys.platform != "darwin":
    raise RuntimeError("nate2-scripts only supports macOS")
