from __future__ import annotations

import pytest
import math
from invest_os.core.metrics import (
    nvt_ratio, mvrv_ratio, sopr, sharpe_ratio, il_break_even,
    fee_apy, herfindahl_hirschman_index, financial_temperature,
    shannon_entropy, gini_coefficient, pbo_probability,
    calculate_all_metrics,
)


class TestNVTRatio:
    def test_basic(self):
        assert nvt_ratio(1e9, 1e7) == 100.0

    def test_zero_volume(self):
        assert nvt_ratio(1e9, 0) == float("inf")

    def test_zero_cap(self):
        assert nvt_ratio(0, 1e7) == 0.0


class TestMVRVRatio:
    def test_basic(self):
        assert mvrv_ratio(1e9, 8e8) == 1.25

    def test_below_one(self):
        assert mvrv_ratio(5e8, 1e9) == 0.5

    def test_zero_realized(self):
        assert mvrv_ratio(1e9, 0) is None


class TestSOPR:
    def test_profit(self):
        assert sopr(120, 100) == 1.2

    def test_loss(self):
        assert sopr(80, 100) == 0.8

    def test_zero_bought(self):
        assert sopr(100, 0) is None


class TestSharpeRatio:
    def test_positive(self):
        r = sharpe_ratio([0.01, 0.02, 0.015, 0.005, 0.01])
        assert r is not None
        assert r > 0

    def test_negative(self):
        r = sharpe_ratio([-0.01, -0.02, -0.015])
        assert r is not None
        assert r < 0

    def test_insufficient_data(self):
        assert sharpe_ratio([0.01]) is None

    def test_risk_free(self):
        r = sharpe_ratio([0.02, 0.025, 0.03], risk_free=0.015)
        assert r is not None


class TestILBreakEven:
    def test_equal_prices(self):
        assert il_break_even(100, 100) == 0.0

    def test_double_price(self):
        result = il_break_even(100, 200)
        assert abs(result - (-0.057)) < 0.01

    def test_half_price(self):
        result = il_break_even(200, 100)
        assert abs(result - (-0.057)) < 0.01


class TestHHI:
    def test_concentrated(self):
        assert herfindahl_hirschman_index([100, 0, 0]) == 1.0

    def test_diversified(self):
        hhi = herfindahl_hirschman_index([25, 25, 25, 25])
        assert abs(hhi - 0.25) < 0.01

    def test_empty(self):
        assert herfindahl_hirschman_index([]) == 0.0


class TestShannonEntropy:
    def test_equal_weights(self):
        h = shannon_entropy([1, 1, 1, 1])
        assert abs(h - 2.0) < 0.01

    def test_concentrated(self):
        h = shannon_entropy([1, 0, 0])
        assert abs(h - 0.0) < 0.001

    def test_empty(self):
        assert shannon_entropy([]) == 0.0


class TestGiniCoefficient:
    def test_perfect_equality(self):
        assert abs(gini_coefficient([10, 10, 10]) - 0.0) < 0.01

    def test_perfect_inequality(self):
        assert gini_coefficient([0, 0, 100]) > 0.5

    def test_empty(self):
        assert gini_coefficient([]) == 0.0


class TestFinancialTemperature:
    def test_basic(self):
        assert abs(financial_temperature(0.05, 0.2) - 0.01) < 1e-10


class TestCalculateAllMetrics:
    def test_full_run(self):
        metrics = calculate_all_metrics(
            market_cap=1e9,
            transaction_volume=1e7,
            realized_cap=8e8,
            returns_90d=[0.01, 0.02, -0.01, 0.015, 0.005],
            p1=100, p2=120,
            volume_24h=1e7,
            fee_tier=0.003,
            liquidity=1e8,
            portfolio_weights=[40, 30, 20, 10],
            volatility_24h=0.05,
            exposure_pct=0.2,
        )
        assert "nvt" in metrics
        assert "mvrv" in metrics
        assert "sharpe_90d" in metrics
        assert "alertas" in metrics
        assert isinstance(metrics["alertas"], list)
