"""
forecasting.py
Módulo de forecasting estocástico para retornos financieros.

Implementa:
- SARIMA / SARIMAX (statsmodels)
- Frecuencia mensual
- Estacionalidad anual (12)
- Salida: vector de retornos esperados (mu) por activo

El objetivo no es predecir precios exactos, sino generar expectativas
forward-looking que alimenten el módulo de optimización (MVO) y el reporte.
"""

from __future__ import annotations

import warnings
from typing import Dict, Any

import pandas as pd
from statsmodels.tsa.statespace.sarimax import SARIMAX

warnings.filterwarnings("ignore")


def _fit_sarima(
    series: pd.Series,
    order: tuple[int, int, int],
    seasonal_order: tuple[int, int, int, int],
):
    """
    Ajusta un modelo SARIMAX a una serie univariada de retornos.
    """
    model = SARIMAX(
        series,
        order=order,
        seasonal_order=seasonal_order,
        trend="c",
        enforce_stationarity=False,
        enforce_invertibility=False,
    )
    return model.fit(disp=False)


def run_forecasting_sarima(
    prices: pd.DataFrame,
    cfg: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Ejecuta forecasting SARIMA/SARIMAX para cada activo.

    Parameters
    ----------
    prices : pd.DataFrame
        DataFrame de precios (index temporal, columnas = activos).
    cfg : Dict[str, Any]
        Configuración global cargada desde config.yaml.

    Returns
    -------
    Dict[str, Any]
        Diccionario con forecasts, diagnósticos y notas metodológicas.
    """

    # Configuración (robusta a claves faltantes)
    fcfg = cfg.get("forecasting", {})

    enabled = bool(fcfg.get("enabled", True))
    order = tuple(fcfg.get("order", [1, 1, 1]))
    seasonal_order = tuple(fcfg.get("seasonal_order", [1, 1, 1, 12]))
    horizon = int(fcfg.get("horizon", 1))

    if not enabled:
        return {
            "status": "disabled",
            "forecasts_mu": {},
            "diagnostics": {},
            "notes": ["Módulo de forecasting deshabilitado por configuración."],
        }

    forecasts_mu: Dict[str, float] = {}
    diagnostics: Dict[str, Dict[str, Any]] = {}

    # Loop por activo
    for ticker in prices.columns:
        px = prices[ticker].copy()

        # Remuestreo mensual (fin de mes)
        px_m = px.resample("MS").last()

        # Retornos simples mensuales
        rets_m = px_m.pct_change().dropna()

        # Control mínimo de tamaño de muestra
        if len(rets_m) < 36:
            forecasts_mu[ticker] = None
            diagnostics[ticker] = {
                "status": "skipped",
                "reason": "Serie demasiado corta para estimar SARIMA",
            }
            continue

        try:
            model_fit = _fit_sarima(
                rets_m,
                order=order,
                seasonal_order=seasonal_order,
            )

            # Forecast (one-step o multi-step)
            forecast = model_fit.forecast(steps=horizon)

            # Usamos el promedio del horizonte como mu esperado
            mu_hat = float(forecast.mean())

            diagnostics[ticker] = {
                "status": "ok",
                "mu_forecast": mu_hat,
                "hist_mean": float(rets_m.mean()),
                "hist_std": float(rets_m.std(ddof=0)),
                "order": order,
                "seasonal_order": seasonal_order,
                "aic": float(model_fit.aic),
            }

            forecasts_mu[ticker] = mu_hat

        except Exception as e:
            forecasts_mu[ticker] = None
            diagnostics[ticker] = {
                "status": "error",
                "error": str(e),
            }

    # Salida estandarizada para el pipeline y el reporte
    return {
        "status": "ok",
        "forecasts_mu": forecasts_mu,
        "diagnostics": diagnostics,
        "notes": [
            "Forecasting realizado sobre retornos mensuales (no precios).",
            "Modelo SARIMA con estacionalidad anual (12).",
            "La salida corresponde a expectativas de retorno (mu) para optimización.",
            "Resultados sensibles a cambios de régimen y shocks exógenos.",
        ],
    }
