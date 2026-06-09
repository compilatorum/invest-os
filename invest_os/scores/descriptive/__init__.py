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


def financial_temperature(volatility_24h: float, exposure_pct: float) -> float:
    return volatility_24h * exposure_pct


def compute_descriptive(
    market_cap: float = 0,
    transaction_volume: float = 1,
    realized_cap: float = 1,
    returns_90d: Optional[list[float]] = None,
    p1: float = 1.0,
    p2: float = 1.0,
    volume_24h: float = 0,
    fee_tier: float = 0.003,
    liquidity: float = 1,
    volatility_24h: float = 0,
    exposure_pct: float = 0,
    risk_free: float = 0.0,
) -> dict:
    d = {}
    d["nvt"] = nvt_ratio(market_cap, transaction_volume)
    d["mvrv"] = mvrv_ratio(market_cap, realized_cap)
    d["sopr"] = sopr(transaction_volume, realized_cap)
    if returns_90d:
        d["sharpe_90d"] = sharpe_ratio(returns_90d, risk_free)
    d["il_break_even"] = il_break_even(p1, p2)
    d["fee_apy"] = fee_apy(volume_24h, fee_tier, liquidity)
    d["temperature"] = financial_temperature(volatility_24h, exposure_pct)
    return d
