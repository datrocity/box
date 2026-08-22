"""Path conventions, write modes, and canonicalization helpers.

Pure functions and enums only. No I/O.
"""

import enum
import hashlib
import json


class WriteMode(enum.Enum):
    """Behavior when writing an artifact that may already have a prior version.

    v1 ships a single mode; the enum is kept for future extension.
    """

    WRITE_ON_CHANGE = "write_on_change"


def canonicalize_params(params):
    """Serialize a params dict in a canonical form: sorted keys, JSON.

    Parameters
    ----------
    params : dict
        Mapping of JSON-safe values.

    Returns
    -------
    str
        Canonical JSON string with sorted keys at every level.
    """
    return json.dumps(params, sort_keys=True, separators=(", ", ": "))


def params_hash(params):
    """Compute a short stable hash of a params dict.

    Parameters
    ----------
    params : dict

    Returns
    -------
    str
        First 8 hex chars of the SHA-256 of the canonical form (~4B possible
        values -- collisions are vanishingly unlikely for research-scale use).
    """
    canonical = canonicalize_params(params).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()[:8]


def experiment_folder_name(creation_date, name, params):
    """Compose an experiment folder name from date, name, and params hash.

    Parameters
    ----------
    creation_date : datetime.date
        The date the experiment folder was first created.
    name : str
        Human-chosen experiment name.
    params : dict
        Params used to compute the disambiguating hash.

    Returns
    -------
    str
        A folder name in the form ``YYYY-MM-DD__<name>__<hash>``.
    """
    return f"{creation_date.isoformat()}__{name}__{params_hash(params)}"
