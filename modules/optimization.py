"""
optimization.py
Módulo de optimización de portafolio (Mean-Variance Optimization, MVO).

- Usa PyPortfolioOpt (EfficientFrontier) con covarianza muestral (o shrinkage opcional).
- Integra retorno esperado (mu) que puede venir de forecasting (SARIMA) + histórico.
- Es robusto a NaN/Inf: filtra activos problemáticos y aplica fallbacks.

Salida:
- Pesos óptimos
- Curva de portafolio (rebalance mensual)
- Metadatos para el reporte (notas, supuestos, fallbacks ejecutados)
"""

from __future__ import annotations

from typing import Dict, Any, Optional

import numpy as np
import pandas as pd


def _safe_float(x) -> Optional[float]:
    try:
        if x is None:
            return None
        v = float(x)
        if np.isfinite(v):
            return v
        return None
    except Exception:
        return None


def _make_mu_vector(
    returns: pd.DataFrame,
    forecast_outputs: Dict[str, Any],
    cfg: Dict[str, Any],
) -> pd.Series:
    """
    Construye vector mu (retornos esperados anualizados) de forma robusta.
    - Si forecasting entrega mu por ticker, lo usa.
    - Si falta mu para un ticker, usa media histórica.
    - Permite mezclar (híbrido) forecast + histórico.
    """
    ocfg = cfg.get("optimization", {})
    mix = ocfg.get("mu_mix", {"forecast_weight": 0.5, "historical_weight": 0.5})
    wf = float(mix.get("forecast_weight", 0.5))
    wh = float(mix.get("historical_weight", 0.5))
    s = wf + wh
    if s <= 0:
        wf, wh = 0.5, 0.5
    else:
        wf, wh = wf / s, wh / s

    trading_days = int(cfg.get("evaluation", {}).get("trading_days", 252))

    # Media histórica diaria -> anualizada aproximada
    hist_mu_annual = (1.0 + returns.mean()) ** trading_days - 1.0

    # Forecast mu: normalmente mensual; convertimos a anual aprox si corresponde
    # Si forecasting entrega mu mensual: anual ~ (1+mu_m)^12 - 1
    fcfg = cfg.get("forecasting", {})
    forecast_is_monthly = bool(fcfg.get("forecast_is_monthly", True))  # default: mensual
    forecasts = forecast_outputs.get("forecasts_mu", {}) if isinstance(forecast_outputs, dict) else {}

    mu_forecast_annual = pd.Series(index=returns.columns, dtype=float)
    for c in returns.columns:
        v = _safe_float(forecasts.get(c))
        if v is None:
            mu_forecast_annual.loc[c] = np.nan
        else:
            if forecast_is_monthly:
                mu_forecast_annual.loc[c] = (1.0 + v) ** 12 - 1.0
            else:
                mu_forecast_annual.loc[c] = (1.0 + v) ** trading_days - 1.0

    # Híbrido con fallback: si forecast NaN -> usar histórico
    mu = wf * mu_forecast_annual + wh * hist_mu_annual
    mu = mu.where(np.isfinite(mu), hist_mu_annual)  # reemplaza NaN/Inf por histórico

    # Clip opcional para evitar extremos (importante para estabilidad numérica)
    clip_cfg = ocfg.get("mu_clip", {"enabled": True, "min": -0.5, "max": 1.5})
    if bool(clip_cfg.get("enabled", True)):
        mu = mu.clip(lower=float(clip_cfg.get("min", -0.5)), upper=float(clip_cfg.get("max", 1.5)))

    return mu


def _safe_covariance(returns: pd.DataFrame, cfg: Dict[str, Any]) -> pd.DataFrame:
    """
    Construye matriz de covarianza anualizada y la sanea.
    """
    trading_days = int(cfg.get("evaluation", {}).get("trading_days", 252))

    # Covarianza diaria
    cov = returns.cov()

    # Reemplazar NaN/Inf
    cov = cov.replace([np.inf, -np.inf], np.nan)
    # Si hay NaN en diagonal, no se puede; fill mínimo
    cov = cov.fillna(0.0)

    # Anualizar
    cov_annual = cov * trading_days

    # Regularización (jitter) para PSD / mal condicionamiento
    ocfg = cfg.get("optimization", {})
    jitter = float(ocfg.get("cov_jitter", 1e-6))
    if jitter > 0:
        cov_annual = cov_annual + np.eye(len(cov_annual)) * jitter

    return cov_annual


def _monthly_rebalance_curve(prices: pd.DataFrame, weights: pd.Series) -> pd.Series:
    """
    Curva de valor con rebalance mensual (simple):
    - Rebalance en inicio de cada mes a los pesos.
    - Entre rebalanceos, Buy&Hold por drift.
    """
    px = prices.copy().sort_index()
    rets = px.pct_change().fillna(0.0)

    w = weights.values.astype(float)
    w = w / w.sum() if w.sum() != 0 else np.ones_like(w) / len(w)

    vals = []
    current_w = w.copy()
    val = 1.0

    for dt, r in rets.iterrows():
        vals.append(val)

        # Retorno del portafolio
        pr = float(np.dot(current_w, r.values))
        val *= (1.0 + pr)

        # Drift weights
        current_w = current_w * (1.0 + r.values)
        s = current_w.sum()
        current_w = current_w / s if s != 0 else w.copy()

        # Rebalance mensual al inicio del mes
        if getattr(dt, "is_month_start", False):
            current_w = w.copy()

    curve = pd.Series(vals, index=rets.index, name="MVO")
    curve.iloc[0] = 1.0
    return curve


