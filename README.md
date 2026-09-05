# MLB Projection Pipeline

Pipeline modular en Python para proyectar mercados de MLB usando la API v3 de **SportsData.io**.

## Mercados Cubiertos

| Mercado | Metodología | Distribución |
|:---|:---|:---|
| **Moneyline** | Monte Carlo (10,000 sims) | Conway-Maxwell-Poisson |
| **Team Totals** | Monte Carlo + ratings ajustados | CMP por equipo |
| **Player Props (Hits)** | Simulación compuesta | Poisson(PA) × Binomial(Hits) |

## Métricas Avanzadas Implementadas

- **Bateo**: wOBA, wRC+, xBA, xwOBA, Contact%, Whiff%, ISO, BABIP
- **Pitcheo**: FIP, xFIP, SIERA, K%, BB%, HR/FB%, SwStr%, CSW%
- **Contexto**: Park Factors (16 estadios), ajustes por clima, fatiga de bullpen, splits platoon L/R

## Estructura del Proyecto
