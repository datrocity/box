import pytest

from box.errors import (
    ArtifactNotFound,
    BoxError,
    ExperimentAlreadyExists,
)


def test_all_errors_are_box_errors():
    assert issubclass(ExperimentAlreadyExists, BoxError)
    assert issubclass(ArtifactNotFound, BoxError)


def test_box_error_is_an_exception():
    assert issubclass(BoxError, Exception)


def test_error_carries_message():
    err = ArtifactNotFound("no such artifact: result")
    assert str(err) == "no such artifact: result"

    with pytest.raises(ArtifactNotFound, match="no such artifact"):
        raise err
