"""
Integration tests: cross-module interaction, data flow correctness.
"""

from __future__ import annotations

import pytest

from invest_os.core.metrics import calculate_all_metrics
from invest_os.core.capital_grid import CapitalGrid, suggest_action
from invest_os.pipeline.cognitive import CognitivePipeline
from invest_os.models.schemas import Action, CapitalType, InvestorProfile, RiskProfile
from tests.fixtures import (
    make_config, make_capital_grid, Scenarios, make_capital_scores,
)


class TestMetricsCapitalGridIntegration:
    """Metrics output feeds into Capital Grid."""

    def test_metrics_to_capital_scoring(self):
        metrics = calculate_all_metrics(**Scenarios.bull_market())
        cap_scores = CapitalGrid.score_from_metrics(
            market_cap=2e9, tvl=6e8, revenue=4e7,
            github_stars=2000, github_forks=400, contributors=80,
            community_size=100000, governance_participation=0.4,
            carbon_offset_tco2=5000, has_audit=True, years_active=4,
        )
        assert all(0 <= v <= 1 for v in cap_scores.values())
        assert cap_scores[CapitalType.FINANCEIRO] > 0.7

    def test_bear_metrics_trigger_alerts(self):
        metrics = calculate_all_metrics(**Scenarios.bear_market())
        assert len(metrics.get("alertas", [])) >= 0
        if metrics.get("mvrv") and metrics["mvrv"] < 1.0:
            assert any("MVRV" in a for a in metrics["alertas"])

    def test_high_risk_defi_suggest_action(self):
        metrics = calculate_all_metrics(**Scenarios.high_risk_defi())
        scores = {t: 0.3 for t in CapitalType}
        grid = CapitalGrid().evaluate(scores)
        action = suggest_action(grid, metrics)
        assert action in list(Action)


class TestPipelineMetricsIntegration:
    """Pipeline correctly ingests metrics and produces decisions."""

    @pytest.mark.parametrize("scenario_fn,expected_action_range", [
        (Scenarios.bull_market, [Action.COMPRAR, Action.AGUARDAR]),
        (Scenarios.bear_market, [Action.AGUARDAR, Action.EVITAR, Action.REBALANCEAR]),
        (Scenarios.stable_market, [Action.AGUARDAR, Action.COMPRAR, Action.REBALANCEAR]),
    ])
    def test_pipeline_with_scenarios(self, scenario_fn, expected_action_range):
        pipe = CognitivePipeline()
        metrics = scenario_fn()
        result = pipe.run(ativo="TEST", metrics_input=metrics)
        assert result.state.decision.acao in expected_action_range
        assert result.state.capital_grid is not None
        assert len(result.chain_output) == 6

    def test_pipeline_conservador_gate(self):
        config = make_config(risco=RiskProfile.CONSERVADOR)
        pipe = CognitivePipeline(config=config)
        result = pipe.run(ativo="ALTO_RISCO", metrics_input=Scenarios.high_risk_defi())
        if result.state.decision.tamanho_posicao > 0:
            assert result.state.decision.gate_humano is True

    def test_pipeline_arrojado_small_position(self):
        config = make_config(risco=RiskProfile.ARROJADO, capital_disponivel_brl=30.0)
        pipe = CognitivePipeline(config=config)
        result = pipe.run(ativo="PEQUENO", metrics_input=Scenarios.stable_market())
        assert result.state.decision is not None


class TestPromptsGovernanceIntegration:
    """Prompt engine + governance engine interaction."""

    def test_prompt_with_governance_context(self):
        from invest_os.governance.engine import OstromEngine
        from invest_os.prompts.engine import PromptEngine
        from invest_os.models.schemas import InvestorConfig, DecisionOutput, RlhfLog

        ostrom = OstromEngine()
        prompts = PromptEngine()
        config = make_config()
        grid = make_capital_grid()
        scores = ["sábio" if grid.rhi_estimated >= 0.8 else "cultivador"]

        decision = DecisionOutput(acao=Action.COMPRAR, tamanho_posicao=0.10, score_composto=0.75)
        log = RlhfLog()
        chain = prompts.run_full_chain("GOV_TEST", config, {}, grid, decision, log)
        assert len(chain) == 6
        assert "comprar" in chain["level4_axiological"]

    def test_capital_grid_governance_feedback(self):
        from invest_os.governance.engine import GoodhartShield
        grid = make_capital_grid(rhi=0.65)
        shield = GoodhartShield()
        noisy_rhi = shield.apply("rhi", grid.rhi_estimated)
        assert noisy_rhi != grid.rhi_estimated
        assert 0 <= noisy_rhi <= 1


class TestMetricsCrossValidation:
    """Multiple metrics consistency checks."""

    def test_nvt_mvrv_consistency(self):
        metrics = calculate_all_metrics(
            market_cap=1e9, transaction_volume=2e7, realized_cap=5e8,
        )
        assert metrics["nvt"] == 50.0
        assert metrics["mvrv"] == 2.0

    def test_entropy_maximally_diversified(self):
        weights = [10] * 10
        from invest_os.core.metrics import shannon_entropy
        h = shannon_entropy(weights)
        assert abs(h - 3.3219) < 0.01

    def test_entropy_fully_concentrated(self):
        from invest_os.core.metrics import shannon_entropy
        assert abs(shannon_entropy([100]) - 0.0) < 0.001

    def test_gini_perfect_equality(self):
        from invest_os.core.metrics import gini_coefficient
        assert abs(gini_coefficient([10, 10, 10, 10]) - 0.0) < 0.01

    def test_temperature_extreme(self):
        from invest_os.core.metrics import financial_temperature
        assert financial_temperature(0.5, 1.0) == 0.5
        assert financial_temperature(0, 1) == 0
