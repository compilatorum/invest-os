from __future__ import annotations

import json
from typing import Any
from invest_os.models.schemas import (
    InvestorConfig, CognitiveMap, FinancialMetrics, CapitalGridResult,
    SemioticAnalysis, AlchemicalPhase, DecisionOutput, Action, RlhfLog,
)


PROMPT_REPO = {}


def load_prompt_repo(path: str = "prompts/repository") -> dict:
    import os
    repo = {}
    base = os.path.join(os.path.dirname(__file__), "..", "..", path)
    for fname in os.listdir(base):
        if fname.endswith(".md"):
            key = fname.replace(".md", "")
            with open(os.path.join(base, fname)) as f:
                repo[key] = f.read()
    return repo


def render_prompt(template: str, **kwargs) -> str:
    for k, v in kwargs.items():
        placeholder = "{" + k.upper() + "}"
        template = template.replace(placeholder, str(v))
    return template


class PromptEngine:
    def __init__(self, repo_path: str = None):
        self.history: list[dict] = []

    def level0_context(self, config: InvestorConfig, ativo: str) -> str:
        return f"""# Nível 0 — Contexto & Perfil

## SYSTEM
Você é o Web3 Investment OS no modo Curador Arquitetonico.

## INPUT
- Ativo/Protocolo: {ativo}
- Tese de Impacto: {config.tese_impacto}
- Perfil do Investidor: {config.perfil.value}
- Capital disponível: R$ {config.capital_disponivel_brl:,.2f}
- Modo de Linguagem: {config.modo_linguagem}

## TASK
Gere um mapa cognitivo inicial do ativo em 3 camadas:
1. **Camada Técnica**: whitepaper, tokenomics, arquitetura
2. **Camada Semiótica**: qual narrativa o projeto vende?
3. **Camada Ontológica**: que problema de verdade resolve?

## OUTPUT
```json
{{ "tecnica": {{}}, "semiotica": {{}}, "ontologica": {{}}, "flags_iniciais": [] }}
```"""

    def level1_financial_dd(self, mapa: CognitiveMap, metrics: dict) -> str:
        def fmt(v, dec=2):
            if v is None or v == "N/A":
                return "N/A"
            return f"{v:.{dec}f}"

        return f"""# Nível 1 — Due Diligence Financeira

## INPUT
Mapa cognitivo recebido.

## TASK
Calcule e interprete com base nos dados fornecidos:

| Métrica | Valor | Alerta |
|---------|-------|--------|
| NVT | {fmt(metrics.get('nvt'))} | {'⚠️' if isinstance(metrics.get('nvt'), (int, float)) and metrics['nvt'] > 150 else '✅'} |
| MVRV | {fmt(metrics.get('mvrv'))} | {'🟢 < 1.0' if isinstance(metrics.get('mvrv'), (int, float)) and metrics['mvrv'] < 1.0 else '🔴 > 3.5' if isinstance(metrics.get('mvrv'), (int, float)) and metrics['mvrv'] > 3.5 else '🟡'} |
| SOPR | {fmt(metrics.get('sopr'))} | {'🔴 < 1.0 (capitulação)' if isinstance(metrics.get('sopr'), (int, float)) and metrics['sopr'] < 1.0 else '✅'} |
| Sharpe 90d | {fmt(metrics.get('sharpe_90d'))} | - |
| IL Break-even | {fmt(metrics.get('il_break_even'))} | - |
| Temperatura | {fmt(metrics.get('temperature'))} | - |
| HHI | {fmt(metrics.get('hhi'))} | {'⚠️ > 0.25' if isinstance(metrics.get('hhi'), (int, float)) and metrics['hhi'] > 0.25 else '✅'} |
| Entropia | {fmt(metrics.get('entropy'))} | - |

## OUTPUT
```json
{{ "metricas": {{}}, "score_financeiro": 0.0, "alertas": [], "recomendacao": "" }}
```"""

    def level2_regenerative_dd(self, capital_grid: CapitalGridResult) -> str:
        scores_md = "\n".join(
            f"| {s.type.value} | {s.score:.2f} | {'🟢' if s.score > 0.5 else '🟡' if s.score > 0.3 else '🔴'} |"
            for s in capital_grid.scores
        )
        bloqueio_md = f"🚫 {capital_grid.bloqueio}" if capital_grid.bloqueio else "✅ Nenhum bloqueio"
        return f"""# Nível 2 — Due Diligence Regenerativa (KAIROS)

## INPUT
Resultado da análise financeira.

## TASK
Avalie o ativo sob as 8 Formas de Capital:

| Capital | Score | Status |
|---------|-------|--------|
{scores_md}

**RHI Estimado:** {capital_grid.rhi_estimated:.2%}
**Nível Arquetípico:** {self._rhi_level(capital_grid.rhi_estimated)}
**Bloqueio:** {bloqueio_md}

## BLOQUEIOS
- Shannon H' < 1.2 → 🚫 RECUSAR
- Gini > 0.5 → 🚫 ALERTA CRÍTICO

## OUTPUT
```json
{{ "capitais_8d": [], "rhi_estimado": {capital_grid.rhi_estimated:.4f}, "nivel_arquetipo": "{self._rhi_level(capital_grid.rhi_estimated)}", "recomendacao": "" }}
```"""

    def level3_semiotic(self, ativo: str, metrics: dict) -> str:
        return f"""# Nível 3 — Análise Semiótica (Peirce)

## INPUT
Análise financeira e regenerativa concluída.

## TASK
Analise a tríade Peirceana de {ativo} no momento atual:

1. **Signo**: que sinal/preço/narrativa domina?
2. **Objeto**: o que os fundamentos realmente indicam?
3. **Interpretante**: que interpretações concorrentes existem?
4. **Coerência Semiótica**: Correl(Signo, Objeto) — 0 a 1
5. **Ruído Semiótico**: 1 - Coerência
6. **Fase Alquímica**: Nigredo / Albedo / Rubedo

## ALERTA
Ruído > 0.6 → especulação dominante → recomendar aguardar

## OUTPUT
```json
{{ "coerencia": 0.5, "ruido": 0.5, "fase_alquimica": "nigredo", "interpretacoes": [], "acao_recomendada": "" }}
```"""

    def level4_axiological(self, decision: DecisionOutput, config: InvestorConfig) -> str:
        return f"""# Nível 4 — Decisão Axiológica & Gate Humano

## INPUT
Análise completa dos níveis 0-3.

## TASK
Sintetize recomendação final:

- **Score composto**: 40% financeiro + 35% regenerativo + 25% semiótico
- **Alinhamento com perfil**: {config.perfil.value} — 0 a 100%
- **Ação recomendada**: {decision.acao.value}
- **Tamanho de posição**: {decision.tamanho_posicao:.1%} do portfolio
- **Gate**: {'⚠️ Gate humano obrigatório' if decision.gate_humano else '✅ Execução automática'}

## OUTPUT
```json
{{ "acao": "{decision.acao.value}", "tamanho_posicao": {decision.tamanho_posicao:.2f}, "score_composto": {decision.score_composto:.2f}, "narrativa": "", "metadata_nft": {{}} }}
```"""

    def level5_rlhf(self, log: RlhfLog) -> str:
        return f"""# Nível 5 — Reflexão & Aprendizado (RLHF)

## INPUT
Resultado da ação + feedback humano pós-decisão.

## TASK
Registre em decisions.org:

- O que o sistema previu vs. o que aconteceu?
- Que capital multidimensional se transformou?
- O prompt de qual nível errou mais? Por quê?
- Sugestão de melhoria para o prompt-repo
- RHI score real vs. RHI estimado
- Nível do investidor atualizado?

## OUTPUT
```json
{{ "log_rlhf": {{}}, "delta_capital": {{}}, "prompt_improvement": "", "level_up": false }}
```"""

    @staticmethod
    def _rhi_level(rhi: float) -> str:
        if rhi < 0.2:
            return "semeador"
        elif rhi < 0.4:
            return "brotador"
        elif rhi < 0.6:
            return "cultivador"
        elif rhi < 0.8:
            return "guardião"
        else:
            return "sábio"

    def run_full_chain(self, ativo: str, config: InvestorConfig,
                       metrics: dict, capital: CapitalGridResult,
                       decision: DecisionOutput, log: RlhfLog) -> dict[str, str]:
        chain = {
            "level0_context": self.level0_context(config, ativo),
            "level1_financial_dd": self.level1_financial_dd(CognitiveMap(), metrics),
            "level2_regenerative_dd": self.level2_regenerative_dd(capital),
            "level3_semiotic": self.level3_semiotic(ativo, metrics),
            "level4_axiological": self.level4_axiological(decision, config),
            "level5_rlhf": self.level5_rlhf(log),
        }
        self.history.append({"ativo": ativo, "timestamp": __import__("datetime").datetime.now().isoformat(), "chain": chain})
        return chain
