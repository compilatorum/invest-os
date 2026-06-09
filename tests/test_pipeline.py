import pytest
from invest_os.pipeline.cognitive import CognitivePipeline
from invest_os.models.schemas import CapitalType, Action
from invest_os.signals.base import MarketSignal


class TestCognitivePipeline:
    def setup_method(self):
        self.pipe = CognitivePipeline()

    def test_full_run(self):
        result = self.pipe.run(ativo="ETH")
        assert result.state.config is not None
        assert result.chain_output is not None
        assert result.elapsed_ms > 0
        assert len(result.chain_output) == 6

    def test_percepcao(self):
        metrics = self.pipe.camada1_percepcao(
            market_cap=5e8,
            transaction_volume=5e6,
            realized_cap=4e8,
            returns_90d=[0.01, -0.02, 0.03, -0.01, 0.02],
        )
        assert metrics["nvt"] == 100.0
        assert metrics["mvrv"] == 1.25

    def test_normalizacao(self):
        signals = [MarketSignal(source="test", value=0.5, market_cap=1e9, transaction_volume=1e7, realized_cap=8e8)]
        normalized = self.pipe.camada2_normalizacao(signals)
        assert len(normalized) == 1
        assert 0 <= normalized[0].normalized_value <= 1

    def test_modelagem(self):
        sim = self.pipe.camada3_modelagem()
        assert "gbm_final" in sim
        assert "lotka_vivo_final" in sim
        assert "lotka_financeiro_final" in sim

    def test_semiose(self):
        capital = self.pipe.camada4_semiose(shannon_h=1.8, gini=0.25)
        assert len(capital.scores) == 8
        assert capital.rhi_estimated > 0

    def test_semiose_with_block(self):
        capital = self.pipe.camada4_semiose(shannon_h=0.5, gini=0.7)
        assert capital.bloqueio is not None

    def test_interpretacao(self):
        self.pipe.camada4_semiose()
        analysis = self.pipe.camada5_interpretacao("BTC")
        assert analysis.coherence >= 0
        assert analysis.noise >= 0

    def test_decisao(self):
        self.pipe.camada4_semiose()
        decision = self.pipe.camada6_decisao({"mvrv": 1.0, "sharpe_90d": 0.5})
        assert decision.acao in list(Action)
        assert -1 <= decision.tamanho_posicao <= 1

    def test_memoria(self):
        self.pipe.camada4_semiose()
        self.pipe.camada6_decisao({})
        log = self.pipe.camada7_memoria({"realidade": "lucro 3%", "level_up": False})
        assert log.previsao is not None

    def test_custom_config(self):
        from invest_os.models.schemas import InvestorConfig, RiskProfile
        config = InvestorConfig(risco=RiskProfile.CONSERVADOR, capital_disponivel_brl=1000)
        pipe = CognitivePipeline(config=config)
        result = pipe.run(ativo="SOL", capital_scores_kwargs={"shannon_h": 0.5})
        assert result.state.config.risco.value == "conservador"
        if result.state.decision:
            assert result.state.decision.gate_humano is True
