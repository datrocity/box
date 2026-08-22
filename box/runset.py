"""RunSet: filterable, iterable view over a project's experiments."""

import pandas as pd
import yaml

from box.errors import ArtifactNotFound


class Run:
    """A read-only handle to a persisted experiment.

    Parameters
    ----------
    project : Project
    folder : str
        Folder path relative to the datastore root
        (e.g. ``walker/2026-08-15__baseline__a3f18d02``).
    name : str
    params : dict
    """

    def __init__(self, project, folder, name, params):
        self._project = project
        self._folder = folder
        self.name = name
        self.params = dict(params)

    def load(self, artifact_name, version=None):
        """Load an artifact from this run.

        Parameters
        ----------
        artifact_name : str
        version : int, optional
            Version to load. Defaults to the latest.

        Raises
        ------
        ArtifactNotFound
        """
        ds = self._project._datastore
        try:
            children = ds.list_dir(f"{self._folder}/{artifact_name}")
        except KeyError:
            raise ArtifactNotFound(
                f"no artifact '{artifact_name}' in {self._folder}"
            ) from None
        data_files = [
            c for c in children
            if not c.endswith(".manifest.yml") and c.startswith("v")
        ]
        if not data_files:
            raise ArtifactNotFound(
                f"no artifact '{artifact_name}' in {self._folder}"
            )
        target = version if version is not None else max(
            int(c.split(".")[0][1:]) for c in data_files
        )
        try:
            data_file = next(
                c for c in data_files if c.startswith(f"v{target}.")
            )
        except StopIteration:
            raise ArtifactNotFound(
                f"artifact '{artifact_name}' has no version v{target} "
                f"in {self._folder}"
            ) from None
        ext = data_file.split(".", 1)[1]
        blob = ds.read(f"{self._folder}/{artifact_name}/{data_file}")
        from box.project import _artifact_class_for_extension

        return _artifact_class_for_extension(ext)().read_bytes(blob)


class RunSet:
    """A collection of Run objects with pandas-style filtering.

    Parameters
    ----------
    runs : iterable of Run
    """

    def __init__(self, runs):
        self._runs = list(runs)

    def __iter__(self):
        """Yield each ``Run`` in insertion order."""
        return iter(self._runs)

    def __len__(self):
        """Return the number of runs in the set."""
        return len(self._runs)

    def where(self, **criteria):
        """Filter runs by exact param match.

        Runs missing any of the criteria params are excluded.

        Parameters
        ----------
        **criteria
            Param name -> required value.

        Returns
        -------
        RunSet
        """
        def match(run):
            for k, v in criteria.items():
                if k not in run.params:
                    return False
                if run.params[k] != v:
                    return False
            return True

        return RunSet([r for r in self._runs if match(r)])

    def frame(self):
        """Return a DataFrame with one row per run: params + built-in cols.

        Built-in columns: ``name``, ``folder``. Missing params in some runs
        become NaN.

        Returns
        -------
        pandas.DataFrame
        """
        rows = []
        for r in self._runs:
            rows.append({"name": r.name, "folder": r._folder, **r.params})
        return pd.DataFrame(rows)


def _load_run(project, folder):
    """Read a run's params.yaml + manifest.yml and return a Run."""
    ds = project._datastore
    params_text = ds.read(f"{folder}/params.yaml").decode("utf-8")
    params = yaml.safe_load(params_text) or {}
    manifest_text = ds.read(f"{folder}/manifest.yml").decode("utf-8")
    manifest = yaml.safe_load(manifest_text) or {}
    name = manifest.get("experiment", folder.split("__", 2)[1])
    return Run(project, folder, name, params)


def load_runs(project):
    """Return a RunSet of every experiment in the project."""
    ds = project._datastore
    try:
        entries = ds.list_dir(project.name)
    except KeyError:
        return RunSet([])
    runs = []
    for entry in entries:
        if entry == "global":
            continue
        folder = f"{project.name}/{entry}"
        if ds.exists(f"{folder}/params.yaml"):
            runs.append(_load_run(project, folder))
    return RunSet(runs)
