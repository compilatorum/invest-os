# Governança Algorítmica

## 8 Princípios de Ostrom

| Princípio | Verificação | Implementação |
|-----------|------------|---------------|
| Fronteiras Claras | SBT Token-Gating | `has_sbt` |
| Congruência Local | Sub-DAOs por biorregião | `local_config` |
| Escolha Coletiva | Votação quadrática | `voting_enabled` |
| Monitoramento | Oráculos híbridos | `has_oracles` |
| Sanções Graduadas | Slashing progressivo | `has_slashing` |
| Resolução de Conflitos | Kleros Integration | `has_dispute_resolution` |
| Reconhecimento Externo | Wrappers legais | `has_legal_framework` |
| Empresas Aninhadas | DAO de DAOs | `is_dao_of_daos` |

## Goodhart Shield

Proteção contra o efeito Goodhart ("quando uma métrica vira alvo, deixa de ser boa métrica"):

- Ruído estocástico anti-gaming
- Adaptação dinâmica de pesos
- Detecção de drift via z-score

## Drift Detection

Monitora métricas ao longo do tempo e alerta quando ocorre desvio significativo (|z| > 2.0) nos últimos N samples.
