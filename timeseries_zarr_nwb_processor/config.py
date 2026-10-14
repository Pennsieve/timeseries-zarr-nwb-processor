"""The directories and files a Pennsieve workflow supplies to one run."""

import os
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

from timeseries_zarr_nwb_processor.properties import DEFAULT_PROPERTIES_FILE


@dataclass(frozen=True, slots=True)
class Config:
    """The input file, the bundle path, and the properties path of one run.

    properties_path is a sibling of final_dir.
    """

    nwb_path: Path
    final_dir: Path
    properties_path: Path


def load_config(env: Mapping[str, str]) -> Config:
    """Resolve a Config from the environment.

    The bundle is published to OUTPUT_DIR/<stem>.zarr, named for the *.nwb
    file in INPUT_DIR. ASSET_PROPERTIES_FILE names the properties file
    written beside the bundle, DEFAULT_PROPERTIES_FILE when unset. Raises
    ValueError if INPUT_DIR or OUTPUT_DIR is unset or empty, or if INPUT_DIR
    cannot be read or does not hold exactly one *.nwb file.
    """
    input_dir = env.get("INPUT_DIR")
    output_dir = env.get("OUTPUT_DIR")
    if not input_dir or not output_dir:
        raise ValueError(
            "INPUT_DIR and OUTPUT_DIR must both be set and non-empty"
        )
    # Atomic publish renames the final path, and a rename cannot target a mount
    # point such as the bare OUTPUT_DIR volume. The bundle is therefore a named
    # directory inside it, taking the input stem: session.nwb -> session.zarr.
    nwb_path = _sole_nwb(Path(input_dir))
    final_dir = Path(output_dir) / f"{nwb_path.stem}.zarr"
    properties_name = env.get("ASSET_PROPERTIES_FILE", DEFAULT_PROPERTIES_FILE)
    return Config(
        nwb_path=nwb_path,
        final_dir=final_dir,
        properties_path=final_dir.parent / properties_name,
    )


def _sole_nwb(input_dir: Path) -> Path:
    """Return the single *.nwb file in input_dir.

    Raises ValueError unless input_dir can be read and holds exactly one *.nwb
    file.
    """
    try:
        with os.scandir(input_dir) as entries:
            nwbs = sorted(
                Path(entry.path)
                for entry in entries
                if entry.name.lower().endswith(".nwb") and entry.is_file()
            )
    except OSError as error:
        raise ValueError(
            f"cannot read INPUT_DIR {input_dir}: {error}"
        ) from error
    if len(nwbs) != 1:
        raise ValueError(
            f"expected exactly one .nwb file in {input_dir}, found {len(nwbs)}"
        )
    return nwbs[0]
