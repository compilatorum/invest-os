"""
Smoke tests: quick sanity checks — imports, CLI responses, basic integrity.
"""

from __future__ import annotations

import importlib
import sys

import pytest
from click.testing import CliRunner


class TestImportSmoke:
    """Verify every module imports cleanly."""

    MODULES = [
        "invest_os",
        "invest_os.models",
        "invest_os.models.schemas",
        "invest_os.core",
        "invest_os.core.metrics",
        "invest_os.core.capital_grid",
        "invest_os.entities",
        "invest_os.entities.base",
        "invest_os.capitals",
        "invest_os.capitals.grid",
        "invest_os.capitals.dimensions",
        "invest_os.signals",
        "invest_os.signals.base",
        "invest_os.scores",
        "invest_os.scores.descriptive",
        "invest_os.scores.interpretive",
        "invest_os.scores.axiological",
        "invest_os.scores.decisional",
        "invest_os.learning",
        "invest_os.learning.rlhf",
        "invest_os.learning.drift",
        "invest_os.prompts",
        "invest_os.prompts.engine",
        "invest_os.prompts.router",
        "invest_os.pipeline",
        "invest_os.pipeline.cognitive",
        "invest_os.governance",
        "invest_os.governance.engine",
        "invest_os.utils",
        "invest_os.utils.math_tools",
    ]

    @pytest.mark.parametrize("modname", MODULES)
    def test_module_imports(self, modname):
        mod = importlib.import_module(modname)
        assert mod is not None


class TestCLISmoke:
    """Quick CLI invocation smoke tests."""

    def test_cli_help(self):
        from invest_os.cli import main
        runner = CliRunner()
        result = runner.invoke(main, ["--help"])
        assert result.exit_code == 0
        assert "InvestmentOS" in result.output

    def test_cli_version(self):
        from invest_os.cli import main
        runner = CliRunner()
        result = runner.invoke(main, ["version"])
        assert result.exit_code == 0
        assert "InvestmentOS" in result.output or "Capital OS" in result.output

    def test_cli_analyze_help(self):
        from invest_os.cli import main
        runner = CliRunner()
        result = runner.invoke(main, ["analyze", "--help"])
        assert result.exit_code == 0

    def test_cli_pipeline_help(self):
        from invest_os.cli import main
        runner = CliRunner()
        result = runner.invoke(main, ["pipeline", "--help"])
        assert result.exit_code == 0

    def test_cli_prompts_help(self):
        from invest_os.cli import main
        runner = CliRunner()
        result = runner.invoke(main, ["prompts", "--help"])
        assert result.exit_code == 0

    def test_cli_governance_help(self):
        from invest_os.cli import main
        runner = CliRunner()
        result = runner.invoke(main, ["governance", "--help"])
        assert result.exit_code == 0

    def test_cli_simulate_help(self):
        from invest_os.cli import main
        runner = CliRunner()
        result = runner.invoke(main, ["simulate", "--help"])
        assert result.exit_code == 0


class TestDataModelSmoke:
    """Smoke tests for data model integrity."""

    def test_all_enums_have_values(self):
        from invest_os.models.schemas import (
            InvestorProfile, RiskProfile, Action, CapitalType, AlchemicalPhase,
        )
        for e in [InvestorProfile, RiskProfile, Action, CapitalType, AlchemicalPhase]:
            assert len(e) > 0, f"{e.__name__} has no members"

    def test_default_system_state(self):
        from invest_os.models.schemas import SystemState
        state = SystemState()
        assert state.config.nome == "investidor"
        assert state.history == []


class TestFixtureSmoke:
    """Verify test fixtures load correctly."""

    def test_factories(self):
        from tests.fixtures import (
            make_config, make_metrics, make_capital_scores,
            make_capital_grid, make_decision, make_rlhf,
        )
        assert make_config().nome == "testador"
        assert make_metrics().nvt == 100.0
        assert len(make_capital_scores()) == 8
        assert make_capital_grid().rhi_estimated == 0.65
        assert make_decision().acao.value == "aguardar"

    def test_scenarios(self):
        from tests.fixtures import Scenarios
        bull = Scenarios.bull_market()
        bear = Scenarios.bear_market()
        stable = Scenarios.stable_market()
        assert bull["market_cap"] > bear["market_cap"]
        assert bear["volatility_24h"] > stable["volatility_24h"]
