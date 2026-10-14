# timeseries-zarr-nwb-processor

Pennsieve analytics processor that converts one NWB recording into a TS-Zarr bundle.
It packages the [timeseries-zarr-nwb](https://github.com/Pennsieve/timeseries-zarr-nwb)
converter with the input and output contract of a Pennsieve workflow and the `app.yml`
manifest that registers it.

## Contract

The processor reads the single `*.nwb` file in `INPUT_DIR` and publishes the bundle to
`OUTPUT_DIR/<stem>.zarr`, so `session.nwb` produces `session.zarr`. It then writes
`asset-properties.json` beside the bundle, or the file `ASSET_PROPERTIES_FILE` names,
holding the bundle directory name under the key `root_path`. The parameters in
`app.yml` reach the converter as `ZARR_WRITER_*` environment variables; the converter's
README documents them.

The exit code is 0 on success and 2 when `INPUT_DIR` or `OUTPUT_DIR` is unset or empty.
It is also 2 when `INPUT_DIR` cannot be read or does not hold exactly one `.nwb` file.
The converter returns 2 for a `ZARR_WRITER_*` value it rejects and 1 for a failed
conversion, and the processor exits with that code. The processor exits with 1 when it
cannot write the properties file, and it writes none unless the bundle was published.

## Running locally

Put one `.nwb` file in `data/input`, then:

```bash
make run        # docker-compose build + up, against data/input and data/output
```

`dev.env` points `INPUT_DIR` and `OUTPUT_DIR` at the container mounts.

## Build

The Dockerfile installs the library and the converter from the GitHub refs that
`requirements.txt` names, then installs this package.

```bash
docker build -t timeseries-zarr-nwb-processor .
```

## Development

Python 3.12, fully typed under `mypy --strict`, with a strict `ruff` ruleset. `make venv`
installs `../timeseries-zarr-py` and `../timeseries-zarr-nwb` in editable mode; set
`LIBRARY=` and `CONVERTER=` to point elsewhere.

```bash
make venv        # create the virtualenv and install the siblings and this package
make test        # pytest
make typecheck   # mypy --strict
make lint        # ruff check --fix + ruff format (rewrites files)
make check       # the gate: ruff check + format check + mypy + pytest
```

`make check` must stay green.

## License

Apache-2.0. See [LICENSE](LICENSE).
