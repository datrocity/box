import pandas as pd

from box import init


def _seed(tmp_path):
    proj = init("walker", datastore=str(tmp_path))
    for lr in (0.01, 0.02, 0.05):
        exp = proj.experiment(f"sweep_lr_{lr}", lr=lr, prior="uniform")
        exp.save(pd.DataFrame({"x": [lr, lr]}), "result")
    exp = proj.experiment("with_prior", lr=0.01, prior="gauss")
    exp.save(pd.DataFrame({"x": [999]}), "result")
    return proj


def test_runs_returns_all_experiments(tmp_path):
    proj = _seed(tmp_path)
    runs = proj.runs()
    assert len(list(runs)) == 4


def test_where_filters_by_param(tmp_path):
    proj = _seed(tmp_path)
    runs = proj.runs()
    hits = list(runs.where(lr=0.01))
    assert len(hits) == 2  # sweep_lr_0.01 and with_prior


def test_where_multi_criteria(tmp_path):
    proj = _seed(tmp_path)
    hits = list(proj.runs().where(lr=0.01, prior="gauss"))
    assert len(hits) == 1
    assert hits[0].name == "with_prior"


def test_iter_yields_runs_with_name_params_load(tmp_path):
    proj = _seed(tmp_path)
    for run in proj.runs().where(prior="uniform"):
        assert isinstance(run.name, str)
        assert "lr" in run.params
        df = run.load("result")
        assert isinstance(df, pd.DataFrame)


def test_frame_returns_dataframe_with_params(tmp_path):
    proj = _seed(tmp_path)
    df = proj.runs().frame()
    assert "lr" in df.columns
    assert "prior" in df.columns
    assert "name" in df.columns
    assert len(df) == 4


def test_where_missing_param_excludes(tmp_path):
    proj = _seed(tmp_path)
    exp = proj.experiment("no_prior", lr=0.99)
    exp.save({"k": 1}, "cfg")
    hits = list(proj.runs().where(prior="uniform"))
    names = [r.name for r in hits]
    assert "no_prior" not in names


def test_run_load_specific_version(tmp_path):
    proj = init("walker", datastore=str(tmp_path))
    exp = proj.experiment("baseline", lr=0.01)
    exp.save({"v": 1}, "cfg")
    exp.save({"v": 2}, "cfg")

    run = next(iter(proj.runs()))
    assert run.load("cfg") == {"v": 2}
    assert run.load("cfg", version=1) == {"v": 1}
