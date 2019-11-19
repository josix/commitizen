import os
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Optional, List

from commitizen import cmd


def tag(tag: str):
    c = cmd.run(f"git tag {tag}")
    return c


def commit(message: str, args=""):
    f = NamedTemporaryFile("wb", delete=False)
    f.write(message.encode("utf-8"))
    f.close()
    c = cmd.run(f"git commit {args} -F {f.name}")
    os.unlink(f.name)
    return c


def get_commits(
    start: str,
    end: str = "HEAD",
    *,
    from_beginning: bool = False,
    log_format: str = "%s%n%b",
) -> list:
    delimiter = '"----------commit-delimiter----------"'
    git_log_cmd = f"git log --pretty={log_format}{delimiter}"

    c = cmd.run(f"{git_log_cmd} {start}...{end}")

    if from_beginning:
        c = cmd.run(f"{git_log_cmd} {end}")

    if not c.out:
        return []
    return [commit.strip() for commit in c.out.split(delimiter) if commit.strip()]


def tag_exist(tag: str) -> bool:
    c = cmd.run(f"git tag --list {tag}")
    return tag in c.out


def is_staging_clean() -> bool:
    """Check if staing is clean"""
    c = cmd.run("git diff --no-ext-diff --name-only")
    c_cached = cmd.run("git diff --no-ext-diff --cached --name-only")
    return not (bool(c.out) or bool(c_cached.out))


def get_latest_tag() -> Optional[str]:
    c = cmd.run("git describe --abbrev=0 --tags")
    if c.err:
        return None
    return c.out.strip()


def get_all_tags() -> Optional[List[str]]:
    c = cmd.run("git tag --list")
    if c.err:
        return []
    return [tag.strip() for tag in c.out.split("\n") if tag.strip()]


def find_git_project_root() -> Optional[Path]:
    c = cmd.run("git rev-parse --show-toplevel")
    if not c.err:
        return Path(c.out.strip())
    return None
