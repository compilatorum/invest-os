"""
System tests: full workflows, multi-step scenarios, end-to-end pipelines.
"""

from __future__ import annotations

import pytest

from invest_os.pipeline.cognitive import CognitivePipeline
from invest_os.core.metrics import calculate_all_metrics
from invest_os.core.capital_grid import CapitalGrid
from invest_os.models.schemas import (
    Action, CapitalType, RiskProfile, InvestorProfile,
)
from tests.fixtures import Scenarios, make_config, make_capital_grid


class TestSystemFullWorkflow:
    """Complete system workflow: metrics → grid → pipeline → decision."""

    def test_full_workflow_bull(self):
        """Bull market should suggest COMPRAR or AGUARDAR."""
        pipe = CognitivePipeline()
        result = pipe.run(ativo="BTC", metrics_input=Scenarios.bull_market())
        assert result.state.metrics.nvt is not None
        assert result.state.capital_grid is not None
        assert result.state.semiotic is not None
        assert result.state.decision is not None
        assert result.state.decision.acao in (Action.COMPRAR, Action.AGUARDAR)
        assert len(result.state.history) == 1

    def test_full_workflow_bear(self):
        """Bear market should trigger alerts and suggest defensive action."""
        pipe = CognitivePipeline()
        result = pipe.run(ativo="ETH", metrics_input=Scenarios.bear_market())
        assert result.state.metrics.mvrv is not None
        assert result.state.decision.acao in (Action.AGUARDAR, Action.EVITAR, Action.REBALANCEAR)

    def test_full_workflow_stable(self):
        """Stable market should produce moderate scores."""
        pipe = CognitivePipeline()
        result = pipe.run(ativo="USDC", metrics_input=Scenarios.stable_market())
        assert 0.3 <= result.state.decision.score_composto <= 0.9

    def test_full_workflow_high_risk(self):
        """High risk DeFi should trigger human gate."""
        config = make_config(risco=RiskProfile.CONSERVADOR)
        pipe = CognitivePipeline(config=config)
        result = pipe.run(ativo="SHITCOIN", metrics_input=Scenarios.high_risk_defi())
        if result.state.decision.tamanho_posicao > 0:
            assert result.state.decision.gate_humano is True

    def test_workflow_with_feedback_loop(self):
        """Pipeline + RLHF feedback loop."""
        pipe = CognitivePipeline()
        result1 = pipe.run(ativo="BTC", metrics_input=Scenarios.bull_market(),
                           feedback={"realidade": "lucro 5%"})
        assert result1.state.history[0].realidade == "lucro 5%"

        result2 = pipe.run(ativo="BTC", metrics_input=Scenarios.bull_market(),
                           feedback={"realidade": "lucro 3%", "level_up": True})
        assert len(result2.state.history) == 2

    def test_workflow_with_capital_block(self):
        """Capital grid bloqueio should force EVITAR."""
        pipe = CognitivePipeline()
        result = pipe.run(
            ativo="BAD_PROTOCOL",
            metrics_input=Scenarios.bear_market(),
            capital_scores_kwargs={"shannon_h": 0.3, "gini": 0.7},
        )
        assert result.state.capital_grid.bloqueio is not None
        assert result.state.decision.acao == Action.EVITAR


class TestSystemMultipleProfiles:
    """System behavior across different investor profiles."""

    @pytest.mark.parametrize("perfil,risco", [
        (InvestorProfile.SEMEADOR, RiskProfile.CONSERVADOR),
        (InvestorProfile.BROTADOR, RiskProfile.MODERADO),
        (InvestorProfile.CULTIVADOR, RiskProfile.MODERADO),
        (InvestorProfile.GUARDIAO, RiskProfile.ARROJADO),
        (InvestorProfile.SABIO, RiskProfile.ARROJADO),
    ])
    def test_each_profile_completes_pipeline(self, perfil, risco):
        config = make_config(perfil=perfil, risco=risco)
        pipe = CognitivePipeline(config=config)
        result = pipe.run(ativo=f"TEST_{perfil.value.upper()}")
        assert result.state.decision is not None
        assert result.elapsed_ms > 0


class TestSystemEndToEnd:
    """True end-to-end: external data → metric calculation → full pipeline."""

    def test_e2e_mock_market_data(self):
        data = {
            "BTC": {"market_cap": 1.2e12, "volume_24h": 3e10, "realized_cap": 8e11},
            "ETH": {"market_cap": 4e11, "volume_24h": 1.5e10, "realized_cap": 3e11},
            "SOL": {"market_cap": 8e10, "volume_24h": 5e9, "realized_cap": 4e10},
        }

        for ativo, vals in data.items():
            metrics = calculate_all_metrics(
                market_cap=vals["market_cap"],
                transaction_volume=vals["volume_24h"],
                realized_cap=vals["realized_cap"],
            )
            assert metrics["nvt"] > 0
            assert metrics["mvrv"] > 0

            pipe = CognitivePipeline()
            result = pipe.run(ativo=ativo, metrics_input=vals)
            assert result.state.metrics.nvt > 0
            assert result.state.capital_grid.rhi_estimated > 0
            assert result.chain_output is not None

    def test_e2e_multi_asset_portfolio(self):
        assets = ["BTC", "ETH", "SOL", "ADA", "DOT"]
        results = []
        for ativo in assets:
            pipe = CognitivePipeline()
            r = pipe.run(ativo=ativo, metrics_input=Scenarios.stable_market())
            results.append(r)

        scores = [r.state.decision.score_composto for r in results]
        assert all(0 <= s <= 1 for s in scores)
        assert all(r.state.capital_grid.rhi_estimated > 0 for r in results)

    def test_e2e_full_cycle_with_prompt_output(self):
        pipe = CognitivePipeline()
        result = pipe.run(ativo="PROMT_TEST", metrics_input=Scenarios.bull_market())

        chain = result.chain_output
        assert "level0_context" in chain
        assert "level5_rlhf" in chain
        assert "PROMT_TEST" in chain["level0_context"]
        assert "comprar" in chain["level4_axiological"] or "aguardar" in chain["level4_axiological"]
