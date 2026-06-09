from __future__ import annotations

from typing import Optional

from invest_os.models.schemas import CapitalGridResult


def rhi_from_grid(grid: CapitalGridResult) -> float:
    return grid.rhi_estimated


def purpose_score(grid: CapitalGridResult, purpose_weights: Optional[dict] = None) -> float:
    if not grid.scores:
        return 0.5
    if purpose_weights is None:
        purpose_weights = {
            "vivo": 0.25, "social": 0.20, "cultural": 0.15,
            "espiritual": 0.15, "intelectual": 0.10,
            "financeiro": 0.05, "material": 0.05, "experiencial": 0.05,
        }
    score = 0.0
    for s in grid.scores:
        w = purpose_weights.get(s.type.value, 0.125)
        score += s.score * w
    return round(min(score, 1.0), 4)


def compute_axiological(grid: Optional[CapitalGridResult] = None) -> dict:
    if grid is None:
        return {"rhi": 0.0, "purpose": 0.0}
    return {
        "rhi": rhi_from_grid(grid),
        "purpose": purpose_score(grid),
    }
