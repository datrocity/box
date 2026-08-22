"""box: experiment-first research catalog."""

from box.experiment import Experiment
from box.project import Project, init


def experiment(project_name, exp_name, datastore=None, **params):
    """Short form: create a project and open/create an experiment in one call.

    Parameters
    ----------
    project_name : str
    exp_name : str
    datastore : str
        Filesystem path to the datastore root.
    **params
        Experiment params as keyword args.

    Returns
    -------
    Experiment
    """
    if datastore is None:
        raise TypeError("datastore is required")
    proj = init(project_name, datastore=datastore)
    return proj.experiment(exp_name, **params)


__all__ = ["Experiment", "Project", "experiment", "init"]
