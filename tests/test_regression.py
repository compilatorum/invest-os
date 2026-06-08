"""
Regression tests: edge cases, boundary conditions, all branches.
Covers every missing line identified by coverage analysis.
"""

from __future__ import annotations

import math
import random

import pytest

from invest_os.core.metrics import (
    sharpe_ratio, il_break_even, sopr, gini_coefficient,
    pbo_probability, min_track_record_length, fee_apy,
    financial_temperature, nvt_ratio, mvrv_ratio,
    herfindahl_hirschman_index, shannon_entropy,
)
from invest_os.core.capital_grid import CapitalGrid, suggest_action, interpret_rhi
from invest_os.models.schemas import (
    CapitalType, CapitalGridResult, CapitalScore, Action,
    RiskProfile, InvestorProfile, InvestorConfig,
)
from invest_os.governance.engine import GoodhartShield, OstromEngine, OstromPrinciple, OstromRule
from invest_os.pipeline.cognitive import CognitivePipeline
from invest_os.prompts.engine import PromptEngine, load_prompt_repo, render_prompt
from invest_os.utils.math_tools import (
    lotka_volterra, cosine_similarity, js_divergence,
    geometric_brownian_motion, price_from_bonding_curve,
    augmented_bonding_curve_price, il_protected_shares,
)
from tests.fixtures import make_capital_grid, make_capital_scores


# ── metrics.py gap coverage ────────────────────────────────────────────────

class TestMetricsRegression:
    def test_sharpe_variance_zero(self):
        assert sharpe_ratio([5.0, 5.0, 5.0]) is None

    def test_il_break_even_zero_inputs(self):
        assert il_break_even(0, 100) == 0.0
        assert il_break_even(100, 0) == 0.0
        assert il_break_even(0, 0) == 0.0
        assert il_break_even(-1, 100) == 0.0

    def test_sopr_boundary(self):
        assert sopr(50, 100) == 0.5
        assert sopr(0, 100) == 0.0
        assert sopr(100, 0) is None

    def test_gini_mean_zero(self):
        assert gini_coefficient([0, 0, 0]) == 0.0

    def test_pbo_short_series(self):
        assert pbo_probability([0.01, 0.02]) == 0.5

    def test_pbo_zero_std(self):
        random.seed(42)
        assert pbo_probability([1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]) == 0.5

    def test_pbo_normal_run(self):
        random.seed(42)
        prob = pbo_probability([0.01, 0.02, -0.01, 0.015, 0.005, 0.01, -0.02, 0.03, 0.01, 0.005])
        assert 0 <= prob <= 1

    def test_min_track_record_zero_sharpe(self):
        assert min_track_record_length(0) == float("inf")
        assert min_track_record_length(-0.5) == float("inf")

    def test_min_track_record_positive_sharpe(self):
        length = min_track_record_length(1.0, skew=0.5, kurt=4.0)
        assert length < float("inf")
        assert length > 0

    def test_nvt_ratio(self):
        assert nvt_ratio(100, 0) == float("inf")
        assert nvt_ratio(0, 100) == 0.0

    def test_mvrv_ratio_zero(self):
        assert mvrv_ratio(100, 0) is None

    def test_hhi_empty(self):
        assert herfindahl_hirschman_index([]) == 0.0
        assert herfindahl_hirschman_index([0, 0]) == 0.0

    def test_shannon_empty(self):
        assert shannon_entropy([]) == 0.0
        assert abs(shannon_entropy([1, 0]) - 0.0) < 0.001

    def test_fee_apy_zero_liquidity(self):
        assert fee_apy(1000, 0.003, 0) is None


# ── capital_grid.py gap coverage ───────────────────────────────────────────

