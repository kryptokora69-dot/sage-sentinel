"""Scorer: asks Sage (via LLMRouter) to score each trade idea."""
from llm_router import LLMRouter

class Scorer:
    def __init__(self, router: LLMRouter):
        self.router = router

    def score(self, idea: dict) -> dict:
        return {**idea, **self.router.score(idea)}
