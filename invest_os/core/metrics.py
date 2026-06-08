from __future__ import annotations

import math
from typing import Optional


def nvt_ratio(market_cap: float, transaction_volume: float) -> float:
    if transaction_volume <= 0:
        return float("inf")
    return market_cap / transaction_volume


def mvrv_ratio(market_cap: float, realized_cap: float) -> Optional[float]:
    if realized_cap <= 0:
        return None
    return market_cap / realized_cap


def sopr(value_sold: float, value_bought: float) -> Optional[float]:
    if value_bought <= 0:
        return None
    return value_sold / value_bought


def sharpe_ratio(returns: list[float], risk_free: float = 0.0) -> Optional[float]:
    if len(returns) < 2:
        return None
    mean_ret = sum(returns) / len(returns)
    variance = sum((r - mean_ret) ** 2 for r in returns) / (len(returns) - 1)
    if variance <= 0:
        return None
    std = math.sqrt(variance)
    return (mean_ret - risk_free) / std


def il_break_even(p1: float, p2: float) -> float:
    if p1 <= 0 or p2 <= 0:
        return 0.0
    ratio = p2 / p1
    return 2 * math.sqrt(ratio) / (1 + ratio) - 1


def fee_apy(volume_24h: float, fee_tier: float, liquidity: float) -> Optional[float]:
    if liquidity <= 0:
        return None
    return (volume_24h * fee_tier * 365) / liquidity


def herfindahl_hirschman_index(weights: list[float]) -> float:
    total = sum(weights)
    if total <= 0:
        return 0.0
    normalized = [w / total for w in weights]
    return sum(w ** 2 for w in normalized)


def financial_temperature(volatility_24h: float, exposure_pct: float) -> float:
    return volatility_24h * exposure_pct


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
        import random
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
    metrics = {}
    metrics["nvt"] = nvt_ratio(market_cap, transaction_volume)
    metrics["mvrv"] = mvrv_ratio(market_cap, realized_cap)
    metrics["sopr"] = sopr(1.0, 1.0)
    if returns_90d:
        metrics["sharpe_90d"] = sharpe_ratio(returns_90d, risk_free)
    metrics["il_break_even"] = il_break_even(p1, p2)
    metrics["fee_apy"] = fee_apy(volume_24h, fee_tier, liquidity)
    if portfolio_weights:
        metrics["hhi"] = herfindahl_hirschman_index(portfolio_weights)
        metrics["entropy"] = shannon_entropy(portfolio_weights)
    metrics["temperature"] = financial_temperature(volatility_24h, exposure_pct)

    alertas = []
    if metrics.get("nvt") and metrics["nvt"] > 150:
        alertas.append("NVT elevado — possível supervalorização")
    if metrics.get("mvrv") and metrics["mvrv"] < 1.0:
        alertas.append("MVRV < 1.0 — oportunidade de acumulação")
    elif metrics.get("mvrv") and metrics["mvrv"] > 3.5:
        alertas.append("MVRV > 3.5 — perigo de sobrevalorização")
    if metrics.get("sopr") and metrics["sopr"] < 1.0:
        alertas.append("SOPR < 1.0 — capitulação de holders")
    if metrics.get("hhi") and metrics["hhi"] > 0.25:
        alertas.append("HHI > 0.25 — concentração excessiva no portfolio")

    metrics["alertas"] = alertas
    return metrics
