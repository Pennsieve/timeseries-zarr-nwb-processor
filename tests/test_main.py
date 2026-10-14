import json

import numpy as np
import pytest
from pynwb import NWBHDF5IO
from pynwb.testing.mock.ecephys import mock_ElectricalSeries
from pynwb.testing.mock.file import mock_NWBFile

from timeseries_zarr_nwb_processor.main import main, run


def _layout(tmp_path):
    """Return (env, nwb_path, bundle_dir) for one empty input file."""
    input_dir = tmp_path / "in"
    input_dir.mkdir()
    nwb = input_dir / "session.nwb"
    nwb.write_bytes(b"")
    out = tmp_path / "out"
    out.mkdir()
    env = {"INPUT_DIR": str(input_dir), "OUTPUT_DIR": str(out)}
    return env, nwb, out / "session.zarr"


def test_main_runs_the_converter_and_writes_the_properties(tmp_path, mocker):
    convert = mocker.patch(
        "timeseries_zarr_nwb_processor.main.convert", return_value=0
    )
    env, nwb, bundle = _layout(tmp_path)
    assert main(env) == 0
    convert.assert_called_once_with([str(nwb), str(bundle)])
    properties = json.loads(
        (bundle.parent / "asset-properties.json").read_text()
    )
    assert properties == {"root_path": "session.zarr"}


def test_main_returns_the_converter_code_and_writes_no_properties(
    tmp_path, mocker
):
    mocker.patch("timeseries_zarr_nwb_processor.main.convert", return_value=3)
    env, _, bundle = _layout(tmp_path)
    assert main(env) == 3
    assert not (bundle.parent / "asset-properties.json").exists()


def test_main_returns_2_on_a_bad_environment(mocker):
    convert = mocker.patch("timeseries_zarr_nwb_processor.main.convert")
    assert main({}) == 2
    convert.assert_not_called()


def test_main_returns_2_when_the_input_dir_is_missing(tmp_path, mocker):
    convert = mocker.patch("timeseries_zarr_nwb_processor.main.convert")
    env = {"INPUT_DIR": str(tmp_path / "missing"), "OUTPUT_DIR": str(tmp_path)}
    assert main(env) == 2
    convert.assert_not_called()


def test_main_returns_1_when_the_properties_cannot_be_written(tmp_path, mocker):
    mocker.patch("timeseries_zarr_nwb_processor.main.convert", return_value=0)
    env, _, _ = _layout(tmp_path)
    env["ASSET_PROPERTIES_FILE"] = "missing-dir/asset-properties.json"
    assert main(env) == 1


def test_main_converts_a_real_file(tmp_path):
    env, nwb, bundle = _layout(tmp_path)
    nwbfile = mock_NWBFile()
    mock_ElectricalSeries(
        nwbfile=nwbfile, data=np.zeros((4096, 2)), rate=1000.0
    )
    with NWBHDF5IO(str(nwb), mode="w") as io:
        io.write(nwbfile)
    assert main(env) == 0
    assert (bundle / "zarr.json").exists()
    assert (bundle / "recording.json").exists()
    assert json.loads(
        (bundle.parent / "asset-properties.json").read_text()
    ) == {"root_path": "session.zarr"}


def test_run_exits_with_the_main_code(mocker):
    mocker.patch("timeseries_zarr_nwb_processor.main.main", return_value=3)
    with pytest.raises(SystemExit) as exit_info:
        run()
    assert exit_info.value.code == 3
