# 🔄 Plano de Refatoração — InvestmentOS → Capital OS

> A qualidade de uma arquitetura não é medida pela quantidade de conceitos que ela contém, mas pela quantidade de conceitos que ela consegue ocultar.

---

## 🧭 Diagnóstico Geral

- **Visão**: 10/10 · **Pesquisa**: 10/10 · **Ontologia**: 9.5/10
- **Arquitetura**: 8/10 · **Modularidade**: 7.8/10 · **Operabilidade**: 7.5/10
- ⚠️ Risco central: **excesso de densidade epistemológica por unidade de código**
- ⚠️ 1 produto = 10 produtos (InvestmentOS, ReFi, Oracle, Prompt, Multi-Agent, cadCAD, Econofísica, Due Diligence, Governança, Aprendizagem)
- ⚠️ README funciona como whitepaper + manifesto + roadmap + spec + documentação — precisa ser destilado

### 🎯 Direção

Evoluir de **"sistema de investimentos"** para **"sistema operacional de capitais"** (Capital OS / KAIROS OS).

---

## 🌳 Fase 1 — Pureza Ontológica (curto prazo · 0–4 semanas)

### 📦 1.1 Núcleo Mínimo: `invest-os-core`

```
invest-os-core/
├── signals/    # Tudo vira sinal: MarketSignal, SocialSignal, CodeSignal, GovernanceSignal
├── scores/     # RHI, Sharpe, MVRV, SOPR, HHI, Gini, Entropia
└── decisions/  # Invest, Grant, Mentor, Connect, Ignore, Monitor
```

- ✂️ Extrair `signals/` — normalização de tweets, commits, transações, observações em sinais padronizados
- ✂️ Extrair `scores/` — todo cálculo de métrica mora aqui (descritivas + interpretativas)
- ✂️ Extrair `decisions/` — recommenders, gates humanos, alçadas por perfil

### 🧩 1.2 Ontologia Explícita

- 🏗️ Criar `invest_os/entities/` — `Person`, `Project`, `Community`, `Organization`, `DAO`, `Fund`
- 🏗️ Criar `invest_os/capitals/` — `FinancialCapital`, `HumanCapital`, `SocialCapital`, `CulturalCapital`, `NaturalCapital` (hierarquia de `Capital` base)
- 🏗️ `CapitalGrid` em `capitals/` — avaliador configurável de dimensões de capital
- 🏗️ `Entity.capital_score()` → acopla entidades a seus scores de capital

### 🔧 1.3 Pipeline Refinado

Atual:
```
Percepção → Semiose → Interpretação → Decisão → Registro
```

Novo:
```
Percepção → Normalização → Modelagem → Interpretação → Decisão → Memória
```

- ➕ **Normalização**: transforma dados brutos em sinais padronizados (nova camada)
- ➕ **Modelagem**: GBM, Lotka-Volterra, ABM, cadCAD — simula cenários antes da interpretação
- ➕ **Memória**: substitui "Registro" — inclui RLHF + drift detection + level-up do investidor
- 🔄 Semiose e Interpretação estavam acopladas — agora são fases distintas

### 🧪 1.4 Testes Ontológicos

- ✅ `assert each_module_represents_one_concept()`
- ✅ `assert entity_has_capital_score()`
- ✅ `assert signal_normalization_is_lossless()`
- ✅ `assert pipeline_stages_are_decoupled()`

---

## 🔬 Fase 2 — Limpeza de Acoplamento (médio prazo · 4–12 semanas)

### 📦 2.1 Separação em Pacotes

```
invest-os-core/        # Signals → Scores → Decisions (núcleo mínimo publicável)
invest-os-governance/  # Ostrom 8 princípios + Goodhart Shield + Conviction Voting
invest-os-cadcad/      # Gêmeos digitais, ABM, TokenSPICE, Purged K-Fold
invest-os-prompts/     # Motor epistêmico (desacoplado do domínio financeiro)
invest-os-regenerative/ # KAIROS, RHI, métricas de capital natural
invest-os-semiotics/   # Análise de signos, coerência, ruído, fases alquímicas
invest-os-web3/        # Conectores on-chain, oráculos, carteiras
```

