import pytest
from invest_os.core.capital_grid import CapitalGrid, interpret_rhi, suggest_action
from invest_os.models.schemas import CapitalType, CapitalGridResult, Action, CapitalScore


class TestCapitalGrid:
    def setup_method(self):
        self.grid = CapitalGrid()

    def test_evaluate_basic(self):
        scores = {t: 0.5 for t in CapitalType}
        result = self.grid.evaluate(scores, shannon_h=1.5, gini=0.3)
        assert result.rhi_estimated == 0.5
        assert result.bloqueio is None
        assert len(result.scores) == 8

    def test_evaluate_with_block_shannon(self):
        scores = {t: 0.5 for t in CapitalType}
        result = self.grid.evaluate(scores, shannon_h=0.5, gini=0.3)
        assert result.bloqueio is not None
        assert "Shannon" in result.bloqueio

    def test_evaluate_with_block_gini(self):
        scores = {t: 0.5 for t in CapitalType}
        result = self.grid.evaluate(scores, shannon_h=1.5, gini=0.7)
        assert result.bloqueio is not None
        assert "Gini" in result.bloqueio

    def test_rhi_different_scores(self):
        scores = {
            CapitalType.FINANCEIRO: 1.0,
            CapitalType.VIVO: 0.0,
            CapitalType.MATERIAL: 0.5,
            CapitalType.SOCIAL: 0.5,
            CapitalType.INTELECTUAL: 0.5,
            CapitalType.EXPERIENCIAL: 0.5,
            CapitalType.CULTURAL: 0.5,
            CapitalType.ESPIRITUAL: 0.5,
        }
        result = self.grid.evaluate(scores, shannon_h=2.0, gini=0.2)
        expected = (0.20 * 1.0 + 0.15 * 0.0 + 0.10 * 0.5 + 0.15 * 0.5 +
                    0.15 * 0.5 + 0.10 * 0.5 + 0.10 * 0.5 + 0.05 * 0.5)
        assert abs(result.rhi_estimated - expected) < 0.01

    def test_score_from_metrics(self):
        scores = CapitalGrid.score_from_metrics(
            market_cap=1e9,
            tvl=5e8,
            revenue=1e6,
            github_stars=1000,
            github_forks=200,
            contributors=50,
            community_size=50000,
            governance_participation=0.3,
            carbon_offset_tco2=10000,
            has_audit=True,
            years_active=4,
        )
        assert len(scores) == 8
        assert all(0 <= v <= 1 for v in scores.values())
        assert scores[CapitalType.FINANCEIRO] > 0.5
        assert scores[CapitalType.VIVO] > 0.5


class TestInterpretRHI:
    def test_semeador(self):
        assert interpret_rhi(0.1)[0] == "semeador"

    def test_brotador(self):
        assert interpret_rhi(0.3)[0] == "brotador"

    def test_cultivador(self):
        assert interpret_rhi(0.5)[0] == "cultivador"

    def test_guardiao(self):
        assert interpret_rhi(0.7)[0] == "guardião"

    def test_sabio(self):
        assert interpret_rhi(0.9)[0] == "sábio"


class TestSuggestAction:
    def test_comprar_alto_rhi(self):
        scores = [CapitalScore(type=t, score=0.9, confidence=0.7) for t in CapitalType]
        grid = CapitalGridResult(scores=scores, rhi_estimated=0.85, shannon_h=2.0, gini=0.2)
        action = suggest_action(grid, {"mvrv": 0.8, "sopr": 0.9, "sharpe_90d": 1.5})
        assert action == Action.COMPRAR

    def test_evitar_bloqueio(self):
        scores = [CapitalScore(type=t, score=0.9, confidence=0.7) for t in CapitalType]
        grid = CapitalGridResult(scores=scores, rhi_estimated=0.85, shannon_h=0.5, gini=0.2, bloqueio="Shannon")
        action = suggest_action(grid, {})
        assert action == Action.EVITAR
