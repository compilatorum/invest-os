from __future__ import annotations

import math
import random


def choquet_expected_value(min_val: float, expected: float, c: float = 0.3) -> float:
    return c * min_val + (1 - c) * expected


def geometric_brownian_motion(s0: float, mu: float, sigma: float, dt: float, n_steps: int) -> list[float]:
    path = [s0]
    for _ in range(n_steps):
        z = random.gauss(0, 1)
        s_next = path[-1] * math.exp((mu - 0.5 * sigma ** 2) * dt + sigma * math.sqrt(dt) * z)
        path.append(s_next)
    return path


def lotka_volterra(alpha: float, beta: float, delta: float, gamma: float,
                   v0: float, f0: float, dt: float, n_steps: int) -> tuple[list[float], list[float]]:
    v, f = v0, f0
    v_hist, f_hist = [v], [f]
    for _ in range(n_steps):
        dv = (alpha * v - beta * v * f) * dt
        df = (delta * v * f - gamma * f) * dt
        v += dv
        f += df
        v = max(v, 0)
        f = max(f, 0)
        v_hist.append(v)
        f_hist.append(f)
    return v_hist, f_hist


def cosine_similarity(v1: list[float], v2: list[float]) -> float:
    dot = sum(a * b for a, b in zip(v1, v2))
    n1 = math.sqrt(sum(a ** 2 for a in v1))
    n2 = math.sqrt(sum(b ** 2 for b in v2))
    if n1 * n2 == 0:
        return 0.0
    return dot / (n1 * n2)


def js_divergence(p: list[float], q: list[float]) -> float:
    m = [(a + b) / 2 for a, b in zip(p, q)]
    def kl(a, b):
        return sum(x * math.log2(x / y) if x > 0 and y > 0 else 0 for x, y in zip(a, b))
    return 0.5 * kl(p, m) + 0.5 * kl(q, m)


def price_from_bonding_curve(supply: float, reserve: float, reserve_ratio: float) -> float:
    if supply <= 0 or reserve_ratio <= 0:
        return 0.0
    return reserve / (supply * reserve_ratio)


def augmented_bonding_curve_price(supply: float, reserve: float,
                                   theta: float = 0.2, friction: float = 0.01) -> float:
    base = price_from_bonding_curve(supply, reserve, 0.5)
    return base * (1 + theta * math.sin(supply * 0.001)) * (1 - friction)


def il_protected_shares(assets: float, total_supply: float, offset: int = 6) -> float:
    return (assets * (total_supply + 10 ** offset)) / (total_supply + 1) if total_supply >= 0 else assets


def conviction_vote(prev_conviction: float, alpha: float, votes: float) -> float:
    return prev_conviction * alpha + votes


def antifragility_score(average_recovery: float, max_drawdown: float) -> float:
    if max_drawdown <= 0:
        return float("inf")
    return average_recovery / max_drawdown


def rwi(return_financeiro: float, impacto_monetizado: float, capital_investido: float) -> Optional[float]:
    if capital_investido <= 0:
        return None
    return (return_financeiro + impacto_monetizado) / capital_investido