- 🔗 `governance/` → pacote independente reutilizável por outros projetos
- 🔗 `prompts/engine.py` → motor epistêmico genérico (não apenas para investimentos)
- 🔗 `core/capital_grid.py` → `invest-os-regenerative` com KAIROS configurável

### 📐 2.2 Camadas de Métricas

Atual: métricas financeiras, axiológicas e interpretativas misturadas.

| Camada | Função | Exemplos |
|--------|--------|----------|
| 📊 **Descritiva** | O que aconteceu? | Sharpe, MVRV, NVT, SOPR |
| 🌿 **Interpretativa** | O que significa? | KAIROS 8 capitais, Gini, Entropia |
| 🧬 **Axiológica** | Qual o valor? | RHI, Score de Propósito, Impacto |
| ⚖️ **Decisória** | O que fazer? | Recommendation, Allocation |

- ✂️ Separar `metrics.py` em `descritivas/`, `interpretativas/`, `axiologicas/`, `decisorias/`
- ✂️ `calculate_all_metrics()` atual tem 12 parâmetros → quebrar em builders por camada

### 🧠 2.3 Motor Epistêmico (Prompt Engine)

- 🔄 Desacoplar `PromptEngine` do domínio financeiro — deve servir a qualquer domínio (grants, avaliação de pessoas, pesquisa científica)
- 🏗️ `PromptRouter` — classifica intenção e seleciona arquétipo
- 🏗️ `PromptChain` — orquestra sequências (diagnóstico → simulação → decisão)
- 🏗️ `MetaPrompt4D` — autoavaliação (precisão, alinhamento, clareza, ontologia)
- 🏗️ `DriftDetector` — monitora eficácia ao longo do tempo
- 🏗️ `DSPyOptimizer` — A/B testing + otimização automatizada
- ➕ RAG Quântico: espaços latentes + álgebra de Clifford para recuperação semântica
- 🔗 `load_prompt_repo()` atual usa path frágil → resolver com `importlib.resources`

### 🌿 2.4 KAIROS Configurável

Atual: 8 capitais fixos.

Novo:
```python
kairos = CapitalGrid()
kairos.add_dimension(name="ecological", weight=0.15, metric="shannon_h", threshold=1.2)
kairos.add_dimension(name="spiritual", weight=0.05, metric="purpose_score", threshold=0.5)
```

- 🏗️ `CapitalDimension` — classe configurável com nome, peso, métrica, threshold
- 🏗️ `CapitalGrid.evaluate()` — itera sobre dimensões configuradas, não fixas
- ➕ Serialização YAML/JSON do grid — permite perfis de capital diferentes por investidor

### 🧪 2.5 Testes de Acoplamento

- ✅ `assert cli_does_not_import_cognitive_directly()`
- ✅ `assert governance_can_be_installed_independently()`
- ✅ `assert prompts_engine_works_without_finance_domain()`
- ✅ `assert kairos_add_dimension_affects_rhi()`

---

## 🌱 Fase 3 — Sistema Operacional de Capitais (longo prazo · 12–24 semanas)

### 📁 3.1 Estrutura-alvo

