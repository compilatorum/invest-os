from __future__ import annotations

from typing import Optional
from invest_os.models.schemas import RlhfLog


class RLHFEngine:
    def __init__(self):
        self.history: list[RlhfLog] = []

    def register(self, log: RlhfLog) -> None:
        self.history.append(log)

    def accuracy(self) -> float:
        if not self.history:
            return 0.0
        correct = sum(1 for h in self.history if h.level_up)
        return correct / len(self.history)

    def last_n(self, n: int = 5) -> list[RlhfLog]:
        return self.history[-n:]

    def improvement_suggestions(self) -> list[str]:
        return [h.prompt_melhoria for h in self.history if h.prompt_melhoria]
