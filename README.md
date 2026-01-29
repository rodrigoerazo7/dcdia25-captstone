# Portfolio Optimization Toolkit

## Diseño e Implementación de Herramientas para Optimización Dinámica de Portafolios

### FEN Univesidad de Chile - Capstone Proyecto de Inteligencia Artificial

**2025 – Semestre 2**

---

## 1. Introducción

Este repositorio contiene la implementación de un **pipeline experimental de Ciencia de Datos e Inteligencia Artificial** orientado a la **optimización dinámica de portafolios de inversión**. El proyecto se enmarca en el contexto de una **Startup Fintech / Consultora de Inversiones**, donde la toma de decisiones enfrenta mercados financieros **no estacionarios**, con **cambios de régimen** y alta incertidumbre.

La solución propuesta no se basa en un único modelo, sino en una **caja de herramientas modular**, que integra técnicas clásicas y modernas de análisis cuantitativo, forecasting, optimización matemática y aprendizaje por refuerzo, con el objetivo de evaluar su desempeño relativo, robustez y viabilidad técnica.

---

## 2. Objetivo del Proyecto

El objetivo general es **diseñar, implementar y evaluar una arquitectura experimental** que permita:

* Analizar datos financieros históricos de forma reproducible.
* Generar expectativas de retorno mediante modelos estocásticos de series de tiempo.
* Optimizar asignaciones de capital bajo restricciones realistas.
* Adaptar dinámicamente la exposición al riesgo mediante control secuencial.
* Comparar enfoques tradicionales y basados en IA bajo métricas de riesgo–retorno.
* Documentar todo el proceso mediante un reporte técnico estructurado.

---

## 3. Enfoques Metodológicos Integrados

La caja de herramientas incorpora los siguientes enfoques:

### 3.1 Ingesta de Datos

* Descarga automatizada de datos financieros históricos mediante `yfinance`.
* Implementación de un sistema de **caché local en disco** (formato Parquet) para garantizar reproducibilidad y eficiencia computacional.

### 3.2 Preprocesamiento y Feature Engineering

* Limpieza de datos y manejo de valores faltantes.
* Cálculo de retornos financieros (simples o logarítmicos).
* Construcción de indicadores técnicos ampliamente utilizados en finanzas cuantitativas:

  * Medias Móviles Simples (SMA)
  * Medias Móviles Exponenciales (EMA)
  * Índice de Fuerza Relativa (RSI)
  * Bandas de Bollinger
  * Volatilidad rodante
* Preparación de un conjunto de características adecuado para modelos de aprendizaje por refuerzo.

### 3.3 Análisis Exploratorio de Datos (EDA)

* Estadísticos descriptivos de retornos.
* Análisis de correlación entre activos.
* Detección de outliers mediante z-score.
* Generación automática de figuras.

### 3.4 Forecasting Estocástico

* Implementación de modelos SARIMA / SARIMAX.
* Trabajo en frecuencia mensual para capturar patrones estructurales.
* Incorporación de estacionalidad anual.
* Generación de **vectores de retornos esperados (μ)** como insumo para optimización.

### 3.5 Optimización de Portafolio

* Optimización de Media–Varianza (Markowitz).
* Implementación mediante la librería PyPortfolioOpt.
* Maximización del Ratio de Sharpe.
* Restricciones:
  * Long-only.
  * Límites máximos por activo.
* Rebalanceo periódico de tipo mensual.

### 3.6 Aprendizaje por Refuerzo (Opcional)

* Implementación de un agente PPO (Proximal Policy Optimization).
* Uso de Stable-Baselines3 y Gymnasium.
* Entorno de simulación simplificado (MVP conceptual).
* Función de recompensa penalizada por volatilidad.
* El módulo puede habilitarse o deshabilitarse desde configuración.

### 3.7 Evaluación y Comparación de Modelos

* Definición de baselines (Buy & Hold).
* Métricas de desempeño:
  * Retorno total
  * CAGR
  * Volatilidad anualizada
  * Ratio de Sharpe
  * Maximum Drawdown
  * Ratio de Calmar
* Comparación sistemática entre modelos.
* Generación de tablas y curvas de valor (INR).

