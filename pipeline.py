from pathlib import Path
import pandas as pd

REQUIRED_COLUMNS = {"ticker", "shares", "price", "asset_class"}


def load_csv(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")
    return df


def clean_and_validate(df: pd.DataFrame) -> pd.DataFrame:
    # Drop completely empty rows
    df = df.dropna(how="all").copy()

    # Strip whitespace and normalize types
    df["ticker"] = df["ticker"].astype(str).str.strip().str.upper()
    df["asset_class"] = df["asset_class"].astype(str).str.strip()

    # Coerce numeric columns
    df["shares"] = pd.to_numeric(df["shares"], errors="coerce")
    df["price"] = pd.to_numeric(df["price"], errors="coerce")

    # Drop rows with critical nulls
    df = df.dropna(subset=["ticker", "shares", "price", "asset_class"])

    # Validate business rules
    df = df[(df["shares"] > 0) & (df["price"] > 0)]

    # Compute market value
    df["market_value"] = df["shares"] * df["price"]

    return df.reset_index(drop=True)


def to_db_rows(df: pd.DataFrame) -> list[dict]:
    return df[["ticker", "shares", "price", "asset_class", "market_value"]].to_dict(
        orient="records"
    )