```
invest-os/                       # Meta-repositório (monorepo ou org)
├── core/                        # invest-os-core
│   ├── signals/                 # MarketSignal, SocialSignal, CodeSignal, GovernanceSignal
│   ├── scores/                  # Sharpe, MVRV, NVT, HHI, Gini, Entropia
│   └── decisions/               # Invest, Grant, Connect, Mentor, Ignore, Monitor
├── capitals/                    # KAIROS configurável + RHI
│   ├── dimensions/              # FinancialCapital, NaturalCapital, SocialCapital...
│   └── evaluator.py             # CapitalGrid com add_dimension()
├── models/                      # Simulação e modelagem
│   ├── gbm.py                   # Geometric Brownian Motion
│   ├── lotka_volterra.py        # Capital Vivo × Financeiro
│   ├── abm/                     # Agent-Based Modeling
│   └── cadcad/                  # Gêmeos digitais (integrado com invest-os-cadcad)
├── prompts/                     # Motor epistêmico (desacoplado)
│   ├── engine.py                # PromptEngine genérico
│   ├── router.py                # Roteamento por intenção
│   ├── chains/                  # Sequências de prompts
│   ├── metaprompts/             # Autoavaliação 4D
│   └── drift.py                 # Drift detection + DSPy optimizer
├── governance/                  # (pode ser pacote separado)
│   ├── ostrom.py                # 8 princípios
│   ├── conviction.py            # Conviction Voting
│   ├── gds.py                   # Generalized Dynamical Systems (Zargham)
│   └── shield.py                # Goodhart Shield + drift
├── entities/                    # Ontologia explícita
│   ├── base.py                  # Entity → capital_score()
│   ├── person.py
│   ├── project.py
│   ├── community.py
│   ├── dao.py
│   └── fund.py
├── learning/                    # Memória do sistema
│   ├── rlhf.py                  # Feedback loop
│   ├── drift.py                 # Detecção de drift
│   └── level_up.py              # Evolução do investidor
├── cli/                         # (separado do core)
│   ├── main.py                  # Click entrypoint
│   ├── commands/
│   │   ├── analyze.py
│   │   ├── pipeline.py
│   │   ├── simulate.py
│   │   ├── governance.py
│   │   └── prompts.py
│   └── render.py                # Rich output helpers
└── docs/                        # Documentação (extraída do README)
    ├── 00-filosofema.md
    ├── 01-ontologia.md
    ├── 02-matematica.md          # Lotka-Volterra, Langevin, Supertensor de Valor
    ├── 03-pipeline.md
    ├── 04-kairos.md
    ├── 05-governanca.md
    ├── 06-simulacao.md           # cadCAD, ABM, Purged K-Fold
    ├── 07-prompt-engineering.md
    └── 08-seguranca.md
```

### 🔬 3.2 Laboratório de Simulação (cadCAD)

- 🏗️ `invest-os-cadcad` — Gêmeos Digitais para testar estratégias antes da execução real
- 🏗️ Ciclo **Engenheiro vs. Piloto**: validar o modelo ≠ operar o sistema
- 🏗️ **Purged K-Fold**: validação cruzada temporal sem data leakage (López de Prado)
- 🏗️ **Agent-Based Modeling**: simular comportamentos emergentes (arbitradores, liquidadores)
- ➕ `TokenSPICE` — ABM + EVM in-the-loop
- ➕ `radCAD` — sweeps paramétricos 10-100x

### 🏛️ 3.3 Governança Algorítmica (Ostrom + GDS)

- 🏗️ **Ostrom 8 princípios** codificados em contratos:
  - `Fronteiras Claras` → SBT Token-Gating
  - `Congruência Local` → Sub-DAOs fractais por biorregião
  - `Escolha Coletiva` → Votação quadrática / Conviction Voting
  - `Monitoramento` → Oráculos híbridos (Coordinape + dClimate)
  - `Sanções Graduadas` → Slashing progressivo
  - `Resolução de Conflitos` → Kleros Integration
  - `Reconhecimento Externo` → Wrappers legais UNA/LLC
  - `Empresas Aninhadas` → DAO de DAOs
- 🏗️ **GDS (Zargham)**: separação entre mecânica do sistema (φ) e política dos agentes (π)
- ➕ Ruído estocástico anti-gaming (Goodhart Shield)
- ➕ Fechamento operacional: código imutável, parâmetros evolutivos via DAO

### 🧪 3.4 Testes Avançados

Além dos 217 testes atuais (99% coverage):

