FROM python:3.12

WORKDIR /app

RUN apt-get update && apt-get -y install libhdf5-dev && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r /app/requirements.txt

COPY pyproject.toml /app/pyproject.toml
COPY timeseries_zarr_nwb_processor/ /app/timeseries_zarr_nwb_processor

RUN pip install --no-cache-dir /app

CMD ["python3.12", "-m", "timeseries_zarr_nwb_processor"]
