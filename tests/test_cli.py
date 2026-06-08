"""
E2E CLI tests: full command invocations via Click CliRunner.
Covers all 6 CLI commands with various options and output formats.
"""

from __future__ import annotations

import json
import os
import tempfile

import pytest
from click.testing import CliRunner

from invest_os.cli import main


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


class TestCLIAnalyze:
    """`invest-os analyze` command E2E."""

    def test_analyze_default(self, runner):
        result = runner.invoke(main, ["analyze"])
        assert result.exit_code == 0
        assert "InvestmentOS" in result.output
        assert "Métricas Financeiras" in result.output or "Grid KAIROS" in result.output

    def test_analyze_with_args(self, runner):
        result = runner.invoke(main, [
            "analyze", "--market-cap", "1e9", "--volume", "1e7",
            "--shannon-h", "1.5", "--gini", "0.3",
        ])
        assert result.exit_code == 0
        assert "NVT" in result.output or "RHI" in result.output

    def test_analyze_json_output(self, runner):
        result = runner.invoke(main, ["analyze", "--json-output"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "metrics" in data
        assert "capital_grid" in data
        assert "rhi" in data
        assert "nivel_arquetipo" in data

    def test_analyze_with_custom_prices(self, runner):
        result = runner.invoke(main, [
            "analyze", "--p1", "50", "--p2", "75", "--json-output",
        ])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "metrics" in data

    def test_analyze_with_returns(self, runner):
        result = runner.invoke(main, [
            "analyze", "--returns", "[0.05,0.03,-0.02]", "--json-output",
        ])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "metrics" in data
        assert "sharpe_90d" in data["metrics"]


class TestCLIPipeline:
    """`invest-os pipeline` command E2E."""

    def test_pipeline_default(self, runner):
        result = runner.invoke(main, ["pipeline"])
        assert result.exit_code == 0
        assert "Pipeline Cognitivo" in result.output
        assert "Camada 1" in result.output
        assert "Camada 4" in result.output

    def test_pipeline_with_profile(self, runner):
        result = runner.invoke(main, [
            "pipeline", "--ativo", "ETH", "--perfil", "sabio",
            "--risco", "arrojado", "--capital", "10000",
        ])
        assert result.exit_code == 0
        assert "SABIO" in result.output or "sabio" in result.output

    def test_pipeline_with_tese(self, runner):
        result = runner.invoke(main, [
            "pipeline", "--tese", "Agua potavel Africa",
        ])
        assert result.exit_code == 0
        assert "Agua potavel" in result.output

    def test_pipeline_json_output(self, runner):
        result = runner.invoke(main, ["pipeline", "--json-output"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "config" in data
        assert "decision" in data

    def test_pipeline_conservador_rejeita(self, runner):
        result = runner.invoke(main, [
            "pipeline", "--risco", "conservador",
            "--shannon-h", "0.3", "--gini", "0.7",
        ])
        assert result.exit_code == 0
        assert result.output is not None

    def test_pipeline_with_feedback(self, runner):
        fb = json.dumps({"realidade": "lucro 2%", "level_up": False})
        result = runner.invoke(main, [
            "pipeline", "--feedback", fb,
        ])
        assert result.exit_code == 0


class TestCLIPrompts:
    """`invest-os prompts` command E2E."""

    def test_prompts_default(self, runner):
        result = runner.invoke(main, ["prompts"])
        assert result.exit_code == 0
        assert "Nível 0" in result.output or "level0" in result.output

    def test_prompts_specific_level(self, runner):
        result = runner.invoke(main, ["prompts", "--nivel", "0"])
        assert result.exit_code == 0
        assert "Nível 0" in result.output

    def test_prompts_with_profile(self, runner):
        result = runner.invoke(main, ["prompts", "--perfil", "sabio", "--ativo", "BTC"])
        assert result.exit_code == 0
        assert "BTC" in result.output or "sabio" in result.output

    def test_prompts_to_file(self, runner, tmp_path):
        out = tmp_path / "chain.md"
        result = runner.invoke(main, ["prompts", "--output", str(out)])
        assert result.exit_code == 0
        assert out.exists()
        content = out.read_text()
        assert "Nível 0" in content


class TestCLIGovernance:
    """`invest-os governance` command E2E."""

    def test_governance_no_flags(self, runner):
        result = runner.invoke(main, ["governance"])
        assert result.exit_code == 0
        assert "Fronteiras Claras" in result.output or "Score" in result.output

    def test_governance_all_flags(self, runner):
        result = runner.invoke(main, [
            "governance", "--has-sbt", "--voting", "--oracles",
            "--slashing", "--dispute", "--legal",
        ])
        assert result.exit_code == 0

    def test_governance_json(self, runner):
        result = runner.invoke(main, ["governance", "--json-output"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "score" in data
        assert "principios_atendidos" in data
        assert "failed" in data

    def test_governance_perfect_score(self, runner):
        result = runner.invoke(main, [
            "governance", "--has-sbt", "--local-config", "--voting",
            "--oracles", "--slashing", "--dispute", "--legal", "--dao-of-daos",
        ])
        assert result.exit_code == 0


class TestCLISimulate:
    """`invest-os simulate` command E2E."""

    @pytest.mark.parametrize("tipo", ["gbm", "lotka", "bonding", "conviction"])
    def test_simulate_all_types(self, runner, tipo):
        result = runner.invoke(main, ["simulate", "--tipo", tipo])
        assert result.exit_code == 0

    def test_simulate_gbm_json(self, runner):
        result = runner.invoke(main, ["simulate", "--tipo", "gbm", "--json-output"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["type"] == "gbm"
        assert "path" in data

    def test_simulate_lotka_json(self, runner):
        result = runner.invoke(main, ["simulate", "--tipo", "lotka", "--json-output"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "vivo" in data
        assert "financeiro" in data

    def test_simulate_bonding_json(self, runner):
        result = runner.invoke(main, ["simulate", "--tipo", "bonding", "--json-output", "--steps", "50"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "prices" in data

    def test_simulate_conviction_json(self, runner):
        result = runner.invoke(main, ["simulate", "--tipo", "conviction", "--json-output"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "final" in data


class TestCLIErrorHandling:
    """Error cases and edge conditions."""

    def test_invalid_command(self, runner):
        result = runner.invoke(main, ["invalid-command"])
        assert result.exit_code != 0

    def test_invalid_profile(self, runner):
        result = runner.invoke(main, ["pipeline", "--perfil", "inexistente"])
        assert result.exit_code != 0

    def test_invalid_risk(self, runner):
        result = runner.invoke(main, ["pipeline", "--risco", "super-arrojado"])
        assert result.exit_code != 0

    def test_simulate_invalid_type(self, runner):
        result = runner.invoke(main, ["simulate", "--tipo", "black-scholes"])
        assert result.exit_code != 0
