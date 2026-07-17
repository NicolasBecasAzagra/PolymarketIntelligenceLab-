# Module Status: Ingestion

## Goal
Ingest market data and metadata from Polymarket and save it efficiently to the Bronze layer in Parquet format.
Supports hourly runs to capture intraday volatility.

## Current Architecture
- **Data Source:** Polymarket Gamma API (Public).
- **Client:** `requests` based client with error handling.
- **Storage:** Saved to `data/raw/` in `.parquet` format using `pandas`/`polars` with hourly partitioning.

## Tasks
- [x] Base API Client implementation.
- [x] Bronze layer Parquet writer.
- [x] Orchestration script (`run_ingestion.py`).

## Technical Context
- The script should be robust enough to be later orchestrated by Airflow.
- Output path format: `data/raw/markets_YYYYMMDD_HH.parquet`.
