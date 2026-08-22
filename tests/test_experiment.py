import datetime as dt

import pandas as pd
import pandas.testing as pdt
import yaml

from box import init


def _today():
    return dt.date.today().isoformat()


def test_experiment_creates_dated_folder(tmp_path):
    proj = init("walker", datastore=str(tmp_path))
    proj.experiment("baseline", lr=0.01, prior="uniform")

    walker = tmp_path / "walker"
    subs = [p.name for p in walker.iterdir() if p.name != "global"]
    assert len(subs) == 1
    folder = subs[0]
    assert folder.startswith(_today() + "__baseline__")


def test_experiment_writes_params_yaml(tmp_path):
    proj = init("walker", datastore=str(tmp_path))
    proj.experiment("baseline", lr=0.01, prior="uniform")
    walker = tmp_path / "walker"
    exp_folder = next(p for p in walker.iterdir() if p.name != "global")
    params = yaml.safe_load((exp_folder / "params.yaml").read_text())
    assert params == {"lr": 0.01, "prior": "uniform"}


def test_experiment_params_are_attribute_accessible(tmp_path):
    proj = init("walker", datastore=str(tmp_path))
    exp = proj.experiment("baseline", lr=0.01, prior="uniform")
    assert exp.lr == 0.01
    assert exp.prior == "uniform"
    assert exp.params == {"lr": 0.01, "prior": "uniform"}


def test_experiment_save_and_load_dataframe(tmp_path):
    proj = init("walker", datastore=str(tmp_path))
    exp = proj.experiment("baseline", lr=0.01)
    df = pd.DataFrame({"a": [1, 2, 3]})
    exp.save(df, "result")
    pdt.assert_frame_equal(exp.load("result"), df)


def test_experiment_reopens_by_identity(tmp_path):
    proj = init("walker", datastore=str(tmp_path))
    exp1 = proj.experiment("baseline", lr=0.01)
    exp1.save({"k": 1}, "cfg")

    exp2 = proj.experiment("baseline", lr=0.01)  # same identity
    assert exp2.load("cfg") == {"k": 1}


def test_experiment_different_params_makes_different_folder(tmp_path):
    proj = init("walker", datastore=str(tmp_path))
    proj.experiment("baseline", lr=0.01)
    proj.experiment("baseline", lr=0.02)
    walker = tmp_path / "walker"
    exp_folders = [p.name for p in walker.iterdir() if p.name != "global"]
    assert len(exp_folders) == 2


def test_experiment_short_form_via_module(tmp_path):
    import box

    exp = box.experiment(
        "walker", "baseline", datastore=str(tmp_path), lr=0.01
    )
    exp.save({"k": 1}, "cfg")
    assert exp.load("cfg") == {"k": 1}