class TestCapitalGridRegression:
    def test_governance_high_participation(self, capital_grid):
        scores = CapitalGrid.score_from_metrics(
            governance_participation=0.5, carbon_offset_tco2=200,
        )
        assert scores[CapitalType.ESPIRITUAL] > 0.7

    def test_suggest_mvrv_high(self):
        grid = make_capital_grid(rhi=0.6)
        action = suggest_action(grid, {"mvrv": 4.0, "sopr": 1.0, "sharpe_90d": 0.5})
        assert action in list(Action)

    def test_suggest_sharpe_low(self):
        grid = make_capital_grid(rhi=0.6)
        action = suggest_action(grid, {"mvrv": 1.5, "sopr": 1.0, "sharpe_90d": -1.0})
        assert action in list(Action)

    def test_suggest_comprar(self):
        grid = make_capital_grid(rhi=0.85)
        action = suggest_action(grid, {"mvrv": 1.2, "sopr": 1.1, "sharpe_90d": 1.5})
        assert action == Action.COMPRAR

    def test_suggest_aguardar(self):
        grid = make_capital_grid(rhi=0.55)
        action = suggest_action(grid, {"mvrv": 1.5, "sopr": 1.0, "sharpe_90d": 0.3})
        assert action == Action.AGUARDAR

    def test_suggest_rebalancear(self):
        grid = make_capital_grid(rhi=0.35)
        action = suggest_action(grid, {"mvrv": 1.5, "sopr": 1.0, "sharpe_90d": 0.0})
        assert action == Action.REBALANCEAR

    def test_suggest_evitar(self):
        grid = make_capital_grid(rhi=0.15)
        action = suggest_action(grid, {"mvrv": 0.5, "sopr": 0.8, "sharpe_90d": -2.0})
        assert action == Action.EVITAR

    def test_suggest_evitar_apos_ajuste(self):
        grid = make_capital_grid(rhi=0.22, bloqueio=None)
        action = suggest_action(grid, {"mvrv": 4.0, "sopr": 1.2, "sharpe_90d": -2.0})
        assert action == Action.EVITAR

    def test_interpret_rhi_all_levels(self):
        assert interpret_rhi(0.1)[0] == "semeador"
        assert interpret_rhi(0.3)[0] == "brotador"
        assert interpret_rhi(0.5)[0] == "cultivador"
        assert interpret_rhi(0.7)[0] == "guardião"
        assert interpret_rhi(0.9)[0] == "sábio"

    def test_shannon_block(self, capital_grid):
        result = capital_grid.evaluate({t: 0.5 for t in CapitalType}, shannon_h=0.5)
        assert result.bloqueio is not None

    def test_gini_block(self, capital_grid):
        result = capital_grid.evaluate({t: 0.5 for t in CapitalType}, gini=0.7)
        assert result.bloqueio is not None

    def test_score_from_metrics_minimal(self):
        scores = CapitalGrid.score_from_metrics()
        assert all(0 <= v <= 1 for v in scores.values())

    def test_tvl_stars_contributors_all_boundaries(self):
        scores = CapitalGrid.score_from_metrics(
            market_cap=0, tvl=0, revenue=0,
            github_stars=0, github_forks=0, contributors=0,
            community_size=0, governance_participation=0,
            carbon_offset_tco2=0, has_audit=False, years_active=0,
        )
        assert all(0 <= v <= 1 for v in scores.values())


# ── governance/engine.py gap coverage ──────────────────────────────────────

class TestGovernanceRegression:
    def test_rule_not_enabled(self, ostrom):
        ostrom.rules[0].enabled = False
        context = {"has_sbt": True}
        results = ostrom.check_governance(context)
        assert results["Fronteiras Claras"] is False

    def test_history_truncation(self, shield):
        for i in range(105):
            shield.add_observation("test", float(i))
        assert len(shield._metric_history["test"]) == 100

    def test_drift_variance_zero(self, shield):
        for _ in range(15):
            shield.add_observation("constant", 1.0)
        assert not shield.drift_detected("constant")

    def test_drift_detected_true(self, shield):
        for _ in range(20):
            shield.add_observation("noisy", 0.5)
        shield.add_observation("noisy", 10.0)
        assert shield.drift_detected("noisy")

    def test_governance_all_contexts(self, ostrom):
        contexts = [
            {},
            {"has_sbt": True},
            {"has_sbt": True, "local_config": True},
            {"has_sbt": True, "local_config": True, "voting_enabled": True,
             "has_oracles": True, "has_slashing": True, "has_dispute_resolution": True,
             "has_legal_framework": True, "is_dao_of_daos": True},
        ]
        for ctx in contexts:
            score, _ = ostrom.evaluate_score(ctx)
            assert 0 <= score <= 1


# ── pipeline/cognitive.py gap coverage ─────────────────────────────────────

