import subprocess

from box.manifest.lineage import author_source, git_source, timestamp_source


def test_timestamp_source_returns_iso8601_utc():
    out = timestamp_source()
    assert "created_at" in out
    ts = out["created_at"]
    assert ts.endswith("Z")
    assert "T" in ts


def test_author_source_returns_dict_with_author():
    out = author_source()
    assert "author" in out
    assert isinstance(out["author"], str)
    assert out["author"]


def test_git_source_outside_repo_returns_empty(tmp_path):
    assert git_source(cwd=tmp_path) == {}


def test_git_source_inside_repo_has_sha(tmp_path):
    subprocess.run(
        ["git", "init", "-b", "main"],
        cwd=tmp_path,
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    subprocess.run(
        [
            "git",
            "-c",
            "user.email=t@t",
            "-c",
            "user.name=t",
            "commit",
            "--allow-empty",
            "-m",
            "init",
        ],
        cwd=tmp_path,
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    out = git_source(cwd=tmp_path)
    assert "code" in out
    code = out["code"]
    assert "git_sha" in code
    assert len(code["git_sha"]) == 40
    assert code["dirty"] is False
    assert code["git_remote"] is None


def test_git_source_dirty_flag(tmp_path):
    subprocess.run(
        ["git", "init", "-b", "main"],
        cwd=tmp_path,
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    subprocess.run(
        [
            "git",
            "-c",
            "user.email=t@t",
            "-c",
            "user.name=t",
            "commit",
            "--allow-empty",
            "-m",
            "init",
        ],
        cwd=tmp_path,
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    (tmp_path / "new.txt").write_text("hi")

    out = git_source(cwd=tmp_path)
    assert out["code"]["dirty"] is True
