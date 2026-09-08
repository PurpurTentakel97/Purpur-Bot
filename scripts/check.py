import subprocess
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
_NOCOMMIT_SCAN_DIRS = ("src", "scripts")

_RED = "\033[31m"
_GREEN = "\033[32m"
_RESET = "\033[0m"


def run(cmd: list[str]) -> None:
    print(f"Running: `{' '.join(cmd)}`")
    result = subprocess.run(cmd)
    if result.returncode != 0:
        sys.exit(result.returncode)


def run_uv(args: list[str]) -> None:
    cmd = ["uv", "run", "--active"] + args
    run(cmd)


def check_nocommit_markers() -> None:
    print("Running: `nocommit marker check`")

    needle = "nocommit"
    checker = Path(__file__).resolve()
    hits: list[str] = []

    for directory in _NOCOMMIT_SCAN_DIRS:
        for path in sorted((_REPO_ROOT / directory).rglob("*")):
            if not path.is_file() or path == checker or "__pycache__" in path.parts:
                continue
            try:
                content = path.read_text(encoding="utf-8")
            except (UnicodeDecodeError, OSError):
                continue
            for number, line in enumerate(content.splitlines(), start=1):
                if needle in line.lower():
                    hits.append(f"{path.relative_to(_REPO_ROOT).as_posix()}:{number}: {line.strip()}")

    if hits:
        print(f"{_RED}Error{_RESET}: found {len(hits)} forbidden '{needle}' marker(s):", file=sys.stderr)
        for hit in hits:
            print(f"  {hit}", file=sys.stderr)
        sys.exit(1)

    print(f"{_GREEN}Pass{_RESET}: no '{needle}' markers found")


def main() -> None:
    args = sys.argv[1:]

    if len(args) > 1 or (args and args[0] not in ("--fix", "--test")):
        print(f"Usage: {args[0]} [--fix/--test]", file=sys.stderr)
        print(args, file=sys.stderr)
        sys.exit(2)

    if "--test" in args:
        run_uv(
            [
                "pytest",
                "-v",
                "--cov=src/",
                "--cov-branch",
                "--cov-report=term-missing:skip-covered",
                "--cov-report=html:coverage_html",
            ]
        )
    elif "--fix" in args:
        run_uv(["ruff", "format"])
        run_uv(["ruff", "check", "--fix"])
        run_uv(["pyright"])
    else:
        run_uv(["ruff", "format", "--check"])
        run_uv(["ruff", "check"])
        run_uv(["pyright"])
        check_nocommit_markers()


if __name__ == "__main__":
    main()
