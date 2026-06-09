# Grid KAIROS — Sistema de Avaliação de Capitais Múltiplos

## Configurável

O KAIROS é configurável via `add_dimension()`:

```python
from invest_os.capitals.grid import CapitalGrid

kairos = CapitalGrid()
kairos.add_dimension(name="ecological", weight=0.15, metric="shannon_h", threshold=1.2)
kairos.add_dimension(name="spiritual", weight=0.05, metric="purpose_score", threshold=0.5)
kairos.add_dimension(name="financial", weight=0.20, metric="mvrv", threshold=3.5)
```

## Dimensões Default

| Dimensão | Peso | Métrica | Threshold | Bloqueio |
|----------|------|---------|-----------|----------|
| financeiro | 0.20 | mvrv | 3.5 | - |
| vivo | 0.15 | shannon_h | 1.2 | Monocultura |
| material | 0.10 | - | - | - |
| social | 0.15 | gini | 0.5 | Plutocracia |
| intelectual | 0.15 | - | - | - |
| experiencial | 0.10 | - | - | - |
| cultural | 0.10 | - | - | - |
| espiritual | 0.05 | - | - | - |

## Bloqueios

Um bloqueio em qualquer dimensão com threshold dispara `Action.EVITAR`. Isso implementa o princípio de "não fazer mal" (precautionary principle).

## RHI

O RHI (Regenerative Health Index) é a média ponderada dos scores de todas as dimensões:

```
RHI = 0.20·score_financeiro + 0.15·score_vivo + 0.10·score_material + ...
```

### Níveis Arquetípicos

| RHI | Nível | Comportamento |
|-----|-------|---------------|
| 0-20% | Semeador | Aprendendo; posições pequenas |
| 21-40% | Brotador | Primeiros impactos; diversificação |
| 41-60% | Cultivador | Portfolio equilibrado |
| 61-80% | Guardião | Proteção de valor; mentoria |
| 81-100% | Sábio | Individuação completa |
