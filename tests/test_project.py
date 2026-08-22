import pandas as pd
import pandas.testing as pdt
import pytest

from box.errors import ArtifactNotFound
from box.project import Project


def test_project_creates_datastore_root(tmp_path):
    Project("walker", datastore=str(tmp_path / "catalog"))
    assert (tmp_path / "catalog" / "walker").is_dir()


def test_project_save_and_load(tmp_path):
    proj = Project("walker", datastore=str(tmp_path / "catalog"))
    df = pd.DataFrame({"a": [1, 2, 3]})
    proj.save(df, "processed_input")

    back = proj.load("processed_input")
    pdt.assert_frame_equal(back, df)


def test_project_save_writes_to_global_folder(tmp_path):
    proj = Project("walker", datastore=str(tmp_path / "catalog"))
    proj.save({"k": "v"}, "config")
    assert (tmp_path / "catalog" / "walker" / "global" / "config" / "v1.json").is_file()
    assert (
        tmp_path / "catalog" / "walker" / "global" / "config" / "v1.manifest.yml"
    ).is_file()


def test_project_has_returns_bool(tmp_path):
    proj = Project("walker", datastore=str(tmp_path / "catalog"))
    assert proj.has("nope") is False
    proj.save({"k": 1}, "nope")
    assert proj.has("nope") is True


def test_project_load_missing_raises(tmp_path):
    proj = Project("walker", datastore=str(tmp_path / "catalog"))
    with pytest.raises(ArtifactNotFound):
        proj.load("nope")


def test_project_load_returns_latest_version(tmp_path):
    proj = Project("walker", datastore=str(tmp_path / "catalog"))
    proj.save({"v": 1}, "config")
    proj.save({"v": 2}, "config")
    assert proj.load("config") == {"v": 2}


def test_project_load_specific_version(tmp_path):
    proj = Project("walker", datastore=str(tmp_path / "catalog"))
    proj.save({"v": 1}, "config")
    proj.save({"v": 2}, "config")
    proj.save({"v": 3}, "config")

    assert proj.load("config") == {"v": 3}
    assert proj.load("config", version=1) == {"v": 1}
    assert proj.load("config", version=2) == {"v": 2}


def test_project_load_missing_version_raises(tmp_path):
    proj = Project("walker", datastore=str(tmp_path / "catalog"))
    proj.save({"v": 1}, "config")
    with pytest.raises(ArtifactNotFound):
        proj.load("config", version=42)


def test_project_init_helper_returns_project(tmp_path):
    from box import init

    proj = init("walker", datastore=str(tmp_path / "catalog"))
    assert isinstance(proj, Project)
    assert proj.name == "walker"


def test_project_write_on_change_no_new_file_for_identical_data(tmp_path):
    proj = Project("walker", datastore=str(tmp_path / "catalog"))
    proj.save({"k": 1}, "cfg")
    proj.save({"k": 1}, "cfg")

    files = sorted(
        (tmp_path / "catalog" / "walker" / "global" / "cfg").iterdir()
    )
    data_files = [f for f in files if f.name.endswith(".json")]
    assert len(data_files) == 1
    assert data_files[0].name == "v1.json"
