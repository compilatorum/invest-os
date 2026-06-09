from __future__ import annotations

from enum import Enum
from typing import Optional


class IntentType(str, Enum):
    INVESTMENT = "investment"
    GOVERNANCE = "governance"
    RESEARCH = "research"
    GRANT = "grant"
    MENTOR = "mentor"


class PromptRouter:
    def __init__(self):
        self._routes: dict[IntentType, str] = {
            IntentType.INVESTMENT: "level0_context",
            IntentType.GOVERNANCE: "level1_financial_dd",
            IntentType.RESEARCH: "level2_regenerative_dd",
            IntentType.GRANT: "level3_semiotic",
            IntentType.MENTOR: "level4_axiological",
        }

    def route(self, intent: IntentType) -> str:
        return self._routes.get(intent, "level0_context")

    def add_route(self, intent: IntentType, entrypoint: str) -> None:
        self._routes[intent] = entrypoint

    def list_routes(self) -> dict[str, str]:
        return {k.value: v for k, v in self._routes.items()}
