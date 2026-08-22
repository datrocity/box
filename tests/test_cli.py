import box
from box.__main__ import main


def test_skills_path_points_to_shipped_dir():
    p = box.skills_path()
    assert p.is_dir()
    assert (p / "using-box.md").is_file()


def test_install_skills_copies_files(tmp_path, capsys):
    dest = tmp_path / "skills"
    exit_code = main(["install-skills", "--dest", str(dest)])
    assert exit_code == 0
    assert (dest / "using-box.md").is_file()
    out = capsys.readouterr().out
    assert "using-box.md" in out


def test_install_skills_default_dest_expands_tilde(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("HOME", str(tmp_path))
    exit_code = main(["install-skills"])
    assert exit_code == 0
    assert (tmp_path / ".claude" / "skills" / "box" / "using-box.md").is_file()
