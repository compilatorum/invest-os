from __future__ import annotations

from enum import Enum
from typing import Optional, Callable
from dataclasses import dataclass, field


class OstromPrinciple(Enum):
    FRONTEIRAS_CLARAS = "Fronteiras Claras"
    CONGRUENCIA_LOCAL = "Congruência Local"
    ESCOLHA_COLETIVA = "Escolha Coletiva"
    MONITORAMENTO = "Monitoramento"
    SANCOES_GRADUADAS = "Sanções Graduadas"
    RESOLUCAO_CONFLITOS = "Resolução de Conflitos"
    RECONHECIMENTO_EXTERNO = "Reconhecimento Externo"
    EMPRESAS_ANINHADAS = "Empresas Aninhadas"


@dataclass
class OstromRule:
    principle: OstromPrinciple
    enabled: bool = True
    params: dict = field(default_factory=dict)


class OstromEngine:
    def __init__(self):
        self.rules: list[OstromRule] = [
            OstromRule(OstromPrinciple.FRONTEIRAS_CLARAS, params={"token_gating": True}),
            OstromRule(OstromPrinciple.CONGRUENCIA_LOCAL, params={"sub_daos": True}),
            OstromRule(OstromPrinciple.ESCOLHA_COLETIVA, params={"quadratic_voting": True}),
            OstromRule(OstromPrinciple.MONITORAMENTO, params={"hybrid_oracles": True}),
            OstromRule(OstromPrinciple.SANCOES_GRADUADAS, params={"progressive_slashing": True}),
            OstromRule(OstromPrinciple.RESOLUCAO_CONFLITOS, params={"kleros_integration": True}),
            OstromRule(OstromPrinciple.RECONHECIMENTO_EXTERNO, params={"legal_wrappers": True}),
            OstromRule(OstromPrinciple.EMPRESAS_ANINHADAS, params={"dao_of_daos": True}),
        ]

    def check_governance(self, context: dict) -> dict[str, bool]:
        results = {}
        for rule in self.rules:
            if not rule.enabled:
                results[rule.principle.value] = False
                continue

            passed = True
            p = rule.principle

            if p == OstromPrinciple.FRONTEIRAS_CLARAS:
                passed = context.get("has_sbt", False) or context.get("token_gated", False)
            elif p == OstromPrinciple.CONGRUENCIA_LOCAL:
                passed = context.get("local_config", False)
            elif p == OstromPrinciple.ESCOLHA_COLETIVA:
                passed = context.get("voting_enabled", False)
            elif p == OstromPrinciple.MONITORAMENTO:
                passed = context.get("has_oracles", False)
            elif p == OstromPrinciple.SANCOES_GRADUADAS:
                passed = context.get("has_slashing", False)
            elif p == OstromPrinciple.RESOLUCAO_CONFLITOS:
                passed = context.get("has_dispute_resolution", False)
            elif p == OstromPrinciple.RECONHECIMENTO_EXTERNO:
                passed = context.get("has_legal_framework", False)
            elif p == OstromPrinciple.EMPRESAS_ANINHADAS:
                passed = context.get("is_dao_of_daos", False)

            results[rule.principle.value] = passed

        return results

    def evaluate_score(self, context: dict) -> tuple[float, list[str]]:
        results = self.check_governance(context)
        passed = [k for k, v in results.items() if v]
        failed = [k for k, v in results.items() if not v]
        score = len(passed) / len(self.rules) if self.rules else 0.0
        return score, failed


class GoodhartShield:
    def __init__(self, noise_std: float = 0.05, adaptation_rate: float = 0.1):
        self.noise_std = noise_std
        self.adaptation_rate = adaptation_rate
        self._metric_history: dict[str, list[float]] = {}

    def apply(self, metric_name: str, value: float, weights: Optional[dict] = None) -> float:
        import random
        if weights is None:
            weights = {}
        w = weights.get(metric_name, 1.0)
        noise = random.gauss(0, self.noise_std * w)
        return value + noise

    def add_observation(self, metric_name: str, value: float):
        if metric_name not in self._metric_history:
            self._metric_history[metric_name] = []
        self._metric_history[metric_name].append(value)
        if len(self._metric_history[metric_name]) > 100:
            self._metric_history[metric_name] = self._metric_history[metric_name][-100:]

    def drift_detected(self, metric_name: str, z_threshold: float = 2.0) -> bool:
        vals = self._metric_history.get(metric_name, [])
        if len(vals) < 10:
            return False
        mean = sum(vals) / len(vals)
        var = sum((v - mean) ** 2 for v in vals) / (len(vals) - 1)
        if var <= 0:
            return False
        std = var ** 0.5
        latest = vals[-1]
        return abs(latest - mean) / std > z_threshold

    def adapt_weights(self, metric_name: str, base_weights: dict, signal: float) -> dict:
        weights = base_weights.copy()
        if metric_name in weights:
            weights[metric_name] *= (1 + self.adaptation_rate * signal)
            weights[metric_name] = max(0.01, min(weights[metric_name], 1.0))
        total = sum(weights.values())
        if total > 0:
            for k in weights:
                weights[k] /= total
        return weights
