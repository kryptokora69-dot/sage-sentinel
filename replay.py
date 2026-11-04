"""Replay fixtures through the agents in mock mode (no network)."""
import csv, time
from collections import Counter
from pathlib import Path
from llm_router import LLMRouter
from agents import scout, guard as g, accountant
from agents.scorer import Scorer

FIX = Path(__file__).parent / "data/fixtures"

def main():
    router = LLMRouter(mock=True); scorer = Scorer(router); guard = g.Guard()
    guard.r["kill_switch"] = False
    now = time.time(); proposed = 0; blocked = Counter()
    for i, idea in enumerate(scout.ideas_from_fixture(FIX / "near_miss_sample.csv")):
        s = scorer.score(idea); proposed += 1
        # synthetic: one oversized and one stale action to exercise the caps
        s.update(size_usd=500 if i == 2 else 25, price_ts=now - (1000 if i == 1 else 10))
        ok, why = guard.check(s, now)
        if not ok: blocked[why] += 1
    pnl = sum(float(r["realized_pnl_usd"] or 0) for r in csv.DictReader((FIX / "paper_trades_sample.csv").open()) if r["event"] == "EXIT")
    print(f"proposed: {proposed}\nallowed: {proposed - sum(blocked.values())}\nblocked by rule: {dict(blocked)}")
    print(f"paper P&L (fixture exits): ${pnl:.2f}\ncredit cost by route: {accountant.cost_by_route(router.calls)}")

if __name__ == "__main__":
    main()
