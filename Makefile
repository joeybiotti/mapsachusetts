.PHONY: help install lint format lint-sql format-sql ingest process pipeline explore app clean test

# Default target
help:
	@echo "Available commands:"
	@echo "  make install    - Install Python and SQL styling dependencies"
	@echo "  make lint       - Run ruff (Python) and sqlfluff (SQL) linter checks"
	@echo "  make format     - Automatically format Python (ruff) and SQL (sqlfluff) code"
	@echo "  make lint-sql   - Run sqlfluff checks on SQL files"
	@echo "  make format-sql - Auto-fix SQL formatting with sqlfluff"
	@echo "  make pipeline   - Run complete end-to-end ETL pipeline (main.py)"
	@echo "  make explore    - Run DuckDB analytical query checks"
	@echo "  make app        - Spin up the local Streamlit application"
	@echo "  make clean      - Remove cached files, pycache, and log artifacts"

install:
	pip install --upgrade pip
	pip install ruff streamlit duckdb osmnx sqlfluff

lint:
	ruff check .
	sqlfluff lint sql/

format:
	ruff format .
	ruff check --fix .
	sqlfluff fix --force sql/

lint-sql:
	sqlfluff lint sql/

format-sql:
	sqlfluff fix --force sql/

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

test: 
	pytest -v