.PHONY: help install lint format ingest process pipeline explore app clean

# Default target
help:
	@echo "Available commands:"
	@echo "  make install   - Install Python dependencies in editable mode"
	@echo "  make lint      - Run ruff linter checks"
	@echo "  make format    - Automatically format code with ruff"
	@echo "  make pipeline  - Run complete end-to-end ETL pipeline (main.py)"
	@echo "  make explore   - Run DuckDB analytical query checks"
	@echo "  make app       - Spin up the local Streamlit application"
	@echo "  make clean     - Remove cached files, pycache, and log artifacts"

install:
	pip install --upgrade pip
	pip install ruff streamlit duckdb osmnx

lint:
	ruff check .

format:
	ruff format .
	ruff check --fix .

ingest:
	python scripts/ingest.py

process:
	python scripts/process.py

pipeline:
	python main.py

explore:
	python queries/explore.py

app:
	streamlit run app.py

clean:
	rm -rf __pycache__ */__pycache__ .pytest_cache .ruff_cache
	rm -rf logs/*.log
	@echo "✓ Cleaned cache and log artifacts."