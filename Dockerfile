FROM python:3.12.15-trixie@sha256:42dc0ee40d7707e2f2ee506a1cbe52e09ab11c207c5b429342638f83177601fe

WORKDIR /app

COPY requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r /app/requirements.txt

COPY timeseries_zarr_nwb_processor/ /app/timeseries_zarr_nwb_processor

ENV PYTHONPATH=/app

CMD ["python3.12", "-m", "timeseries_zarr_nwb_processor"]
