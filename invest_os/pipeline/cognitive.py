from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from invest_os.models.schemas import (
    InvestorConfig, FinancialMetrics, CapitalGridResult, CapitalType,
    SemioticAnalysis, AlchemicalPhase, DecisionOutput, Action, RlhfLog,
    CognitiveMap, SystemState,
)
from invest_os.scores.descriptive import compute_descriptive
from invest_os.scores.interpretive import compute_interpretive
from invest_os.capitals.grid import CapitalGrid, interpret_rhi, suggest_action
from invest_os.signals.base import (
    Signal, MarketSignal, SocialSignal, CodeSignal, GovernanceSignal,
    normalize,
)
from invest_os.prompts.engine import PromptEngine
from invest_os.learning.rlhf import RLHFEngine
from invest_os.learning.drift import DriftDetector


@dataclass
class PipelineResult:
    state: SystemState
    chain_output: dict[str, str]
    elapsed_ms: float = 0.0


class CognitivePipeline:
    def __init__(self, config: Optional[InvestorConfig] = None):
        self.config = config or InvestorConfig()
        self.prompts = PromptEngine()
        self.capital_grid = CapitalGrid()
        self.rlhf = RLHFEngine()
        self.drift = DriftDetector()
        self.state = SystemState(config=self.config)

    def camada1_percepcao(
        self,
        market_cap: float = 0,
        transaction_volume: float = 1,
        realized_cap: float = 1,
        returns_90d: Optional[list[float]] = None,
        volume_24h: float = 0,
        fee_tier: float = 0.003,
        liquidity: float = 1,
        portfolio_weights: Optional[list[float]] = None,
        volatility_24h: float = 0,
        exposure_pct: float = 0,
        p1: float = 1.0,
        p2: float = 1.0,
    ) -> dict:
        descriptive = compute_descriptive(
            market_cap=market_cap,
            transaction_volume=transaction_volume,
            realized_cap=realized_cap,
            returns_90d=returns_90d,
            p1=p1, p2=p2,
            volume_24h=volume_24h,
            fee_tier=fee_tier,
            liquidity=liquidity,
            volatility_24h=volatility_24h,
            exposure_pct=exposure_pct,
        )
        interpretive = compute_interpretive(portfolio_weights=portfolio_weights)
        descriptive.update(interpretive)

        alertas = []
        nvt = descriptive.get("nvt")
        if nvt and nvt > 150:
            alertas.append("NVT elevado — possível supervalorização")
        mvrv = descriptive.get("mvrv")
        if mvrv and mvrv < 1.0:
            alertas.append("MVRV < 1.0 — oportunidade de acumulação")
        elif mvrv and mvrv > 3.5:
            alertas.append("MVRV > 3.5 — perigo de sobrevalorização")
        sopr_ = descriptive.get("sopr")
        if sopr_ and sopr_ < 1.0:
            alertas.append("SOPR < 1.0 — capitulação de holders")
        hhi = descriptive.get("hhi")
        if hhi and hhi > 0.25:
            alertas.append("HHI > 0.25 — concentração excessiva no portfolio")
        descriptive["alertas"] = alertas

        self.state.metrics = FinancialMetrics(**{k: v for k, v in descriptive.items() if k != "alertas"})
        return descriptive

    def camada2_normalizacao(self, signals: Optional[list[Signal]] = None) -> list:
        if signals is None:
            signals = [
                MarketSignal(
                    source="on-chain",
                    value=0.5,
                    market_cap=self.state.metrics.nvt or 1e9,
                    transaction_volume=self.state.metrics.sopr or 1e7,
                    realized_cap=self.state.metrics.mvrv or 8e8,
                ),
            ]
        return [normalize(s) for s in signals]

    def camada3_modelagem(self) -> dict:
        from invest_os.utils.math_tools import geometric_brownian_motion, lotka_volterra
        gbm_path = geometric_brownian_motion(100, 0.05, 0.2, 0.01, 50)
        v, f = lotka_volterra(0.5, 0.01, 0.01, 0.3, 40, 10, 0.01, 50)
        return {
            "gbm_final": round(gbm_path[-1], 4) if gbm_path else 100.0,
            "lotka_vivo_final": round(v[-1], 4) if v else 40.0,
            "lotka_financeiro_final": round(f[-1], 4) if f else 10.0,
        }

    def camada4_semiose(
        self,
        shannon_h: float = 0.0,
        gini: float = 0.0,
        custom_scores: Optional[dict[CapitalType, float]] = None,
        evidence: Optional[dict[CapitalType, list[str]]] = None,
    ) -> CapitalGridResult:
        if custom_scores is None:
            custom_scores = {}
        if evidence is None:
            evidence = {}

        grid_scores = {
            CapitalType.FINANCEIRO: custom_scores.get(CapitalType.FINANCEIRO, 0.5),
            CapitalType.VIVO: custom_scores.get(CapitalType.VIVO, 0.3),
            CapitalType.MATERIAL: custom_scores.get(CapitalType.MATERIAL, 0.5),
            CapitalType.SOCIAL: custom_scores.get(CapitalType.SOCIAL, 0.5),
            CapitalType.INTELECTUAL: custom_scores.get(CapitalType.INTELECTUAL, 0.5),
            CapitalType.EXPERIENCIAL: custom_scores.get(CapitalType.EXPERIENCIAL, 0.4),
            CapitalType.CULTURAL: custom_scores.get(CapitalType.CULTURAL, 0.4),
            CapitalType.ESPIRITUAL: custom_scores.get(CapitalType.ESPIRITUAL, 0.3),
            **custom_scores,
        }

        result = self.capital_grid.evaluate(
            scores=grid_scores,
            shannon_h=shannon_h,
            gini=gini,
            evidence=evidence,
        )
        self.state.capital_grid = result
        return result

    def camada5_interpretacao(self, ativo: str) -> SemioticAnalysis:
        analysis = SemioticAnalysis(
            sign=f"Sinais de mercado de {ativo}",
            object="Fundamentos on-chain e off-chain",
            interpretant=["Análise técnica indica momentum", "Métricas on-chain mostram acumulação"],
            coherence=0.65,
            noise=0.35,
            phase=AlchemicalPhase.ALBEDO,
        )
        if self.state.capital_grid and self.state.capital_grid.bloqueio:
            analysis.noise = 0.8
            analysis.coherence = 0.2
        self.state.semiotic = analysis
        return analysis

    def camada6_decisao(self, metrics: dict) -> DecisionOutput:
        grid = self.state.capital_grid
        if not grid:
            grid = self.camada4_semiose()

        acao = suggest_action(grid, metrics)
        score = grid.rhi_estimated
        if metrics.get("sharpe_90d") and metrics["sharpe_90d"] > 1.0:
            score = min(score + 0.1, 1.0)
        if metrics.get("mvrv") and metrics["mvrv"] < 1.0:
            score = min(score + 0.1, 1.0)

        tamanho = 0.0
        if acao == Action.COMPRAR:
            tamanho = min(score * 0.3, 0.25)
        elif acao == Action.AGUARDAR:
            tamanho = 0.05
        elif acao == Action.REBALANCEAR:
            tamanho = -0.1

        gate = grid.bloqueio is not None or score < 0.3

        decision = DecisionOutput(
            acao=acao,
            tamanho_posicao=round(tamanho, 4),
            score_composto=round(score, 4),
            narrativa=f"Score composto {score:.1%}. Ação: {acao.value}. Posição: {tamanho:.1%}.",
            metadata_nft={
                "name": "Position NFT",
                "score": score,
                "acao": acao.value,
                "timestamp": datetime.now().isoformat(),
            },
            gate_humano=gate,
        )
        self.state.decision = decision
        return decision

    def camada7_memoria(self, feedback: Optional[dict] = None) -> RlhfLog:
        log = RlhfLog(
            previsao=str(self.state.decision.acao.value if self.state.decision else "N/A"),
            realidade=feedback.get("realidade", "pendente") if feedback else "pendente",
            delta_capital=feedback.get("delta_capital", {}) if feedback else {},
            prompt_melhoria=feedback.get("melhoria", "") if feedback else "",
            rhi_real=feedback.get("rhi_real") if feedback else None,
            rhi_estimado=self.state.capital_grid.rhi_estimated if self.state.capital_grid else None,
            level_up=feedback.get("level_up", False) if feedback else False,
        )
        self.state.history.append(log)
        self.rlhf.register(log)
        if feedback:
            self.drift.observe("rhi", log.rhi_estimado or 0.0)
        return log

    def run(self, ativo: str = "BTC",
            metrics_input: Optional[dict] = None,
            capital_scores: Optional[dict[CapitalType, float]] = None,
            capital_scores_kwargs: Optional[dict] = None,
            feedback: Optional[dict] = None,
            signals: Optional[list[Signal]] = None) -> PipelineResult:
        import time
        start = time.time()

        m = metrics_input or {}
        metrics = self.camada1_percepcao(**m)

        normalized = self.camada2_normalizacao(signals)

        simulation = self.camada3_modelagem()

        csk = capital_scores_kwargs or {}
        shannon_h = csk.get("shannon_h", metrics.get("entropy", 1.5))
        gini = csk.get("gini", metrics.get("gini", 0.0))
        capital = self.camada4_semiose(
            shannon_h=shannon_h,
            gini=gini,
            custom_scores=capital_scores,
        )

        semiotic = self.camada5_interpretacao(ativo)

        decision = self.camada6_decisao(metrics)

        log = self.camada7_memoria(feedback)

        chain = self.prompts.run_full_chain(
            ativo=ativo,
            config=self.config,
            metrics=metrics,
            capital=capital,
            decision=decision,
            log=log,
        )

        elapsed = (time.time() - start) * 1000
        return PipelineResult(
            state=self.state,
            chain_output=chain,
            elapsed_ms=round(elapsed, 2),
        )
