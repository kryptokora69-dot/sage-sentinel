"""Guard: enforces Warden's rules. Paper only. No signing/transfer code, ever.
Rejects (never clamps) anything over a cap. Fails closed on missing data, stale price, config error."""
import json, time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse
import yaml_lite as yaml

# Hard caps (constants; config may be stricter, never looser)
HARD_MAX_POSITION_USD = 100.0
HARD_MAX_DAILY_LOSS_USD = 25.0
HARD_MAX_AGE_SECONDS = 900
ROOT = Path(__file__).resolve().parent.parent
LOG = ROOT / "logs" / "decisions.jsonl"

class Guard:
    def __init__(self, rules_path=ROOT / "rules/guardrails.yaml"):
        try:
            r = yaml.safe_load(Path(rules_path).read_text())
            self.cfg_ok = (r["mode"] == "paper"
                           and float(r["max_position_usd"]) <= HARD_MAX_POSITION_USD
                           and float(r["max_daily_loss_usd"]) <= HARD_MAX_DAILY_LOSS_USD
                           and int(r["max_age_seconds"]) <= HARD_MAX_AGE_SECONDS)
            self.r = r
        except Exception:  # noqa: BLE001
            self.cfg_ok, self.r = False, {}
        self.daily_loss = 0.0

    def check_endpoint(self, url: str) -> bool:
        return urlparse(url).hostname in set(self.r.get("allowed_endpoints", []))

    def check(self, a: dict, now: float | None = None) -> tuple[bool, str]:
        now = time.time() if now is None else now
        if not self.cfg_ok: v = (False, "config_error")
        elif self.r.get("kill_switch", True): v = (False, "kill_switch")
        elif a.get("mode", "paper") != "paper": v = (False, "not_paper")
        elif any(a.get(k) in (None, "") for k in ("symbol", "side", "price", "size_usd", "sage_p", "price_ts")):
            v = (False, "missing_data")
        elif now - a["price_ts"] > self.r["max_age_seconds"]: v = (False, "stale_price")
        elif a["size_usd"] > self.r["max_position_usd"]: v = (False, "over_max_position")
        elif self.daily_loss >= self.r["max_daily_loss_usd"]: v = (False, "daily_loss_cap")
        elif a["sage_p"] < self.r.get("min_sage_p", 1.0): v = (False, "low_sage_score")
        else: v = (True, "ok")
        self._log(a, *v)
        return v

    def record_pnl(self, pnl: float):
        if pnl < 0: self.daily_loss += -pnl

    def _log(self, a, ok, reason):
        LOG.parent.mkdir(exist_ok=True)
        with LOG.open("a") as f:  # append-only
            f.write(json.dumps({"t": datetime.now(timezone.utc).isoformat(), "allowed": ok,
                                "reason": reason, "action": a}, default=str) + "\n")