| Tipo | Exemplo |
|------|---------|
| 🧮 **Invariantes** | `assert entropy >= 0`, `assert sum(weights) ≈ 1.0` |
| 🏛️ **Governança** | `assert plutocracy_score < limit`, `assert conviction_threshold_met()` |
| ⚛️ **Simulação** | `assert capital_alive_after_shock()`, `assert system_converges()` |
| 🧬 **Filosofema** | `assert system_generates_more_capital_than_consumes()` |
| 🔄 **Regressão ontológica** | `assert every_entity_has_capital_score()`, `assert every_signal_produces_score()` |
| 🔐 **Segurança** | `assert prompt_injection_fails()`, `assert dry_run_prevents_loss()` |

### 📚 3.5 Documentação (README → docs/)

Atual: README = whitepaper + manifesto + roadmap + spec + prompt + documentação.

Novo:
```
README.md          → O que é? Como instalar? Como executar? (3 min)
docs/00-filosofema → Filosofema central e visão
docs/01-ontologia  → Entidades, Capitais, Sinais, Scores, Decisões
docs/02-matematica → Formalismos: Lotka-Volterra, Langevin, Supertensor
docs/03-pipeline   → Pipeline cognitivo 6 estágios
docs/04-kairos     → Grid KAIROS configurável (8+ capitais)
docs/05-governanca → Ostrom, Conviction Voting, GDS
docs/06-simulacao  → cadCAD, ABM, Purged K-Fold, TokenSPICE
docs/07-prompts    → Motor epistêmico, router, chains, metaprompts, drift
docs/08-seguranca  → ZK-Proofs, gates humanos, fallbacks low-tech
```

---

## 📊 Notas de Referência

| Dimensão | Nota | Alvo Fase 3 |
|----------|------|-------------|
| Ontologia | 9.8 | 10 |
| Arquitetura Conceitual | 9.3 | 10 |
| Economia Computacional | 9.7 | 10 |
| Engenharia de Software | 8.2 | 9.5 |
| Modularidade | 7.8 | 9.5 |
| Operabilidade | 7.5 | 9.0 |
| Escalabilidade Conceitual | 9.4 | 10 |
| Escalabilidade de Implementação | 7.4 | 9.5 |

## 🧬 Veredito

> O projeto está mais próximo de uma **linguagem para avaliar e alocar capitais múltiplos** do que de uma ferramenta de investimentos. A próxima evolução não deveria ser adicionar funcionalidades, mas **destilar ontologias, reduzir acoplamentos e transformar filosofemas em contratos explícitos da arquitetura**.

### 🧬 Filosofema-Guia

> "Investir não é escolher ativos; é aumentar a capacidade adaptativa de sistemas vivos através da alocação inteligente de capitais múltiplos."

---

## 🔍 Checklist de Progresso

### Fase 1 — Pureza Ontológica
- [ ] `invest-os-core` extraído com signals → scores → decisions
- [ ] `entities/` com Person, Project, Community, Organization, DAO, Fund
- [ ] `capitals/` com hierarquia de Capital base
- [ ] Pipeline refinado: Percepção → Normalização → Modelagem → Interpretação → Decisão → Memória
- [ ] Testes ontológicos passando

### Fase 2 — Limpeza de Acoplamento
- [ ] Pacotes separados: governance, cadcad, prompts, regenerative, semiotics
- [ ] Métricas em 4 camadas: Descritiva, Interpretativa, Axiológica, Decisória
- [ ] PromptEngine desacoplado como motor epistêmico
- [ ] KAIROS configurável via `add_dimension()`
- [ ] Testes de acoplamento passando

### Fase 3 — Sistema Operacional de Capitais
- [ ] Estrutura-alvo implementada
- [ ] Laboratório de simulação (cadCAD + ABM + Purged K-Fold)
- [ ] Governança algorítmica (Ostrom + GDS + Conviction Voting)
- [ ] Testes de invariante, governança, simulação e filosofema
- [ ] Documentação migrada para `docs/` — README enxuto
- [ ] Sistema produz mais capital do que consome
