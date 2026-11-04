"""LLM router: NEAR AI Cloud first, Orbio NEAR AI API as fallback. Mock mode (default) = no network."""
import hashlib, json, logging, os
from pathlib import Path
import yaml_lite as yaml

log = logging.getLogger("router")
COSTS = yaml.safe_load((Path(__file__).parent / "config/costs.yaml").read_text())["routes"]

class RouteError(Exception):
    pass

class LLMRouter:
    def __init__(self, mock: bool | None = None, min_credit_usd: float = 0.01):
        self.mock = (os.getenv("SAGE_MOCK", "1") != "0") if mock is None else mock
        self.min_credit_usd = min_credit_usd
        self.sage_model = os.getenv("SAGE_MODEL", "levanto/sage-1.4")
        self.fallback_model = os.getenv("FALLBACK_MODEL", "")
        self.calls: list[dict] = []

    def _record(self, route, model, cost):
        rec = {"route": route, "model": model, "est_cost_usd": cost}
        self.calls.append(rec)
        log.info("route=%s model=%s est_cost=%s", route, model, cost)
        return rec

    def score(self, idea: dict) -> dict:
        if self.mock:
            h = int(hashlib.sha256(json.dumps(idea, sort_keys=True).encode()).hexdigest(), 16)
            p = round(0.4 + (h % 50) / 100, 2)  # deterministic canned score 0.40-0.89
            self._record("mock", self.sage_model, COSTS["mock"]["sage"])
            return {"sage_p": p, "route": "mock"}
        try:
            if self._nearai_credit() < self.min_credit_usd:
                raise RouteError("low credit")
            out = self._call(os.environ["NEARAI_BASE_URL"], os.environ["NEARAI_API_KEY"], self.sage_model, idea)
            self._record("nearai", self.sage_model, COSTS["nearai"]["sage"])
            return {**out, "route": "nearai"}
        except Exception as e:  # noqa: BLE001
            log.warning("nearai failed (%s); falling back to orbio", type(e).__name__)
        out = self._call(os.environ["ORBIO_BASE_URL"], os.environ["ORBIO_API_KEY"], self.fallback_model, idea)
        self._record("orbio", self.fallback_model, COSTS["orbio"]["jev"])
        return {**out, "route": "orbio"}

    def _nearai_credit(self) -> float:
        # TODO: query NEAR AI Cloud credit balance (read-only). Fail closed: 0.0 forces fallback.
        return 0.0

    def _call(self, base_url, api_key, model, idea) -> dict:
        # TODO: OpenAI-compatible POST with timeout; parse sage_p. Never log api_key.
        raise RouteError("live calls not implemented in skeleton")
