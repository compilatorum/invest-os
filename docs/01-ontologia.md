# Ontologia do Capital OS

## Entidades

Tudo no Capital OS é uma `Entity`:

```
Entity
├── Person         (indivíduo, investidor, curador)
├── Project        (protocolo, dApp, iniciativa)
├── Community      (comunidade, biorregião)
├── Organization   (empresa, instituto, fundação)
├── DAO            (organização descentralizada autônoma)
└── Fund           (veículo de investimento)
```

Cada `Entity` possui um método `capital_score()` que retorna seu RHI.

## Capitais

As 8+ dimensões de capital são modeladas como `CapitalDimension`:

| Capital | Peso Default | Métrica de Alerta |
|---------|-------------|-------------------|
| Financeiro | 0.20 | MVRV > 3.5 |
| Vivo | 0.15 | Shannon H' < 1.2 |
| Material | 0.10 | - |
| Social | 0.15 | Gini > 0.5 |
| Intelectual | 0.15 | - |
| Experiencial | 0.10 | - |
| Cultural | 0.10 | - |
| Espiritual | 0.05 | - |

## Sinais

Toda observação do mundo vira um `Signal`:

- `MarketSignal`: dados on-chain (preço, volume, realized cap)
- `SocialSignal`: métricas sociais (tamanho da comunidade, participação)
- `CodeSignal`: atividade de desenvolvimento (stars, forks, contribuidores)
- `GovernanceSignal`: maturidade de governança (SBT, votação, oráculos)

## Scores

Os scores são organizados em 4 camadas:

| Camada | Função | Exemplos |
|--------|--------|----------|
| Descritiva | O que aconteceu? | Sharpe, MVRV, NVT, SOPR |
| Interpretativa | O que significa? | Gini, Entropia, HHI |
| Axiológica | Qual o valor? | RHI, Purpose Score |
| Decisória | O que fazer? | Recommend, Allocation |
