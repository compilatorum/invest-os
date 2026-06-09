from __future__ import annotations

import math
from typing import Optional


def herfindahl_hirschman_index(weights: list[float]) -> float:
    total = sum(weights)
    if total <= 0:
        return 0.0
    normalized = [w / total for w in weights]
    return sum(w ** 2 for w in normalized)


def shannon_entropy(weights: list[float]) -> float:
    total = sum(weights)
    if total <= 0:
        return 0.0
    normalized = [w / total for w in weights]
    return -sum(p * math.log2(p) for p in normalized if p > 0)


def gini_coefficient(values: list[float]) -> float:
    if not values:
        return 0.0
    sorted_vals = sorted(values)
    n = len(sorted_vals)
    cumsum = 0
    for i, v in enumerate(sorted_vals):
        cumsum += (2 * (n - i) - 1) * v
    mean = sum(sorted_vals) / n
    if mean <= 0:
        return 0.0
    return max(0.0, (n + 1 - 2 * cumsum / (n * mean)) / n)


def compute_interpretive(portfolio_weights: Optional[list[float]] = None) -> dict:
    d = {}
    if portfolio_weights:
        d["hhi"] = herfindahl_hirschman_index(portfolio_weights)
        d["entropy"] = shannon_entropy(portfolio_weights)
    return d
