"""Lineage metadata gatherers.

Each function returns a dict fragment ready to be added to a Manifest section.
None of these raise; missing information (no git, no user) yields empty or
best-effort output.
"""

import getpass
import subprocess
from datetime import datetime, timezone


def timestamp_source():
    """Return the current UTC time as an ISO 8601 string.

    Returns
    -------
    dict
        ``{"created_at": "<ISO 8601 UTC ending in Z>"}``.
    """
    now = datetime.now(timezone.utc).isoformat()
    if now.endswith("+00:00"):
        now = now[: -len("+00:00")] + "Z"
    return {"created_at": now}


def author_source():
    """Return the current OS user.

    Returns
    -------
    dict
        ``{"author": "<username>"}``. Falls back to ``"unknown"`` on failure.
    """
    try:
        return {"author": getpass.getuser()}
    except Exception:
        return {"author": "unknown"}


def _git(args, cwd):
    return subprocess.check_output(
        ["git", *args], cwd=cwd, stderr=subprocess.DEVNULL, text=True
    ).strip()


def git_source(cwd=None):
    """Return git information for the repo containing ``cwd``.

    Parameters
    ----------
    cwd : str or pathlib.Path, optional
        Directory to run git from. Defaults to the process CWD.

    Returns
    -------
    dict
        Empty ``{}`` if not in a git repo or git is unavailable. Otherwise
        ``{"code": {"git_sha": str, "dirty": bool, "git_remote": str or None}}``.
    """
    try:
        sha = _git(["rev-parse", "HEAD"], cwd=cwd)
    except (subprocess.CalledProcessError, FileNotFoundError):
        return {}
    try:
        status = _git(["status", "--porcelain"], cwd=cwd)
        dirty = bool(status)
    except subprocess.CalledProcessError:
        dirty = False
    try:
        remote = _git(["config", "--get", "remote.origin.url"], cwd=cwd) or None
    except subprocess.CalledProcessError:
        remote = None
    return {"code": {"git_sha": sha, "dirty": dirty, "git_remote": remote}}
