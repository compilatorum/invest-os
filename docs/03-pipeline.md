# Pipeline Cognitivo

O pipeline opera em 6 estágios:

```
Percepção → Normalização → Modelagem → Interpretação → Decisão → Memória
```

## Estágios

### 1. Percepção
Coleta dados brutos do mundo: métricas on-chain (NVT, MVRV, SOPR), off-chain (GitHub, comunidade), e parâmetros de mercado.

### 2. Normalização
Transforma sinais brutos em `NormalizedSignal` com valores entre 0 e 1. Cada tipo de sinal (market, social, code, governance) tem seu próprio normalizador.

### 3. Modelagem
Executa simulações antes da interpretação:
- GBM para cenários de preço
- Lotka-Volterra para dinâmica Capital Vivo × Financeiro

### 4. Interpretação (Semiose + KAIROS)
Avalia o ativo sob as 8 dimensões de capital via `CapitalGrid`. Gera análise semiótica (signo, objeto, interpretante) com coerência e ruído.

### 5. Decisão
Recomenda ação (COMPRAR, AGUARDAR, REBALANCEAR, EVITAR) com base no score composto e nas condições de bloqueio.

### 6. Memória
Registra o resultado, atualiza RLHF, detecta drift, e evolui o perfil do investidor.
