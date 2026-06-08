"""
Fixtures, test doubles, factories, and scenarios for the InvestmentOS test suite.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Optional

from invest_os.models.schemas import (
    InvestorConfig, FinancialMetrics, CapitalGridResult, CapitalScore,
    CapitalType, CognitiveMap, SemioticAnalysis, DecisionOutput,
    Action, RlhfLog, RiskProfile, InvestorProfile, AlchemicalPhase,
    SystemState,
)


# ── Factory Functions ─────────────────────────────────────────────────────

def make_config(**overrides: Any) -> InvestorConfig:
    defaults = dict(
        nome="testador",
        perfil=InvestorProfile.CULTIVADOR,
        risco=RiskProfile.MODERADO,
        tese_impacto="ReFi Amazônia",
        capital_disponivel_brl=5000.0,
        modo_linguagem="hibrido",
    )
    defaults.update(overrides)
    return InvestorConfig(**defaults)


def make_metrics(**overrides: Any) -> FinancialMetrics:
    defaults = dict(
        nvt=100.0,
        mvrv=1.25,
        sopr=1.05,
        sharpe_90d=0.85,
        il_break_even=-0.0041,
        fee_apy=0.12,
        hhi=0.18,
        ps_ratio=25.0,
        temperature=0.01,
        entropy=1.85,
    )
    defaults.update(overrides)
    return FinancialMetrics(**defaults)


def make_capital_scores(
    base: float = 0.6,
    overrides: Optional[dict[CapitalType, float]] = None,
) -> list[CapitalScore]:
    ov = overrides or {}
    return [
        CapitalScore(type=t, score=ov.get(t, base), confidence=0.7)
        for t in CapitalType
    ]


def make_capital_grid(
    rhi: float = 0.65,
    shannon_h: float = 1.8,
    gini: float = 0.25,
    bloqueio: Optional[str] = None,
    base_score: float = 0.6,
    score_overrides: Optional[dict[CapitalType, float]] = None,
) -> CapitalGridResult:
    return CapitalGridResult(
        scores=make_capital_scores(base_score, score_overrides),
        rhi_estimated=rhi,
        shannon_h=shannon_h,
        gini=gini,
        bloqueio=bloqueio,
    )


def make_semiotic(**overrides: Any) -> SemioticAnalysis:
    defaults = dict(
        sign="Preço em queda com volume crescente",
        object="Fundamentos on-chain mostram acumulação",
        interpretant=["Capitulação de curt prazo", "Acumulação de longo prazo"],
        coherence=0.65,
        noise=0.35,
        phase=AlchemicalPhase.ALBEDO,
    )
    defaults.update(overrides)
    return SemioticAnalysis(**defaults)


def make_decision(**overrides: Any) -> DecisionOutput:
    defaults = dict(
        acao=Action.AGUARDAR,
        tamanho_posicao=0.05,
        score_composto=0.55,
        narrativa="Score composto 55.0%. Ação: aguardar. Posição: 5.0%.",
        metadata_nft={"name": "Position NFT", "score": 0.55},
        gate_humano=False,
    )
    defaults.update(overrides)
    return DecisionOutput(**defaults)


def make_rlhf(**overrides: Any) -> RlhfLog:
    defaults = dict(
        previsao="AGUARDAR",
        realidade="mercado subiu 3%",
        delta_capital={"financeiro": 0.03},
        prompt_melhoria="Ajustar limiar de sharpe para 0.8",
        rhi_real=0.62,
        rhi_estimado=0.65,
        level_up=False,
    )
    defaults.update(overrides)
    return RlhfLog(**defaults)


# ── Scenario Builders ──────────────────────────────────────────────────────

class Scenarios:
    """Pre-built market scenarios for tests."""

    @staticmethod
    def bull_market() -> dict:
        return {
            "market_cap": 2e9,
            "transaction_volume": 5e7,
            "realized_cap": 1.2e9,
            "returns_90d": [0.05, 0.03, 0.04, 0.02, 0.06],
            "volume_24h": 5e7,
            "fee_tier": 0.003,
            "liquidity": 2e8,
            "portfolio_weights": [30, 25, 20, 15, 10],
            "volatility_24h": 0.03,
            "exposure_pct": 0.15,
            "p1": 100.0,
            "p2": 150.0,
        }

    @staticmethod
    def bear_market() -> dict:
        return {
            "market_cap": 3e8,
            "transaction_volume": 2e7,
            "realized_cap": 5e8,
            "returns_90d": [-0.03, -0.05, -0.02, -0.04, -0.01],
            "volume_24h": 2e7,
            "fee_tier": 0.003,
            "liquidity": 5e7,
            "portfolio_weights": [50, 30, 20],
            "volatility_24h": 0.12,
            "exposure_pct": 0.3,
            "p1": 100.0,
            "p2": 60.0,
        }

    @staticmethod
    def stable_market() -> dict:
        return {
            "market_cap": 1e9,
            "transaction_volume": 1e7,
            "realized_cap": 9e8,
            "returns_90d": [0.01, -0.005, 0.008, 0.002, -0.003],
            "volume_24h": 1e7,
            "fee_tier": 0.003,
            "liquidity": 1e8,
            "portfolio_weights": [25, 25, 25, 25],
            "volatility_24h": 0.04,
            "exposure_pct": 0.1,
            "p1": 100.0,
            "p2": 105.0,
        }

    @staticmethod
    def high_risk_defi() -> dict:
        return {
            "market_cap": 5e7,
            "transaction_volume": 1e6,
            "realized_cap": 1e7,
            "returns_90d": [0.15, -0.10, 0.08, -0.12, 0.20],
            "volume_24h": 1e6,
            "fee_tier": 0.01,
            "liquidity": 1e6,
            "portfolio_weights": [80, 20],
            "volatility_24h": 0.25,
            "exposure_pct": 0.5,
            "p1": 10.0,
            "p2": 25.0,
        }


# ── CLI Test Doubles ───────────────────────────────────────────────────────

SAMPLE_CLI_OUTPUTS = {
    "version": "🧬 InvestmentOS v1.0.0",
    "analyze_json": json.dumps({
        "metrics": {"nvt": 100.0, "mvrv": 1.25},
        "alertas": [],
        "capital_grid": {"rhi_estimated": 0.65},
        "rhi": 0.65,
        "nivel_arquetipo": "cultivador",
    }),
    "governance_json": json.dumps({
        "score": 0.75,
        "principios_atendidos": 6,
        "principios_total": 8,
        "failed": ["Fronteiras Claras", "Congruência Local"],
    }),
}


# ── Config file helpers ────────────────────────────────────────────────────

def write_test_config(path: Path, **overrides: Any) -> Path:
    data = {
        "nome": "testador",
        "perfil": "cultivador",
        "risco": "moderado",
        "tese_impacto": "ReFi Amazônia",
        "capital_disponivel_brl": 5000.0,
        "modo_linguagem": "hibrido",
    }
    data.update(overrides)
    path.write_text(json.dumps(data, indent=2))
    return path
