# Modelagem Matemática

## Lotka-Volterra (Capital Vivo × Financeiro)

```
dV/dt = α·V - β·V·F
dF/dt = δ·V·F - γ·F
```

Onde:
- V = Capital Vivo (biodiversidade, saúde do ecossistema)
- F = Capital Financeiro
- α = taxa de regeneração do capital vivo
- β = taxa de extração pelo financeiro
- δ = taxa de conversão de capital vivo em financeiro
- γ = taxa de dissipação do capital financeiro

## Geometric Brownian Motion (Preço)

```
dS = μ·S·dt + σ·S·dW
```

Usado para simular cenários estocásticos de preço antes da tomada de decisão.

## RHI (Regenerative Health Index)

```
RHI = Σ(w_i · score_i)  para i em {8 capitais}
```

Onde `w_i` são os pesos configuráveis de cada dimensão de capital.

## MVRV (Market Value to Realized Value)

```
MVRV = Market Cap / Realized Cap
```

- MVRV < 1.0: oportunidade de acumulação
- MVRV > 3.5: sobrevalorização

## Shannon Entropy (Diversidade de Portfolio)

```
H' = -Σ(p_i · log₂(p_i))
```

- H' < 1.2: monocultura (alerta crítico)

## Gini Coefficient (Desigualdade)

```
G = (n+1 - 2·Σ((n-i+1)·v_i) / (n·mean)) / n
```

- G > 0.5: plutocracia (alerta crítico)
