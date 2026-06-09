from __future__ import annotations

import math
import random
from typing import Optional

from invest_os.scores.descriptive import (
    nvt_ratio, mvrv_ratio, sopr, sharpe_ratio,
    il_break_even, fee_apy, financial_temperature,
    compute_descriptive,
)
from invest_os.scores.interpretive import (
    herfindahl_hirschman_index, shannon_entropy, gini_coefficient,
    compute_interpretive,
)
from invest_os.scores.axiological import rhi_from_grid, purpose_score


def pbo_probability(strategy_returns: list[float], num_trials: int = 1000) -> float:
    """Probability of Backtest Overfitting (simplified Monte Carlo approach)."""
    if len(strategy_returns) < 10:
        return 0.5
    mean_ret = sum(strategy_returns) / len(strategy_returns)
    std_ret = math.sqrt(sum((r - mean_ret) ** 2 for r in strategy_returns) / (len(strategy_returns) - 1))
    if std_ret <= 0:
        return 0.5
    sharpe_actual = mean_ret / std_ret * math.sqrt(252)
    beats = 0
    for _ in range(num_trials):
        shuffled = strategy_returns[:]
        random.shuffle(shuffled)
        m = sum(shuffled) / len(shuffled)
        s = math.sqrt(sum((r - m) ** 2 for r in shuffled) / (len(shuffled) - 1))
        if s > 0 and (m / s * math.sqrt(252)) >= sharpe_actual:
            beats += 1
    return beats / num_trials


def min_track_record_length(sharpe: float, skew: float = 0.0, kurt: float = 3.0) -> float:
    if sharpe <= 0:
        return float("inf")
    z = 1.96
    return math.ceil((z / sharpe) ** 2 * (1 - skew * sharpe + (kurt - 1) / 4 * sharpe ** 2))


def calculate_all_metrics(
    market_cap: float = 0,
    transaction_volume: float = 1,
    realized_cap: float = 1,
    returns_90d: Optional[list[float]] = None,
    p1: float = 1.0,
    p2: float = 1.0,
    volume_24h: float = 0,
    fee_tier: float = 0.003,
    liquidity: float = 1,
    portfolio_weights: Optional[list[float]] = None,
    volatility_24h: float = 0,
    exposure_pct: float = 0,
    risk_free: float = 0.0,
) -> dict:
    descriptive = compute_descriptive(
        market_cap=market_cap, transaction_volume=transaction_volume,
        realized_cap=realized_cap, returns_90d=returns_90d,
        p1=p1, p2=p2, volume_24h=volume_24h, fee_tier=fee_tier,
        liquidity=liquidity, volatility_24h=volatility_24h,
        exposure_pct=exposure_pct, risk_free=risk_free,
    )
    interpretive = compute_interpretive(portfolio_weights=portfolio_weights)
    descriptive.update(interpretive)

    alertas = []
    nvt = descriptive.get("nvt")
    if nvt and nvt > 150:
        alertas.append("NVT elevado — possível supervalorização")
    mvrv = descriptive.get("mvrv")
    if mvrv and mvrv < 1.0:
        alertas.append("MVRV < 1.0 — oportunidade de acumulação")
    elif mvrv and mvrv > 3.5:
        alertas.append("MVRV > 3.5 — perigo de sobrevalorização")
    sopr_ = descriptive.get("sopr")
    if sopr_ and sopr_ < 1.0:
        alertas.append("SOPR < 1.0 — capitulação de holders")
    hhi = descriptive.get("hhi")
    if hhi and hhi > 0.25:
        alertas.append("HHI > 0.25 — concentração excessiva no portfolio")
    descriptive["alertas"] = alertas
    return descriptive


__all__ = [
    "nvt_ratio", "mvrv_ratio", "sopr", "sharpe_ratio",
    "il_break_even", "fee_apy", "financial_temperature",
    "herfindahl_hirschman_index", "shannon_entropy", "gini_coefficient",
    "rhi_from_grid", "purpose_score",
    "calculate_all_metrics",
    "pbo_probability", "min_track_record_length",
]
