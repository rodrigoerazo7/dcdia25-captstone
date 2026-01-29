# Backlog 

**Optimización y Evaluación de Portafolios con Técnicas de ML y RL**  
Diplomado en Ciencia de Datos e Inteligencia Artificial – Universidad de Chile (FEN)

---

## Épica 1: Fundaciones de Datos y Baselines

**Objetivo:** Establecer líneas base sólidas, reproducibles y comparables para todo el proyecto.

### Feature 1.1: Pipeline de datos y EDA

* Pipeline de ingestión y limpieza de datos históricos
* Validación de calidad, consistencia y alineación temporal
* Análisis exploratorio univariado y multivariado

### Feature 1.2: Implementación de baselines financieros

* Buy & Hold por activo (universo MAG7)
* Portafolio MVO – Maximización del Ratio de Sharpe
* Portafolio equiponderado como baseline adicional

### Feature 1.3: Métricas de evaluación

* Retorno total
* CAGR
* Volatilidad anual
* Ratio de Sharpe
* Maximum Drawdown
* Ratio de Calmar

---

## Épica 2: Modelos de Forecasting

**Objetivo:** Modelar dinámicas futuras de precios y retornos para apoyar decisiones de optimización.

### Feature 2.1: Forecasting univariado

* Entrenamiento de modelos SARIMA por activo
* Validación estricta out-of-sample mediante split temporal
* Documentación de supuestos y parámetros

### Feature 2.2: Robustez y estabilidad

* Análisis de sensibilidad ante cambios de régimen
* Evaluación de desempeño en períodos extremos
* Simplificación de modelos para mitigar sobreajuste

### Feature 2.3: Extensiones del forecasting

* Implementación de modelos multivariados
* Comparación entre enfoques univariados y multivariados
* Evaluación del impacto en la optimización de portafolios

---

## Épica 3: Optimización de Portafolios

**Objetivo:** Construir portafolios eficientes con control explícito de riesgo.

### Feature 3.1: Optimización Media-Varianza (MVO)

* Estimación de retornos esperados
* Construcción de matriz de covarianza histórica
* Optimización MVO Max Sharpe
* Evaluación fuera de muestra

### Feature 3.2: Restricciones y variantes

* Restricciones de peso máximo por activo
* Prohibición de ventas en corto
* Optimización robusta frente a errores de estimación

### Feature 3.3: Evaluación de supuestos

* Análisis del supuesto de normalidad de retornos
* Estabilidad temporal de la covarianza
* Sensibilidad del portafolio a inputs del modelo

---

## Épica 4: Reinforcement Learning para Gestión de Portafolios

**Objetivo:** Explorar políticas dinámicas de asignación mediante aprendizaje por refuerzo.

### Feature 4.1: Diseño del entorno RL

* Definición del espacio de estados, acciones y recompensas
* Implementación del entorno multi-activo
* Documentación del enfoque PPO

### Feature 4.2: Entrenamiento incremental

* Entrenamiento en entorno simplificado
* Comparación contra baselines tradicionales
* Validación de estabilidad y convergencia

### Feature 4.3: Control de riesgo en RL

* Penalización explícita por drawdowns
* Control de rotación y costos implícitos
* Análisis de comportamiento en escenarios adversos

---

## Épica 5: Backtesting Realista y Evaluación de Riesgo

**Objetivo:** Reducir la brecha entre resultados académicos y condiciones reales de mercado.

### Feature 5.1: Fricciones de mercado

* Incorporación de costos de transacción
* Modelado de slippage
* Evaluación comparativa con y sin fricciones

### Feature 5.2: Análisis por regímenes de mercado

* Segmentación en períodos bull, bear y alta volatilidad
* Evaluación de desempeño por subperíodos
* Identificación de fragilidad estructural

### Feature 5.3: Robustez estadística

* Bootstrap de retornos
* Intervalos de confianza para métricas clave
* Pruebas de significancia entre estrategias

---

## Épica 6: Visualización y Análisis de Resultados

**Objetivo:** Facilitar interpretación, validación y comunicación de los resultados.

### Feature 6.1: Visualizaciones base

* Matriz de correlación de retornos
* Series de precios normalizados
* Histogramas de retornos diarios
* Curvas de valor del portafolio

### Feature 6.2: Visualizaciones avanzadas

* Evolución temporal del riesgo
* Contribución marginal al riesgo por activo
* Comparación dinámica entre estrategias

---

## Épica 7: Documentación, Riesgos y Entrega Académica

**Objetivo:** Asegurar trazabilidad técnica, rigor académico y claridad en la entrega final.

### Feature 7.1: Documentación técnica

* Justificación de decisiones de diseño
* Registro explícito de limitaciones y supuestos
* Manual reproducible del pipeline completo

### Feature 7.2: Gestión de riesgos del proyecto

* Identificación y clasificación de riesgos técnicos
* Estrategias de mitigación
* Discusión crítica de resultados

### Feature 7.3: Entregables finales

* Consolidación de resultados
* Redacción de conclusiones y trabajo futuro
* Preparación de material para presentación y defensa

