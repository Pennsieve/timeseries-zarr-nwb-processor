from pathlib import Path

import pytest

from timeseries_zarr_nwb_processor.config import Config, load_config


def _input_dir(tmp_path, *names):
    input_dir = tmp_path / "in"
    input_dir.mkdir()
    for name in names:
        (input_dir / name).write_bytes(b"")
    return input_dir


def test_unset_input_or_output_dir_raises():
    with pytest.raises(ValueError):
        load_config({})
    with pytest.raises(ValueError):
        load_config({"INPUT_DIR": "/data/input"})
    with pytest.raises(ValueError):
        load_config({"OUTPUT_DIR": "/data/output"})


@pytest.mark.parametrize(
    "env",
    [
        {"INPUT_DIR": "", "OUTPUT_DIR": "/data/output"},
        {"INPUT_DIR": "/data/input", "OUTPUT_DIR": ""},
    ],
)
def test_empty_input_or_output_dir_raises(env):
    with pytest.raises(ValueError):
        load_config(env)


def test_input_dir_scan_finds_sole_nwb(tmp_path):
    input_dir = _input_dir(tmp_path, "session.nwb", "notes.txt")
    out = tmp_path / "out"
    cfg = load_config({"INPUT_DIR": str(input_dir), "OUTPUT_DIR": str(out)})
    assert isinstance(cfg, Config)
    assert cfg.nwb_path == input_dir / "session.nwb"
    assert cfg.bundle_dir == out / "session.zarr"


def test_input_dir_with_no_nwb_raises(tmp_path):
    input_dir = _input_dir(tmp_path)
    with pytest.raises(ValueError):
        load_config(
            {"INPUT_DIR": str(input_dir), "OUTPUT_DIR": str(tmp_path / "out")}
        )


def test_input_dir_with_multiple_nwb_raises(tmp_path):
    input_dir = _input_dir(tmp_path, "a.nwb", "b.nwb")
    with pytest.raises(ValueError):
        load_config(
            {"INPUT_DIR": str(input_dir), "OUTPUT_DIR": str(tmp_path / "out")}
        )


def test_missing_input_dir_raises(tmp_path):
    with pytest.raises(ValueError):
        load_config(
            {
                "INPUT_DIR": str(tmp_path / "missing"),
                "OUTPUT_DIR": str(tmp_path / "out"),
            }
        )


def test_unset_properties_file_uses_the_default_name(tmp_path):
    input_dir = _input_dir(tmp_path, "session.nwb")
    cfg = load_config(
        {"INPUT_DIR": str(input_dir), "OUTPUT_DIR": str(tmp_path / "out")}
    )
    assert cfg.properties_path == tmp_path / "out" / "asset-properties.json"


def test_env_properties_file_honored(tmp_path):
    input_dir = _input_dir(tmp_path, "session.nwb")
    cfg = load_config(
        {
            "INPUT_DIR": str(input_dir),
            "OUTPUT_DIR": str(tmp_path / "out"),
            "ASSET_PROPERTIES_FILE": "declared.json",
        }
    )
    assert cfg.properties_path == tmp_path / "out" / "declared.json"


def test_properties_file_is_a_sibling_of_the_bundle(tmp_path):
    input_dir = _input_dir(tmp_path, "session.nwb")
    cfg = load_config(
        {"INPUT_DIR": str(input_dir), "OUTPUT_DIR": str(tmp_path / "out")}
    )
    assert cfg.properties_path.parent == cfg.bundle_dir.parent
    assert isinstance(cfg.properties_path, Path)
