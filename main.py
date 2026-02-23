import argparse
from pathlib import Path

from database import get_connection, init_db, clear_holdings, insert_holdings
from pipeline import load_csv, clean_and_validate, to_db_rows
from analytics import portfolio_summary, risk_flags


def format_money(x: float) -> str:
    return f"${x:,.2f}"


def main() -> None:
    parser = argparse.ArgumentParser(description="PortfolioOps: CSV → SQLite → analytics report")
    parser.add_argument(
        "--file",
        type=str,
        default="data/sample_portfolio.csv",
        help="Path to portfolio holdings CSV",
    )
    parser.add_argument(
        "--reset-db",
        action="store_true",
        help="Clear holdings table before inserting new rows",
    )
    args = parser.parse_args()

    csv_path = Path(args.file)

    df = load_csv(csv_path)
    df = clean_and_validate(df)
    rows = to_db_rows(df)

    conn = get_connection()
    init_db(conn)

    if args.reset_db:
        clear_holdings(conn)

    insert_holdings(conn, rows)

    summary = portfolio_summary(conn)
    flags = risk_flags(conn)

    total = summary["total"]
    print("\n=== PortfolioOps Report ===")
    print(f"Input File: {csv_path}")
    print(f"Total Portfolio Value: {format_money(total)}\n")

    print("Asset Allocation:")
    for asset_class, value in summary["by_class"]:
        pct = (value / total * 100) if total else 0
        print(f"  - {asset_class}: {format_money(value)} ({pct:.1f}%)")

    ticker, mv = summary["largest"]
    if ticker:
        pct = (mv / total * 100) if total else 0
        print(f"\nLargest Holding: {ticker} ({format_money(mv)} / {pct:.1f}%)")

    if flags:
        print("\nRisk Flags:")
        for f in flags:
            print(f"  ⚠ {f}")
    else:
        print("\nRisk Flags: None ✅")

    conn.close()
    print("\nDone.\n")


if __name__ == "__main__":
    main()