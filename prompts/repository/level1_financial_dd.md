# Nível 1 — Due Diligence Financeira (Messari/Stephen Style)

## INPUT
Mapa cognitivo do Nível 0.

## TASK
Calcule e interprete para {ATIVO}:
- **NVT**: Market Cap / Transaction Volume (alerta se > 2 desvios da média)
- **MVRV**: Market Cap / Realized Cap (< 1.0 = oportunidade; > 3.5 = perigo)
- **SOPR**: se < 1.0 = holders vendendo no prejuízo (capitulação)
- **Sharpe 90d**: (Retorno - CDI_Brasil) / Volatilidade
- **IL Break-even** para posições DeFi: 2*sqrt(P2/P1)/(1+P2/P1)-1
- **Temperatura**: Volatilidade_24h * Exposição_%

## ALERTA AUTOMÁTICO
se NVT_zscore > 2.0 E mindshare_growth > 30% → HYPE

## OUTPUT
```json
{ "metricas": {}, "score_financeiro": 0.0, "alertas": [], "recomendacao": "" }
```
