from __future__ import annotations

from invest_os.models.schemas import (
    CapitalType, CapitalScore, CapitalGridResult, Action, CAPITAL_WEIGHTS,
)


class CapitalGrid:
    def __init__(self):
        self.weights = CAPITAL_WEIGHTS
        self.limits = {
            CapitalType.VIVO: ("shannon_h", 1.2, "Monocultura — Shannon H' < 1.2"),
            CapitalType.SOCIAL: ("gini", 0.5, "Plutocracia — Gini > 0.5"),
        }

    def evaluate(
        self,
        scores: dict[CapitalType, float],
        shannon_h: float = 0.0,
        gini: float = 0.0,
        evidence: dict[CapitalType, list[str]] = None,
    ) -> CapitalGridResult:
        if evidence is None:
            evidence = {}
        capital_scores = []
        for cap_type in CapitalType:
            score = min(max(scores.get(cap_type, 0.5), 0.0), 1.0)
            capital_scores.append(
                CapitalScore(
                    type=cap_type,
                    score=score,
                    confidence=0.7,
                    evidence=evidence.get(cap_type, []),
                )
            )

        bloqueio = None
        if shannon_h < self.limits[CapitalType.VIVO][1]:
            bloqueio = self.limits[CapitalType.VIVO][2]
        if gini > self.limits[CapitalType.SOCIAL][1]:
            _msg = self.limits[CapitalType.SOCIAL][2]
            bloqueio = bloqueio + "; " + _msg if bloqueio else _msg

        rhi = sum(
            cs.score * self.weights[cs.type]
            for cs in capital_scores
        )

        return CapitalGridResult(
            scores=capital_scores,
            rhi_estimated=round(rhi, 4),
            shannon_h=shannon_h,
            gini=gini,
            bloqueio=bloqueio,
        )

    @staticmethod
    def score_from_metrics(
        market_cap: float = 0,
        tvl: float = 0,
        revenue: float = 0,
        github_stars: int = 0,
        github_forks: int = 0,
        contributors: int = 0,
        community_size: int = 0,
        governance_participation: float = 0,
        carbon_offset_tco2: float = 0,
        has_audit: bool = False,
        years_active: float = 0,
    ) -> dict[CapitalType, float]:
        scores = {}

        fin_score = 0.3
        if tvl > 1e6:
            fin_score += 0.2
        if revenue > 1e5:
            fin_score += 0.2
        if has_audit:
            fin_score += 0.15
        if years_active > 2:
            fin_score += 0.15
        scores[CapitalType.FINANCEIRO] = min(fin_score, 1.0)

        scores[CapitalType.VIVO] = min(0.3 + (carbon_offset_tco2 / 10000) * 0.7, 1.0)

        mat_score = 0.4
        if years_active > 1:
            mat_score += 0.3
        if has_audit:
            mat_score += 0.3
        scores[CapitalType.MATERIAL] = min(mat_score, 1.0)

        soc_score = 0.3
        if governance_participation > 0.1:
            soc_score += 0.2
        if community_size > 1000:
            soc_score += 0.25
        if contributors > 10:
            soc_score += 0.25
        scores[CapitalType.SOCIAL] = min(soc_score, 1.0)

        int_score = 0.3
        if github_stars > 100:
            int_score += 0.2
        if github_forks > 20:
            int_score += 0.2
        if contributors > 5:
            int_score += 0.15
        if has_audit:
            int_score += 0.15
        scores[CapitalType.INTELECTUAL] = min(int_score, 1.0)

        exp_score = 0.4
        if years_active > 2:
            exp_score += 0.3
        if contributors > 10:
            exp_score += 0.3
        scores[CapitalType.EXPERIENCIAL] = min(exp_score, 1.0)

        cul_score = 0.3
        if community_size > 5000:
            cul_score += 0.3
        if governance_participation > 0.2:
            cul_score += 0.2
        if github_stars > 500:
            cul_score += 0.2
        scores[CapitalType.CULTURAL] = min(cul_score, 1.0)

        esp_score = 0.5
        if carbon_offset_tco2 > 100:
            esp_score += 0.3
        if governance_participation > 0.3:
            esp_score += 0.2
        scores[CapitalType.ESPIRITUAL] = min(esp_score, 1.0)

        return scores


def interpret_rhi(rhi: float) -> tuple[str, str, str]:
    if rhi < 0.2:
        return "semeador", "0-20", "Aprendendo; posições pequenas; foco educacional"
    elif rhi < 0.4:
        return "brotador", "21-40", "Primeiros impactos; diversificação inicial"
    elif rhi < 0.6:
        return "cultivador", "41-60", "Portfolio equilibrado; impacto mensurável"
    elif rhi < 0.8:
        return "guardião", "61-80", "Proteção de valor; mentoria de outros"
    else:
        return "sábio", "81-100", "Individuação completa; legado regenerativo"


def suggest_action(capital_grid: CapitalGridResult, metrics: dict) -> Action:
    if capital_grid.bloqueio:
        return Action.EVITAR

    score = capital_grid.rhi_estimated

    mvrv = metrics.get("mvrv", 1.5)
    if mvrv is not None and mvrv < 1.0:
        score += 0.15
    if mvrv is not None and mvrv > 3.5:
        score -= 0.2

    sopr = metrics.get("sopr", 1.0)
    if sopr is not None and sopr < 1.0:
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
