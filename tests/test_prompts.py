import pytest
from invest_os.prompts.engine import PromptEngine
from invest_os.models.schemas import (
    InvestorConfig, CognitiveMap, FinancialMetrics, CapitalGridResult,
    CapitalType, CapitalScore, DecisionOutput, Action, RlhfLog,
)


class TestPromptEngine:
    def setup_method(self):
        self.engine = PromptEngine()

    def test_level0_context(self):
        config = InvestorConfig(tese_impacto="ReFi Amazônia")
        prompt = self.engine.level0_context(config, "KlimaDAO")
        assert "KlimaDAO" in prompt
        assert "ReFi Amazônia" in prompt

    def test_level1_financial_dd(self):
        mapa = CognitiveMap()
        metrics = {"nvt": 100.5, "mvrv": 1.2, "sopr": 0.95}
        prompt = self.engine.level1_financial_dd(mapa, metrics)
        assert "100.50" in prompt
        assert "1.20" in prompt
        assert "0.95" in prompt

    def test_level2_regenerative_dd(self):
        scores = [CapitalScore(type=t, score=0.5, confidence=0.7) for t in CapitalType]
        grid = CapitalGridResult(scores=scores, rhi_estimated=0.5, shannon_h=1.5, gini=0.3)
        prompt = self.engine.level2_regenerative_dd(grid)
        assert "0.50" in prompt
        assert "Nenhum bloqueio" in prompt

    def test_level2_with_block(self):
        scores = [CapitalScore(type=t, score=0.3, confidence=0.5) for t in CapitalType]
        grid = CapitalGridResult(scores=scores, rhi_estimated=0.3, shannon_h=0.5, gini=0.6, bloqueio="Test block")
        prompt = self.engine.level2_regenerative_dd(grid)
        assert "Test block" in prompt

    def test_level3_semiotic(self):
        prompt = self.engine.level3_semiotic("ETH", {"nvt": 80})
        assert "ETH" in prompt

    def test_level4_axiological(self):
        config = InvestorConfig()
        decision = DecisionOutput(acao=Action.COMPRAR, tamanho_posicao=0.15, score_composto=0.72)
        prompt = self.engine.level4_axiological(decision, config)
        assert "comprar" in prompt
        assert "72" in prompt or "0.72" in prompt

    def test_level5_rlhf(self):
        log = RlhfLog(previsao="COMPRAR", realidade="lucro de 5%")
        prompt = self.engine.level5_rlhf(log)
        assert "COMPRAR" in prompt or "previu" in prompt

    def test_full_chain(self):
        config = InvestorConfig()
        scores = [CapitalScore(type=t, score=0.6, confidence=0.7) for t in CapitalType]
        grid = CapitalGridResult(scores=scores, rhi_estimated=0.6, shannon_h=2.0, gini=0.25)
        decision = DecisionOutput(acao=Action.AGUARDAR, tamanho_posicao=0.05, score_composto=0.55)
        log = RlhfLog()
        metrics = {"nvt": 100, "mvrv": 1.2, "sopr": 0.95, "sharpe_90d": 0.5}
        chain = self.engine.run_full_chain("BTC", config, metrics, grid, decision, log)
        assert len(chain) == 6
        assert "level0_context" in chain
        assert "level5_rlhf" in chain