---

## 4. Estructura del Proyecto

```text
portfolio_toolkit/
│
├── main.py                      # Script orquestador del pipeline experimental
├── config.yaml                  # Parámetros experimentales y de configuración
│
├── data/
│   ├── raw/                     # Caché de datos descargados
│   └── processed/               # Datos limpios, retornos y features
│
├── modules/
│   ├── data_ingestion.py        # Ingesta de datos y caché
│   ├── preprocessing.py         # Limpieza y feature engineering
│   ├── eda.py                   # Análisis exploratorio y visualizaciones
│   ├── forecasting.py           # Modelos SARIMA / SARIMAX
│   ├── optimization.py          # Optimización Mean–Variance
│   ├── rl_agent.py              # Aprendizaje por Refuerzo (PPO, opcional)
│   └── evaluation.py            # Evaluación, comparación y reporte
│
├── portfolios/
│   ├── outputs-20260129-023150-MIN-001/ # Plantilla: outputs-<timestamp>-<tag>
│   │   ├── MAG7/                        
│   │   │   ├── figures/                 # Imágenes PNG
│   │   │   ├── tables/                  # Tablas CSV
│   │   │   └── report_data.json         # Datos para el reporte
│   │   ├── FANG/
│   │   │   └── ...
│   │   ├── FAANG/
│   │   │   └── ...
│   │   └── portfolios_summary.csv
│   ├── outputs-20260130-141022-MAX-002/
│   │   └── ...
│   └── ...                      # Más ejecuciones
│
└── README.md
```

---

## 5. Requisitos del Entorno

### 5.1 Lenguaje

* Python 3.9 o superior.

### 5.2 Dependencias Base

```bash
pip install pandas numpy matplotlib yfinance pyyaml statsmodels
```

### 5.3 Optimización de Portafolio

```bash
pip install PyPortfolioOpt
```

### 5.4 Aprendizaje por Refuerzo (Opcional)

```bash
pip install gymnasium stable-baselines3
```

---

## 6. Ejecución del Proyecto

### 6.1 Configuración

Editar el archivo `config.yaml` para definir:

* Activos financieros.
* Rango temporal de análisis.
* División train/test.
* Activación o desactivación de módulos (MVO, RL).
* Parámetros de indicadores y métricas.

### 6.2 Ejecución del Pipeline

```bash
python main.py
```

### 6.3 Resultados Generados

Al finalizar la ejecución se generan automáticamente:

```text
portfolios/
└── outputs-<timestamp>-<tag>/      # Ej: outputs-20260129-023150-MIN-001
    ├── <portfolio_1>/				# Ej: MAG7/
    │   ├── figures/                # Figuras para el informe
    │   ├── tables/                 # Resultados tabulares
    │   └── report_data.json        # Datos para el reporte
    ├── <portfolio_2>/				# Ej: FANG/
    │   ├── figures/				
    │   ├── tables/
    │   └── report_data.json
    ├── ...
    └── portfolios_summary.csv      # Resumen consolidado de todos los portafolios
```

---

## 7. Generación de Reporte Técnico-Experimental

El archivo `outputs/report_data.json` contiene la siguiente infrormación estructurada:

* Contexto y definición del problema.
* Caracterización de los datos.
* Análisis exploratorio.
* Diseño experimental.
* Modelos y métodos utilizados.
* Evaluación y comparación de resultados.
* Análisis crítico, validación y limitaciones.

---

## 8. Consideraciones Académicas

* Se respeta estrictamente la temporalidad de las series de tiempo (anti data leakage).
* El diseño es modular y extensible.
* El módulo de Aprendizaje por Refuerzo se presenta como una prueba de concepto.
* La arquitectura está preparada para futuras extensiones:

  * Multi-activo en RL.
  * Datos intradía.
  * Modelado explícito de costos de transacción y slippage.
  * Funciones de recompensa más sofisticadas.

---

## 9. Autoría

Proyecto desarrollado como parte del **Capstone de Inteligencia Artificial**
**2025 – Semestre 2**

**Integrantes:**

* Consuelo Díaz
* Daniel Alcantar
* José Klarian
* Rafael Guevara
* Rodrigo Erazo