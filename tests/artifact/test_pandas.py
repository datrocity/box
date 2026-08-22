import io

import pandas as pd
import pandas.testing as pdt
import pyarrow.parquet as pq

from box.artifact import get_artifact_for
from box.artifact.pandas_ import PandasDataFrameArtifact


def test_registered_on_import():
    df = pd.DataFrame({"a": [1, 2]})
    assert get_artifact_for(df) is PandasDataFrameArtifact


def test_extension_is_parquet():
    assert PandasDataFrameArtifact.extension == "parquet"


def test_roundtrip_preserves_dataframe():
    art = PandasDataFrameArtifact()
    df = pd.DataFrame(
        {"a": [1, 2, 3], "b": ["x", "y", "z"]},
        index=pd.Index([10, 11, 12], name="ix"),
    )
    blob = art.write_bytes(df)
    back = art.read_bytes(blob)
    pdt.assert_frame_equal(back, df)


def test_metadata_is_embedded_in_parquet_schema():
    art = PandasDataFrameArtifact()
    df = pd.DataFrame({"a": [1, 2]})
    card = {
        "project": "walker",
        "experiment": "baseline",
        "artifact": "result",
        "version": "v1",
        "params": '{"lr": 0.01}',
    }
    blob = art.write_bytes(df, metadata=card)
    table = pq.read_table(io.BytesIO(blob))
    md = table.schema.metadata or {}
    decoded = {k.decode(): v.decode() for k, v in md.items()}
    for k, v in card.items():
        assert decoded[k] == v


def test_metadata_none_still_roundtrips():
    art = PandasDataFrameArtifact()
    df = pd.DataFrame({"a": [1, 2]})
    blob = art.write_bytes(df, metadata=None)
    pdt.assert_frame_equal(art.read_bytes(blob), df)
