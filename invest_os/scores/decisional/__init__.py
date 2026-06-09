from __future__ import annotations

from invest_os.models.schemas import CapitalGridResult, Action


def recommend(grid: CapitalGridResult, metrics: dict) -> Action:
    if grid.bloqueio:
        return Action.EVITAR
    if grid.rhi_estimated < 0.2:
        return Action.EVITAR
    score = grid.rhi_estimated
    mvrv = metrics.get("mvrv", 1.5)
    if mvrv is not None and mvrv < 1.0:
        score += 0.15
    if mvrv is not None and mvrv > 3.5:
        score -= 0.2
    sopr_ = metrics.get("sopr", 1.0)
    if sopr_ is not None and sopr_ < 1.0:
        score += 0.1
    sharpe = metrics.get("sharpe_90d")
    if sharpe is not None and sharpe > 1.0:
        score += 0.1
    if sharpe is not None and sharpe < -0.5:
        score -= 0.1
    if score >= 0.7:
        return Action.COMPRAR
    elif score >= 0.45:
        return Action.AGUARDAR
    elif score >= 0.25:
        return Action.REBALANCEAR
    else:
        return Action.EVITAR
