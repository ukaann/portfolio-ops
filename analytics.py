import sqlite3


def portfolio_summary(conn: sqlite3.Connection) -> dict:
    total = conn.execute("SELECT COALESCE(SUM(market_value), 0) AS total FROM holdings;").fetchone()["total"]

    by_class = conn.execute(
        """
        SELECT asset_class, SUM(market_value) AS value
        FROM holdings
        GROUP BY asset_class
        ORDER BY value DESC;
        """
    ).fetchall()

    largest = conn.execute(
        """
        SELECT ticker, market_value
        FROM holdings
        ORDER BY market_value DESC
        LIMIT 1;
        """
    ).fetchone()

    return {
        "total": float(total),
        "by_class": [(r["asset_class"], float(r["value"])) for r in by_class],
        "largest": (largest["ticker"], float(largest["market_value"])) if largest else (None, 0.0),
    }


def risk_flags(conn: sqlite3.Connection) -> list[str]:
    flags: list[str] = []

    total = conn.execute("SELECT COALESCE(SUM(market_value), 0) AS total FROM holdings;").fetchone()["total"]
    total = float(total)

    if total <= 0:
        return ["No holdings found (total portfolio value is 0)."]

    # Holding concentration > 40%
    holding_conc = conn.execute(
        """
        SELECT ticker, market_value / ? AS pct
        FROM holdings
        ORDER BY pct DESC
        LIMIT 1;
        """,
        (total,),
    ).fetchone()

    if holding_conc and float(holding_conc["pct"]) > 0.40:
        pct = round(float(holding_conc["pct"]) * 100, 1)
        flags.append(f"Holding concentration risk: {holding_conc['ticker']} is {pct}% of portfolio (> 40%).")

    # Asset class concentration > 60%
    class_conc = conn.execute(
        """
        SELECT asset_class, SUM(market_value) / ? AS pct
        FROM holdings
        GROUP BY asset_class
        ORDER BY pct DESC
        LIMIT 1;
        """,
        (total,),
    ).fetchone()

    if class_conc and float(class_conc["pct"]) > 0.60:
        pct = round(float(class_conc["pct"]) * 100, 1)
        flags.append(f"Asset class concentration risk: {class_conc['asset_class']} is {pct}% of portfolio (> 60%).")

    return flags