from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from invest_os.models.schemas import (
    InvestorConfig, CapitalGridResult, CapitalType, Action,
    DecisionOutput, FinancialMetrics, RlhfLog, RiskProfile, InvestorProfile,
)
from invest_os.core.metrics import calculate_all_metrics
from invest_os.core.capital_grid import CapitalGrid
from invest_os.pipeline.cognitive import CognitivePipeline
from invest_os.prompts.engine import PromptEngine
from invest_os.governance.engine import OstromEngine, GoodhartShield


# ── Shared Fixtures ────────────────────────────────────────────────────────

@pytest.fixture
def config() -> InvestorConfig:
    return InvestorConfig(
        nome="fixture_tester",
        perfil=InvestorProfile.CULTIVADOR,
        risco=RiskProfile.MODERADO,
        tese_impacto="ReFi Amazônia",
        capital_disponivel_brl=5000.0,
    )


@pytest.fixture
def capital_grid() -> CapitalGrid:
    return CapitalGrid()


@pytest.fixture
def pipeline(config: InvestorConfig) -> CognitivePipeline:
    return CognitivePipeline(config=config)


@pytest.fixture
def prompt_engine() -> PromptEngine:
    return PromptEngine()


@pytest.fixture
def ostrom() -> OstromEngine:
    return OstromEngine()


@pytest.fixture
def shield() -> GoodhartShield:
    return GoodhartShield()


@pytest.fixture
def bull_metrics() -> dict:
    return calculate_all_metrics(**{
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
    })


@pytest.fixture
def bear_metrics() -> dict:
    return calculate_all_metrics(**{
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
    })


@pytest.fixture
def full_capital_grid() -> CapitalGridResult:
    from tests.fixtures import make_capital_grid
    return make_capital_grid()


@pytest.fixture
def temp_dir(tmp_path: Path) -> Path:
    return tmp_path