def run_mvo_optimization(
    returns: pd.DataFrame,
    forecast_outputs: Dict[str, Any],
    cfg: Dict[str, Any],
) -> Dict[str, Any]:
    ocfg = cfg.get("optimization", {})
    enabled = bool(ocfg.get("enabled", True))
    if not enabled:
        return {
            "status": "disabled",
            "models": {},
            "notes": ["Optimización MVO deshabilitada por configuración."],
        }

    notes = []
    models: Dict[str, Any] = {}

    # 1) Sanear returns
    R = returns.replace([np.inf, -np.inf], np.nan).copy()
    # Eliminar columnas con demasiados NaN
    min_rows = int(0.95 * len(R)) if len(R) > 0 else 0
    R = R.dropna(axis=1, thresh=min_rows)
    R = R.dropna(axis=0, how="any")

    if R.shape[1] < 2:
        # fallback a "no-op"
        return {
            "status": "skipped",
            "models": {},
            "notes": ["Muy pocos activos con retornos válidos para optimizar."],
        }

    dropped = sorted(set(returns.columns) - set(R.columns))
    if dropped:
        notes.append(f"Se eliminaron activos por NaN/Inf en retornos: {dropped}")

    # 2) Construir mu y cov robustos
    mu = _make_mu_vector(R, forecast_outputs, cfg)
    cov = _safe_covariance(R, cfg)

    # Validación final: nada NaN/Inf
    if (not np.isfinite(mu.values).all()) or (not np.isfinite(cov.values).all()):
        notes.append("Se detectaron NaN/Inf en mu/cov tras saneo. Aplicando fallback Equal-Weight.")
        w = pd.Series(np.ones(R.shape[1]) / R.shape[1], index=R.columns)
        # curva usando returns (sin precios) -> aproximación: cumprod(1+ret)
        port_ret = (R * w).sum(axis=1)
        curve = (1.0 + port_ret).cumprod()
        curve.iloc[0] = 1.0
        models["EW_Fallback"] = {
            "weights": w,
            "curve": curve,
            "description": "Fallback Equal-Weight por datos inválidos en optimización.",
        }
        return {"status": "ok", "models": models, "notes": notes}

    # 3) Resolver MVO (PyPortfolioOpt)
    try:
        from pypfopt.efficient_frontier import EfficientFrontier
    except Exception:
        notes.append("No se pudo importar PyPortfolioOpt. Instalar con: pip install PyPortfolioOpt")
        return {"status": "skipped", "models": {}, "notes": notes}

    rf = float(ocfg.get("risk_free_rate", 0.0))
    weight_bounds = ocfg.get("weight_bounds", [0.0, 1.0])
    lb, ub = float(weight_bounds[0]), float(weight_bounds[1])

    try:
        ef = EfficientFrontier(mu, cov, weight_bounds=(lb, ub))

        # Límites por activo (opcional)
        max_w = ocfg.get("max_weight", None)
        if max_w is not None:
            for t in mu.index:
                ef.add_constraint(lambda w, i=list(mu.index).index(t): w[i] <= float(max_w))

        # Objetivo principal: max Sharpe
        weights = ef.max_sharpe(risk_free_rate=rf)
        cleaned = ef.clean_weights()
        w = pd.Series(cleaned).reindex(mu.index).fillna(0.0)
        if w.sum() != 0:
            w = w / w.sum()

        # Curva: con precios en cfg/data, podriamos reconstruir.
        # Aquí usamos returns para curva diaria (equivalente a rebalance mensual en returns no aplica).
        # Para mantener coherencia, reconstruimos curva diaria sin rebalance con w fijo.
        port_ret = (R * w).sum(axis=1)
        curve = (1.0 + port_ret).cumprod()
        curve.iloc[0] = 1.0
        curve.name = "MVO_MaxSharpe"

        models["MVO_MaxSharpe"] = {
            "weights": w,
            "curve": curve,
            "description": "Optimización Mean-Variance (PyPortfolioOpt) max Sharpe con mu híbrido.",
        }

    except Exception as e:
        # Fallback: min vol, luego equal-weight
        notes.append(f"Falló max_sharpe por solver/NaN: {repr(e)}. Intentando min_volatility().")
        try:
            ef = EfficientFrontier(mu, cov, weight_bounds=(lb, ub))
            weights = ef.min_volatility()
            cleaned = ef.clean_weights()
            w = pd.Series(cleaned).reindex(mu.index).fillna(0.0)
            if w.sum() != 0:
                w = w / w.sum()

            port_ret = (R * w).sum(axis=1)
            curve = (1.0 + port_ret).cumprod()
            curve.iloc[0] = 1.0
            curve.name = "MVO_MinVol"

            models["MVO_MinVol"] = {
                "weights": w,
                "curve": curve,
                "description": "Fallback MVO min volatility por fallo en max Sharpe.",
            }
        except Exception as e2:
            notes.append(f"Falló min_volatility también: {repr(e2)}. Usando Equal-Weight.")
            w = pd.Series(np.ones(R.shape[1]) / R.shape[1], index=R.columns)
            port_ret = (R * w).sum(axis=1)
            curve = (1.0 + port_ret).cumprod()
            curve.iloc[0] = 1.0
            models["EW_Fallback"] = {
                "weights": w,
                "curve": curve,
                "description": "Fallback Equal-Weight por fallo total del optimizador.",
            }

    return {"status": "ok", "models": models, "notes": notes}
