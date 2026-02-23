# PortfolioOps

PortfolioOps is a lightweight **portfolio data automation** tool that ingests holdings from CSV, validates and stores them in a SQL database, and generates an analytics report with basic concentration risk flags.

This mirrors real OPS-style workflows: **client/onboarding data ingestion, validation, storage, and operational reporting**.

## Features
- CSV ingestion + validation (ticker normalization, numeric coercion, business rule checks)
- SQLite storage of holdings (market value computed)
- Portfolio analytics (total value, allocation by asset class, largest holding)
- Risk flagging:
  - Single holding > 40% of portfolio
  - Asset class concentration > 60%

## Tech Stack
- Python
- Pandas
- SQLite (`sqlite3`)

## Run

Install dependencies:
```bash
pip install -r requirements.txt