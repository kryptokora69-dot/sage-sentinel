"""Scout: reads public NEAR market data (read-only). Fixtures in replay."""
import csv
from pathlib import Path

OKX_CANDLES = "https://www.okx.com/api/v5/market/candles?instId=NEAR-USDT&bar=1H&limit=200"

def ideas_from_fixture(path: Path) -> list[dict]:
    """Turn near-miss/setup rows into trade ideas."""
    out = []
    for r in csv.DictReader(path.open()):
        out.append({"symbol": r["symbol"], "side": r["side"],
                    "price": float(r["price"]) if r["price"] else None,
                    "conditions": r["conditions_passed/total"], "ts": r["ts_ET"]})
    return out

def fetch_candles():
    # TODO: GET OKX_CANDLES via guard.check_endpoint() first; parse [ts,o,h,l,c,vol,...].
    raise NotImplementedError