class TestPipelineRegression:
    def test_camada4_no_grid_yet(self, pipeline):
        pipeline.state.capital_grid = None
        decision = pipeline.camada4_decisao({"mvrv": 1.5, "sharpe_90d": 1.2})
        assert decision is not None

    def test_camada4_comprar_branch(self, pipeline):
        cg = make_capital_grid(rhi=0.85)
        pipeline.state.capital_grid = cg
        decision = pipeline.camada4_decisao({"mvrv": 1.5, "sharpe_90d": 1.5})
        assert decision.acao == Action.COMPRAR
        assert decision.tamanho_posicao > 0

    def test_camada4_rebalancear_branch(self, pipeline):
        cg = make_capital_grid(rhi=0.35)
        pipeline.state.capital_grid = cg
        decision = pipeline.camada4_decisao({"mvrv": 2.0, "sharpe_90d": 0.0})
        assert decision.acao == Action.REBALANCEAR
        assert decision.tamanho_posicao < 0

    def test_camada4_mvrv_boost(self, pipeline):
        cg = make_capital_grid(rhi=0.5)
        pipeline.state.capital_grid = cg
        decision = pipeline.camada4_decisao({"mvrv": 0.8, "sharpe_90d": 0.5})
        assert decision.score_composto > 0.5

    def test_camada4_sharpe_boost(self, pipeline):
        cg = make_capital_grid(rhi=0.5)
        pipeline.state.capital_grid = cg
        decision = pipeline.camada4_decisao({"mvrv": 1.5, "sharpe_90d": 1.2})
        assert decision.score_composto > 0.5

    def test_camada4_gate_por_bloqueio(self, pipeline):
        cg = make_capital_grid(rhi=0.8, bloqueio="Monocultura")
        pipeline.state.capital_grid = cg
        decision = pipeline.camada4_decisao({"mvrv": 1.5, "sharpe_90d": 0.5})
        assert decision.gate_humano is True

    def test_camada5_with_feedback(self, pipeline):
        pipeline.camada2_semiose()
        pipeline.camada4_decisao({})
        log = pipeline.camada5_registro({"realidade": "lucro 5%", "rhi_real": 0.7, "level_up": True})
        assert log.rhi_real == 0.7
        assert log.level_up is True


# ── prompts/engine.py gap coverage ─────────────────────────────────────────

class TestPromptsRegression:
    def test_load_prompt_repo(self):
        repo = load_prompt_repo()
        assert len(repo) >= 6
        assert "level0_context" in repo

    def test_render_prompt(self):
        result = render_prompt("Hello {NAME}", NAME="World")
        assert result == "Hello World"

    def test_render_prompt_multiple(self):
        result = render_prompt("{A} + {B} = {C}", A="1", B="2", C="3")
        assert result == "1 + 2 = 3"

    def test_rhi_level_semeador(self, prompt_engine):
        assert prompt_engine._rhi_level(0.1) == "semeador"

    def test_rhi_level_sabio(self, prompt_engine):
        assert prompt_engine._rhi_level(0.9) == "sábio"

    def test_rhi_level_cultivador(self, prompt_engine):
        assert prompt_engine._rhi_level(0.5) == "cultivador"

    def test_level2_with_block_and_gini(self, prompt_engine):
        from tests.fixtures import make_capital_grid
        grid = make_capital_grid(rhi=0.3, shannon_h=0.5, gini=0.6,
                                 bloqueio="Monocultura + Plutocracia")
        prompt = prompt_engine.level2_regenerative_dd(grid)
        assert "Monocultura" in prompt


# ── models/schemas.py gap coverage ─────────────────────────────────────────

class TestSchemasRegression:
    def test_investor_config_properties(self):
        for risco in RiskProfile:
            config = InvestorConfig(risco=risco)
            assert config.gate_timeout == 3600
            assert isinstance(config.gate_default, str)
            assert isinstance(config.limite_autonomo_brl, float)

    def test_investor_profiles(self):
        for perfil in InvestorProfile:
            config = InvestorConfig(perfil=perfil)
            assert config.perfil == perfil


# ── utils/math_tools.py gap coverage ───────────────────────────────────────

class TestMathToolsRegression:
    def test_lotka_negative_path(self):
        v, f = lotka_volterra(0.1, 99.0, 0.001, 0.5, 100, 100, 0.5, 20)
        assert all(x >= 0 for x in v)
        assert all(x >= 0 for x in f)

    def test_cosine_similarity_zero(self):
        assert cosine_similarity([0, 0], [1, 1]) == 0.0
        assert cosine_similarity([0, 0], [0, 0]) == 0.0

    def test_js_divergence(self):
        p = [0.5, 0.5]
        q = [0.5, 0.5]
        assert abs(js_divergence(p, q)) < 0.001

    def test_gbm_basic(self):
        path = geometric_brownian_motion(100, 0.05, 0.2, 0.01, 10)
        assert len(path) == 11
        assert path[0] == 100
        assert all(p > 0 for p in path)

    def test_lotka_volterra_long(self):
        v, f = lotka_volterra(0.5, 0.01, 0.01, 0.3, 40, 10, 0.01, 500)
        assert len(v) == 501
        assert len(f) == 501

    def test_price_from_bonding_curve_zero_supply(self):
        price = price_from_bonding_curve(0, 50000, 0.5)
        assert price == 0.0

    def test_augmented_bonding_curve(self):
        price = augmented_bonding_curve_price(100, 50000, theta=0.2, friction=0.01)
        base = price_from_bonding_curve(100, 50000, 0.5)
        assert price != base
        assert price > 0

    def test_il_protected_shares(self):
        result = il_protected_shares(100, 1000)
        assert result > 100
        result_neg = il_protected_shares(100, -1)
        assert result_neg == 100
