"""Exception hierarchy for box.

All box-raised exceptions inherit from ``BoxError`` so callers can catch
everything from the library with a single ``except``.
"""


class BoxError(Exception):
    """Base class for all box errors."""


class ExperimentAlreadyExists(BoxError):
    """Raised when an experiment folder exists with different params."""


class ArtifactNotFound(BoxError):
    """Raised when a requested artifact does not exist in the datastore."""


class UnsupportedArtifactType(BoxError):
    """Raised when no registered artifact class can handle the given data type."""
