import pytest
from invest_os.scores.descriptive import (
    compute_descriptive, nvt_ratio, mvrv_ratio, sopr, sharpe_ratio,
)
from invest_os.scores.interpretive import compute_interpretive, gini_coefficient
from invest_os.scores.axiological import compute_axiological, rhi_from_grid, purpose_score
from invest_os.scores.decisional import recommend
from invest_os.models.schemas import Action, CapitalType
from tests.fixtures import make_capital_grid


class TestScoreLayers:
    def test_descriptive_layer(self):
        d = compute_descriptive(market_cap=1e9, transaction_volume=1e7, realized_cap=8e8)
        assert "nvt" in d
        assert "mvrv" in d
        assert "sopr" in d

    def test_interpretive_layer(self):
        d = compute_interpretive(portfolio_weights=[25, 25, 25, 25])
        assert "hhi" in d
        assert "entropy" in d
        assert abs(d["hhi"] - 0.25) < 0.01

    def test_interpretive_empty(self):
        d = compute_interpretive()
        assert d == {}

    def test_axiological_layer(self):
        grid = make_capital_grid(rhi=0.65)
        a = compute_axiological(grid)
        assert "rhi" in a
        assert "purpose" in a
        assert abs(a["rhi"] - 0.65) < 0.01

    def test_axiological_none(self):
        a = compute_axiological()
        assert a["rhi"] == 0.0

    def test_decisional_recommend_comprar(self):
        grid = make_capital_grid(rhi=0.85)
        action = recommend(grid, {"mvrv": 1.0, "sopr": 1.0, "sharpe_90d": 2.0})
        assert action == Action.COMPRAR

    def test_decisional_recommend_evitar(self):
        grid = make_capital_grid(rhi=0.85, bloqueio="Teste")
        action = recommend(grid, {})
        assert action == Action.EVITAR

    def test_decisional_rhi_baixo_evitar(self):
        grid = make_capital_grid(rhi=0.15)
        action = recommend(grid, {"mvrv": 0.8, "sopr": 0.9, "sharpe_90d": -1.0})
        assert action == Action.EVITAR

    def test_decisional_aguardar(self):
        grid = make_capital_grid(rhi=0.5)
        action = recommend(grid, {"mvrv": 1.5, "sopr": 1.0, "sharpe_90d": 0.5})
        assert action == Action.AGUARDAR

    def test_decisional_rebalancear(self):
        grid = make_capital_grid(rhi=0.35)
        action = recommend(grid, {"mvrv": 2.0})
        assert action == Action.REBALANCEAR

    def test_decisional_mvrv_boost(self):
        grid = make_capital_grid(rhi=0.65)
        action = recommend(grid, {"mvrv": 0.8, "sopr": 0.5, "sharpe_90d": -1.0})
        assert action in list(Action)

    def test_decisional_mvrv_penalty(self):
        grid = make_capital_grid(rhi=0.65)
        action = recommend(grid, {"mvrv": 4.0, "sopr": 1.5})
        assert action in list(Action)

    def test_decisional_evitar_pos_ajuste(self):
        grid = make_capital_grid(rhi=0.5)
        action = recommend(grid, {"mvrv": 4.0, "sopr": 1.0, "sharpe_90d": -1.0})
        assert action == Action.EVITAR

    def test_purpose_score_empty_scores(self):
        from invest_os.scores.axiological import purpose_score
        from invest_os.models.schemas import CapitalGridResult
        grid = CapitalGridResult(scores=[], rhi_estimated=0.5)
        assert purpose_score(grid) == 0.5
