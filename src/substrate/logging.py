import sys


def log_info(message: str) -> None:
    sys.stdout.write(f"[INFO] {message}\n")


def log_error(message: str) -> None:
    sys.stderr.write(f"[ERROR] {message}\n")
