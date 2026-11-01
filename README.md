# Sage Sentinel (NEAR Hackathon) — paper trading only

A team of agents; no funds move, and there is no signing or transfer code.

- **Scout** (`agents/scout.py`): reads public NEAR market data (e.g. OKX NEAR-USDT 1H candles) from an allowlist of read-only endpoints.
- **Scorer** (`agents/scorer.py`): asks Sage (`levanto/sage-1.4`) to score each idea via `llm_router.py`.
- **Guard** (`agents/guard.py`, `rules/guardrails.yaml`): paper only; hard caps on position size and daily loss, plus a kill switch. Over-cap actions are rejected and logged, never clamped. Fails closed on missing data, stale prices, or config errors. Writes an append-only `logs/decisions.jsonl` (gitignored).
- **Accountant** (`agents/accountant.py`): totals the route and estimated credit cost per call (`config/costs.yaml`).

## Two inference routes
1. **Primary: NEAR AI Cloud** (`NEARAI_BASE_URL`, `NEARAI_API_KEY`).
2. **Fallback: Orbio NEAR AI API** (`ORBIO_BASE_URL`, `ORBIO_API_KEY`, `FALLBACK_MODEL`), used on error or low credit.

Mock mode (`SAGE_MOCK=1`, the default) returns deterministic canned scores with no network.
Cost figures are early, small-sample estimates; Sage on Orbio is not measured yet.

## Run
```
pip install -r requirements.txt
python replay.py
```
Fixtures in `data/fixtures/` are synthetic.
