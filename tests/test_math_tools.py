import pytest
from invest_os.utils.math_tools import (
    geometric_brownian_motion, lotka_volterra, cosine_similarity,
    js_divergence, price_from_bonding_curve, conviction_vote,
    antifragility_score, rwi, choquet_expected_value,
)


class TestChoquetExpectedValue:
    def test_basic(self):
        result = choquet_expected_value(80, 100, 0.3)
        assert result == 0.3 * 80 + 0.7 * 100


class TestGBM:
    def test_length(self):
        path = geometric_brownian_motion(100, 0.05, 0.2, 0.01, 100)
        assert len(path) == 101
        assert path[0] == 100

    def test_positive(self):
        path = geometric_brownian_motion(100, 0.1, 0.1, 0.01, 50)
        assert all(p > 0 for p in path)


class TestLotkaVolterra:
    def test_length(self):
        v, f = lotka_volterra(0.5, 0.01, 0.01, 0.3, 40, 10, 0.01, 100)
        assert len(v) == 101
        assert len(f) == 101

    def test_non_negative(self):
        v, f = lotka_volterra(0.1, 0.1, 0.1, 0.1, 10, 10, 0.1, 50)
        assert all(x >= 0 for x in v)
        assert all(x >= 0 for x in f)


class TestCosineSimilarity:
    def test_identical(self):
        assert abs(cosine_similarity([1, 2, 3], [1, 2, 3]) - 1.0) < 0.001

    def test_orthogonal(self):
        assert abs(cosine_similarity([1, 0], [0, 1])) < 0.001

    def test_zero_vector(self):
        assert cosine_similarity([0, 0], [1, 1]) == 0.0


class TestBondingCurve:
    def test_basic(self):
        price = price_from_bonding_curve(1000, 50000, 0.5)
        assert price == 50000 / (1000 * 0.5)

    def test_zero_supply(self):
        assert price_from_bonding_curve(0, 50000, 0.5) == 0.0


class TestConvictionVote:
    def test_accumulate(self):
        conv = 0
        conv = conviction_vote(conv, 0.9, 10)
        conv = conviction_vote(conv, 0.9, 10)
        conv = conviction_vote(conv, 0.9, 10)
        expected = 10 * (0.9 ** 2) + 10 * 0.9 + 10
        assert abs(conv - expected) < 0.01


class TestAntifragility:
    def test_positive(self):
        assert antifragility_score(5, 10) == 0.5

    def test_infinite(self):
        assert antifragility_score(5, 0) == float("inf")


class TestRWI:
    def test_basic(self):
        result = rwi(100, 50, 1000)
        assert result == 0.15

    def test_zero_capital(self):
        assert rwi(100, 50, 0) is None
