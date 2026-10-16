# timeseries-zarr-nwb-processor

Pennsieve analytics processor that converts one NWB recording into a TS-Zarr bundle.
It packages the [timeseries-zarr-nwb](https://github.com/Pennsieve/timeseries-zarr-nwb)
converter with the input and output contract of a Pennsieve workflow and the `app.yml`
manifest that registers it.

## Contract

The processor reads the single `*.nwb` file in `INPUT_DIR` and writes the bundle to
`OUTPUT_DIR/<stem>.zarr`, so `session.nwb` produces `session.zarr`. It then writes
`asset-properties.json` beside the bundle, or the file `ASSET_PROPERTIES_FILE` names,
holding the bundle directory name under the key `root_path`. The parameters in
`app.yml` reach the converter as `ZARR_WRITER_*` environment variables; the converter's
README documents them.

The exit code is 0 on success and 2 when `INPUT_DIR` or `OUTPUT_DIR` is unset or empty.
It is also 2 when `INPUT_DIR` cannot be read or does not hold exactly one `.nwb` file.
The converter returns 2 for a `ZARR_WRITER_*` value it rejects and 1 for a failed
conversion, and the processor exits with that code. The processor exits with 1 when it
cannot write the properties file, and it writes none unless the converter succeeds.

## Running locally

Put one `.nwb` file in `data/input`, then:

```bash
make run        # docker-compose build + up, against data/input and data/output
```

`dev.env` points `INPUT_DIR` and `OUTPUT_DIR` at the container mounts.

## Build

`requirements.in` pins the converter to a commit on GitHub and the `timeseries-zarr`
library to a release on PyPI. `requirements.txt` is the lock file generated from it and
pins every runtime dependency. The Dockerfile pins the base image by digest, installs
`requirements.txt`, then copies this package's source into the image.

```bash
docker build -t timeseries-zarr-nwb-processor .
```

## Development

Python 3.12, fully typed under `mypy --strict`, with a strict `ruff` ruleset. `make venv`
installs the same locked dependencies as the Dockerfile, plus the development tools
locked in `requirements-dev.txt`. The package itself is not installed. The tests and
the `make` targets import it from the source tree.

To change a dependency, edit `requirements.in` or `requirements-dev.in`, run
`make lock`, then `make install`. Commit the edited `.in` file and both lock files.

The pre-commit hooks run the ruff in `venv/`, the same version `make check` runs. Run
`make venv` before `make pre-commit`.

```bash
make venv        # create the virtualenv from the lock files
make install     # sync an existing virtualenv to the lock files
make lock        # regenerate both lock files from the .in files
make pre-commit  # install the git hooks
make test        # pytest
make typecheck   # mypy --strict
make lint        # ruff check --fix + ruff format (rewrites files)
make check       # the gate: ruff check + format check + mypy + pytest
```

`make check` must stay green.

## License

Apache-2.0. See [LICENSE](LICENSE).
