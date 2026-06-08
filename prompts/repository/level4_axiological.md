# Nível 4 — Decisão Axiológica & Gate Humano

## INPUT
Análise completa dos Níveis 0-3.

## TASK
Sintetize uma recomendação final para {ATIVO}:

- **Score composto**: 40% financeiro + 35% regenerativo + 25% semiótico
- **Alinhamento com perfil** {PERFIL}: 0 a 100%
- **Ação recomendada**: COMPRAR / AGUARDAR / REBALANCEAR / EVITAR
- **Tamanho de posição**: % do portfolio (respeitar HHI < 0.25)
- **Narrativa para o investidor**: tom {MODO_LINGUAGEM}

## GATE
se valor > limite_perfil → acionar confirmação humana obrigatória

## MINT
se ação = COMPRAR → gerar metadata para NFT de posição

## OUTPUT
```json
{ "acao": "", "tamanho_posicao": 0.0, "score_composto": 0.0, "narrativa": "", "metadata_nft": {} }
```
