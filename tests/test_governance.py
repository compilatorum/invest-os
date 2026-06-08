import pytest
from invest_os.governance.engine import OstromEngine, GoodhartShield


class TestOstromEngine:
    def setup_method(self):
        self.engine = OstromEngine()

    def test_all_passed(self):
        context = {
            "has_sbt": True,
            "local_config": True,
            "voting_enabled": True,
            "has_oracles": True,
            "has_slashing": True,
            "has_dispute_resolution": True,
            "has_legal_framework": True,
            "is_dao_of_daos": True,
        }
        results = self.engine.check_governance(context)
        assert all(results.values())
        score, failed = self.engine.evaluate_score(context)
        assert score == 1.0
        assert len(failed) == 0

    def test_all_failed(self):
        context = {k: False for k in ["has_sbt", "local_config", "voting_enabled", "has_oracles",
                                       "has_slashing", "has_dispute_resolution", "has_legal_framework",
                                       "is_dao_of_daos"]}
        score, failed = self.engine.evaluate_score(context)
        assert score == 0.0
        assert len(failed) == 8


class TestGoodhartShield:
    def setup_method(self):
        self.shield = GoodhartShield()

    def test_apply_noise(self):
        result = self.shield.apply("rhi", 0.65)
        assert result != 0.65
        assert 0.5 < result < 0.8

    def test_drift_no_history(self):
        assert not self.shield.drift_detected("test_metric")

    def test_drift_detection(self):
        for i in range(20):
            self.shield.add_observation("stable", 0.5)
        self.shield.add_observation("stable", 2.0)
        assert self.shield.drift_detected("stable")

    def test_adapt_weights(self):
        base = {"financeiro": 0.4, "vivo": 0.3, "social": 0.3}
        adapted = self.shield.adapt_weights("financeiro", base, 0.5)
        assert abs(sum(adapted.values()) - 1.0) < 0.01
        assert adapted["financeiro"] > base["financeiro"]
