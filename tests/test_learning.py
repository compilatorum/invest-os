import pytest
from invest_os.learning.rlhf import RLHFEngine
from invest_os.learning.drift import DriftDetector
from invest_os.models.schemas import RlhfLog


class TestRLHF:
    def test_engine_empty(self):
        engine = RLHFEngine()
        assert engine.accuracy() == 0.0

    def test_engine_register(self):
        engine = RLHFEngine()
        log = RlhfLog(previsao="comprar", realidade="lucro 5%", level_up=True)
        engine.register(log)
        assert engine.accuracy() == 1.0

    def test_engine_multiple(self):
        engine = RLHFEngine()
        engine.register(RlhfLog(previsao="a", level_up=True))
        engine.register(RlhfLog(previsao="b", level_up=False))
        assert engine.accuracy() == 0.5

    def test_last_n(self):
        engine = RLHFEngine()
        for i in range(10):
            engine.register(RlhfLog(previsao=str(i)))
        assert len(engine.last_n(3)) == 3

    def test_improvement_suggestions(self):
        engine = RLHFEngine()
        engine.register(RlhfLog(prompt_melhoria="Ajustar sharpe"))
        engine.register(RlhfLog(prompt_melhoria=""))
        suggestions = engine.improvement_suggestions()
        assert len(suggestions) == 1


class TestDriftDetector:
    def test_empty(self):
        d = DriftDetector()
        assert d.is_drifting("test") is False

    def test_not_enough_samples(self):
        d = DriftDetector(min_samples=5)
        for i in range(3):
            d.observe("test", 1.0)
        assert d.is_drifting("test") is False

    def test_drift_detected(self):
        d = DriftDetector(min_samples=10)
        for _ in range(15):
            d.observe("test", 0.5)
        d.observe("test", 10.0)
        assert d.is_drifting("test") is True

    def test_no_drift(self):
        d = DriftDetector(min_samples=5)
        for _ in range(10):
            d.observe("test", 0.5)
        assert d.is_drifting("test") is False

    def test_drift_score(self):
        d = DriftDetector(min_samples=5)
        for _ in range(10):
            d.observe("test", 0.5)
        d.observe("test", 10.0)
        assert d.drift_score("test") > 0

    def test_drift_score_insufficient(self):
        d = DriftDetector(min_samples=5)
        d.observe("test", 0.5)
        assert d.drift_score("test") == 0.0

    def test_drift_score_zero_var(self):
        d = DriftDetector(min_samples=5)
        for _ in range(10):
            d.observe("test", 1.0)
        assert d.drift_score("test") == 0.0

    def test_history_truncation(self):
        d = DriftDetector(min_samples=3)
        for i in range(250):
            d.observe("test", float(i))
        assert len(d._history["test"]) == 200
