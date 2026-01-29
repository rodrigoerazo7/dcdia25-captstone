# Proyecto Capstone IA  
## Resultados preliminares y análisis técnico  
**Diplomado en Ciencia de Datos e Inteligencia Artificial**  
**Universidad de Chile – FEN**

---

## Baselines definidos

Se definieron como líneas base (*baselines*) las siguientes estrategias:

- **Buy & Hold por activo**  
  - Estrategia pasiva consistente en mantener cada activo del universo MAG7 durante todo el período de evaluación.
  - Permite establecer una referencia clara y ampliamente aceptada en análisis financiero.

- **Portafolio MVO – Max Sharpe**  
  - Optimización media-varianza utilizando retornos esperados estimados y matriz de covarianza histórica.
  - Sirve como baseline optimizado frente a estrategias puramente pasivas.

Estas estrategias permiten comparar desempeño absoluto y ajustado por riesgo frente a enfoques más complejos.

---

## Estado del entrenamiento

- El pipeline de datos y EDA se encuentra **completamente implementado y validado**.
- Los modelos de forecasting basados en **SARIMA** fueron entrenados individualmente por activo.
- El módulo de **optimización MVO** se encuentra operativo y evaluado en datos fuera de muestra.
- El módulo de **Reinforcement Learning (PPO)** se encuentra documentado, pero **deshabilitado** en esta etapa debido a complejidad computacional y necesidad de validación incremental.

---

# 4. Resultados preliminares

## Métricas obtenidas hasta la fecha

Las métricas evaluadas en el conjunto de test (2022–2024) incluyen:

- Retorno total
- CAGR (aproximado)
- Volatilidad anual
- Ratio de Sharpe
- Maximum Drawdown
- Ratio de Calmar

Resultados destacados:
- Algunos activos individuales (p.ej. NVDA) presentan retornos acumulados muy elevados, acompañados de drawdowns significativos.
- El portafolio **MVO Max Sharpe** muestra un mejor equilibrio riesgo/retorno en comparación con la mayoría de los baselines individuales.

---

## Comparación inicial entre modelos

- **Buy & Hold**:
  - Alto desempeño en activos con fuerte crecimiento estructural.
  - Alta exposición a riesgo idiosincrático y drawdowns profundos.

- **MVO Max Sharpe**:
  - Menor retorno absoluto que el mejor activo individual.
  - Mejor control de volatilidad y drawdown agregado.
  - Mayor estabilidad intertemporal.

La comparación sugiere un trade-off claro entre maximización de retorno y control de riesgo.

---

## Visualización de resultados relevantes

Se utilizaron las siguientes visualizaciones clave:

- Matriz de correlación de retornos (identificación de dependencias entre activos).
- Series de precios normalizados (base = 100) para comparar crecimiento relativo.
- Histograma del retorno diario promedio (*cross-assets*).
- Curvas de valor normalizadas (equity curves) para baselines y portafolio optimizado.

Estas visualizaciones permitieron identificar patrones de correlación, concentración de riesgo y efectos de diversificación.

---

# 5. Análisis inicial

## Interpretación de resultados parciales

- El desempeño de las estrategias está fuertemente condicionado por el régimen de mercado.
- Estrategias concentradas pueden dominar en retorno, pero presentan mayor fragilidad ante shocks.
- La diversificación vía MVO reduce riesgo extremo, aunque limita el retorno máximo alcanzable.

---

## Principales errores y limitaciones detectadas

- Sensibilidad de los modelos de forecasting a cambios de régimen.
- Supuestos de normalidad y estabilidad en la covarianza para MVO.
- Ausencia de costos de transacción y slippage en la evaluación actual.
- Dependencia de datos diarios, sin información intradía.

---

# 6. Decisiones técnicas y riesgos

## Decisiones clave de diseño

- Uso de **split temporal** para evitar fuga de información.
- Selección de métricas enfocadas en riesgo/retorno (Sharpe, Calmar).
- Implementación incremental: baselines → optimización → RL.
- Priorización de interpretabilidad en etapas tempranas del proyecto.

---

## Riesgos técnicos identificados y mitigación

- **Sobreajuste en forecasting**  
  → Evaluación estricta out-of-sample y simplificación de modelos.

- **Inestabilidad en RL multi-activo**  
  → Postergación del módulo RL hasta consolidar baselines robustos.

- **Subestimación de riesgo real**  
  → Plan de incorporación de costos, slippage y análisis por regímenes.

---

# 7. Próximos pasos

## Ajustes en datos y feature engineering

- Incorporar features de régimen (volatilidad, tendencia, drawdown).
- Evaluar reducción dimensional y selección de variables.
- Análisis de sensibilidad frente a outliers extremos.

---

## Nuevos modelos a implementar

- Extensiones del forecasting (p.ej. modelos multivariados).
- Variantes de optimización con restricciones adicionales.
- Activación controlada del módulo de Reinforcement Learning (PPO).

---

## Experimentos pendientes

- Backtesting con costos de transacción realistas.
- Evaluación por subperíodos (bull / bear / alta volatilidad).
- Análisis estadístico de robustez (bootstrap de retornos, intervalos de confianza).
- Comparación con portafolios equiponderados como baseline adicional.

---
