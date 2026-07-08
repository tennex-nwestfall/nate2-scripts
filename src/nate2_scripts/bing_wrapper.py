"""PTY wrapper for cdk that plays a sound when (y/n) prompts appear."""

import fcntl
import os
import select
import signal
import struct
import subprocess
import sys
import termios
import tty
import argparse

# _PATTERN = b"(y/n)"
# _WINDOW = len(_PATTERN) * 2


def _get_winsize(fd: int) -> bytes:
    return fcntl.ioctl(fd, termios.TIOCGWINSZ, b"\x00" * 8)


def _set_winsize(fd: int, winsize: bytes) -> None:
    fcntl.ioctl(fd, termios.TIOCSWINSZ, winsize)


def run(args: argparse.Namespace) -> None:
    patterns = [p.encode() for p in args.patterns] if args.patterns else []
    window = max(map(len, patterns)) * 2 if patterns else 1
    # Capture real terminal dimensions before creating the PTY.
    # pty.spawn() leaves the PTY at {0,0,0,0}, which makes CDK format
    # output to width 1. Using os.openpty() lets us set the size before
    # forking so cdk reads correct dimensions from its very first TIOCGWINSZ.
    try:
        winsize = _get_winsize(sys.stdout.fileno())
    except OSError:
        winsize = struct.pack("HHHH", 24, 80, 0, 0)

    master_fd, slave_fd = os.openpty()
    _set_winsize(master_fd, winsize)

    pid = os.fork()
    if pid == 0:
        # ---- child ----
        os.close(master_fd)
        os.setsid()
        # Acquire slave as the controlling terminal.
        fcntl.ioctl(slave_fd, termios.TIOCSCTTY, 0)
        for fd in (0, 1, 2):
            os.dup2(slave_fd, fd)
        if slave_fd > 2:
            os.close(slave_fd)
        os.execvp(args.command[0], args.command)
        os._exit(1)

    # ---- parent ----
    os.close(slave_fd)

    # Propagate terminal resizes to the child (also sends SIGWINCH to it).
    def _sigwinch(signum: int, frame) -> None:
        try:
            _set_winsize(master_fd, _get_winsize(sys.stdout.fileno()))
        except OSError:
            pass

    signal.signal(signal.SIGWINCH, _sigwinch)

    stdin_fd = sys.stdin.fileno()
    old_settings = None
    try:
        old_settings = termios.tcgetattr(stdin_fd)
        tty.setraw(stdin_fd)
    except termios.error:
        pass

    buf = b""
    try:
        while True:
            try:
                r, _, _ = select.select([master_fd, stdin_fd], [], [])
            except (OSError, ValueError):
                break

            if master_fd in r:
                try:
                    data = os.read(master_fd, 1024)
                except OSError:
                    break
                if not data:
                    break

                check = buf + data
                for pattern in patterns:
                    if pattern in check:
                        subprocess.Popen(["afplay", args.sound_pattern])
                        buf = b""
                        break

                buf = check[-window:]

                sys.stdout.buffer.write(data)
                sys.stdout.buffer.flush()

            if stdin_fd in r:
                try:
                    data = os.read(stdin_fd, 1024)
                except OSError:
                    break
                if data:
                    try:
                        os.write(master_fd, data)
                    except OSError:
                        break
    finally:
        if old_settings is not None:
            try:
                termios.tcsetattr(stdin_fd, termios.TCSADRAIN, old_settings)
            except termios.error:
                pass

    _, status = os.waitpid(pid, 0)

    if args.end:
        subprocess.Popen(["afplay", args.sound_end])
    if os.WIFEXITED(status):
        sys.exit(os.WEXITSTATUS(status))
    elif os.WIFSIGNALED(status):
        sys.exit(128 + os.WTERMSIG(status))
    else:
        sys.exit(1)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="PTY wrapper for cdk that plays a sound when (y/n) prompts appear."
    )
    parser.add_argument("command", nargs="*", help="Command to run")
    parser.add_argument(
        "--end", help="make sound at end of command", action="store_true"
    )
    parser.add_argument(
        "--pattern",
        help="make sound when pattern in seen",
        type=str,
        action="append",
        dest="patterns",
    )
    parser.add_argument(
        "--sound-end",
        help="change the sound at end of command",
        type=str,
        default="/System/Library/Sounds/Glass.aiff",
    )
    parser.add_argument(
        "--sound-pattern",
        help="change the sound when pattern is seen",
        type=str,
        default="/System/Library/Sounds/Glass.aiff",
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    run(args)


if __name__ == "__main__":
    main()
