"""Accountant: aggregates route and credit cost of every LLM call."""
from collections import defaultdict

def cost_by_route(calls: list[dict]) -> dict:
    agg = defaultdict(lambda: {"calls": 0, "est_cost_usd": 0.0})
    for c in calls:
        a = agg[c["route"]]; a["calls"] += 1
        if c["est_cost_usd"] is None:
            a["unmeasured"] = a.get("unmeasured", 0) + 1
        else:
            a["est_cost_usd"] = round(a["est_cost_usd"] + c["est_cost_usd"], 6)
    return dict(agg)
