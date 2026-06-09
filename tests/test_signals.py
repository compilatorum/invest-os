import pytest
from invest_os.signals.base import (
    Signal, SignalType, NormalizedSignal,
    MarketSignal, SocialSignal, CodeSignal, GovernanceSignal,
    normalize, normalize_market, normalize_social, normalize_code, normalize_governance,
)


class TestSignals:
    def test_market_signal_type(self):
        s = MarketSignal(source="chain", value=0.5, market_cap=1e9, transaction_volume=1e7, realized_cap=8e8)
        assert s.type == SignalType.MARKET

    def test_social_signal(self):
        s = SocialSignal(source="discord", value=0.3, community_size=5000, governance_participation=0.2)
        assert s.type == SignalType.SOCIAL

    def test_code_signal(self):
        s = CodeSignal(source="github", value=0.7, github_stars=1000, github_forks=200, contributors=50)
        assert s.type == SignalType.CODE

    def test_governance_signal(self):
        s = GovernanceSignal(source="dao", value=0.9, has_sbt=True, voting_enabled=True)
        assert s.type == SignalType.GOVERNANCE

    def test_normalize_market(self):
        s = MarketSignal(source="chain", value=0.5, market_cap=1e9, transaction_volume=1e7, realized_cap=8e8)
        n = normalize_market(s)
        assert 0 <= n.normalized_value <= 1

    def test_normalize_social(self):
        s = SocialSignal(source="discord", value=0.3, community_size=50000, governance_participation=0.5)
        n = normalize_social(s)
        assert 0 <= n.normalized_value <= 1

    def test_normalize_code(self):
        s = CodeSignal(source="github", value=0.7, github_stars=2000, github_forks=500, contributors=80)
        n = normalize_code(s)
        assert 0 <= n.normalized_value <= 1

    def test_normalize_governance(self):
        s = GovernanceSignal(source="dao", value=0.9, has_sbt=True, voting_enabled=True, has_oracles=True)
        n = normalize_governance(s)
        assert n.normalized_value == 1.0

    def test_normalize_dispatch(self):
        s = MarketSignal(source="chain", value=0.5, market_cap=1e9, transaction_volume=1e7, realized_cap=8e8)
        n = normalize(s)
        assert 0 <= n.normalized_value <= 1

    def test_normalize_unknown_type(self):
        s = Signal(type=SignalType.MARKET, source="test", value=0.5)
        n = normalize(s)
        assert n.normalized_value == 0.5
