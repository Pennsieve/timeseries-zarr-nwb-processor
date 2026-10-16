"""Entry point: the NWB file in INPUT_DIR becomes a bundle in OUTPUT_DIR."""

import logging
import os
from collections.abc import Mapping

from timeseries_zarr_nwb.main import main as convert

from timeseries_zarr_nwb_processor.config import load_config
from timeseries_zarr_nwb_processor.properties import write_properties

logger = logging.getLogger(__name__)


def main(env: Mapping[str, str]) -> int:
    """Run one conversion under the Pennsieve contract and return an exit code.

    Resolves the input file and the output paths from env, runs the converter
    on them, and writes the output properties beside the bundle.
    The converter reads its own ZARR_WRITER_ settings from the process
    environment. Returns 0 on success, 2 on a bad environment, the converter's
    code when it fails, and 1 when the properties file cannot be written. No
    properties file is written unless the converter succeeds.
    """
    try:
        cfg = load_config(env)
    except ValueError:
        logger.exception("invalid invocation")
        return 2

    code = convert([str(cfg.nwb_path), str(cfg.bundle_dir)])
    if code != 0:
        return code

    try:
        write_properties(cfg.properties_path, cfg.bundle_dir)
    except OSError:
        logger.exception("failed to write %s", cfg.properties_path)
        return 1
    return 0


def run() -> None:
    """Configure INFO logging, run main on os.environ, and exit with its code."""
    logging.basicConfig(level=logging.INFO)
    raise SystemExit(main(os.environ))
