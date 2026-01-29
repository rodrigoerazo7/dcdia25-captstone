from __future__ import annotations

import os
from typing import Dict, Any

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def run_baselines(prices: pd.DataFrame, returns: pd.DataFrame, cfg: Dict[str, Any]) -> Dict[str, Any]:
    """
    Baselines simples para referencia:
    - Buy&Hold del activo/benchmark (por ticker)
    """
    models = {}

    # Buy&Hold: curve = precio normalizado
    for col in prices.columns:
        curve = (prices[col] / prices[col].iloc[0]).rename(f"BuyHold_{col}")
        models[f"BuyHold_{col}"] = {"curve": curve, "description": f"Buy&Hold sobre {col}."}

    return {"status": "ok", "models": models, "notes": ["Baseline Buy&Hold por activo."]}


def _annualize_return(daily_mean: float, trading_days: int) -> float:
    return (1.0 + daily_mean) ** trading_days - 1.0


def _annualize_vol(daily_std: float, trading_days: int) -> float:
    return daily_std * np.sqrt(trading_days)


def _max_drawdown(curve: pd.Series) -> float:
    peak = curve.cummax()
    dd = curve / peak - 1.0
    return float(dd.min())


def evaluate_portfolio_curves(models: Dict[str, Any], cfg: Dict[str, Any]) -> Dict[str, Dict[str, float]]:
    td = int(cfg["evaluation"]["trading_days"])
    rf = float(cfg["evaluation"]["risk_free_annual"])

    out = {}

    for name, payload in models.items():
        curve: pd.Series = payload["curve"].dropna().copy()
        # Convertir a curva de valor (si parte distinta de 1)
        if curve.iloc[0] != 1.0:
            curve = curve / float(curve.iloc[0])

        rets = curve.pct_change().fillna(0.0)
        mu = float(rets.mean())
        sigma = float(rets.std(ddof=0))

        ann_ret = _annualize_return(mu, td)
        ann_vol = _annualize_vol(sigma, td)
        sharpe = (ann_ret - rf) / (ann_vol + 1e-12)

        mdd = _max_drawdown(curve)
        calmar = ann_ret / abs(mdd) if mdd < 0 else np.nan

        out[name] = {
            "total_return": float(curve.iloc[-1] - 1.0),
            "CAGR_approx": float(ann_ret),
            "ann_vol": float(ann_vol),
            "sharpe": float(sharpe),
            "max_drawdown": float(mdd),
            "calmar": float(calmar),
            "final_curve": float(curve.iloc[-1]),
        }

    return out


def compare_models_table(metrics: Dict[str, Dict[str, float]]) -> pd.DataFrame:
    df = pd.DataFrame(metrics).T
    # orden por Sharpe desc
    return df.sort_values("sharpe", ascending=False)


def plot_equity_curves(models: Dict[str, Any], cfg: Dict[str, Any]) -> str:
    figs_dir = cfg["data"]["figures_dir"]
    plt.figure(figsize=(12, 5))
    for name, payload in models.items():
        curve = payload["curve"].dropna().copy()
        if curve.iloc[0] != 1.0:
            curve = curve / float(curve.iloc[0])
        plt.plot(curve.index, curve.values, label=name)

    plt.title("Curvas de valor normalizadas (INR)")
    plt.xlabel("Fecha"); plt.ylabel("Valor (base=1.0)")
    plt.grid(True); plt.legend()

    path = os.path.join(figs_dir, "eval_equity_curves.png")
    plt.tight_layout(); plt.savefig(path, dpi=140); plt.close()
    return path


def build_report_payload(
    cfg: Dict[str, Any],
    prices: pd.DataFrame,
    returns: pd.DataFrame,
    features: pd.DataFrame,
    eda: Dict[str, Any],
    forecasting: Dict[str, Any],
    optimization: Dict[str, Any],
    baselines: Dict[str, Any],
    rl: Dict[str, Any],
    metrics: Dict[str, Dict[str, float]],
    comparison_table_path: str
) -> Dict[str, Any]:
    # Para el reporte: figura resumen de curvas (si hay varios modelos)
    models = {}
    models.update(baselines.get("models", {}))
    models.update(optimization.get("models", {}))
    models.update(rl.get("models", {}))

    equity_fig = plot_equity_curves(models, cfg) if models else None

    # Split temporal (para reportar)
    split = cfg["experimental"]["split"]
    train_start, train_end = split["train_start"], split["train_end"]
    test_start, test_end = split["test_start"], split["test_end"]

    # Información de dataset
    data_summary = {
        "source": cfg.get("data", {}).get("source", "yfinance"),
        "tickers": cfg["data"]["tickers"],
        "start_date": cfg["data"]["start_date"],
        "end_date": cfg["data"]["end_date"],
        "n_rows_prices": int(len(prices)),
        "n_assets": int(prices.shape[1]),
        "n_rows_features": int(len(features)),
        "n_features": int(features.shape[1]),
        "variables_raw_expected": ["Close (auto_adjusted)"],
        "frequency": cfg["data"]["interval"],
    }

    # Contexto / definiciones del problema (plantilla)
    context = {
        "organization": cfg["project"]["organization"],
        "process": cfg["project"]["process"],
        "task_type": ["forecasting", "optimización", "aprendizaje_por_refuerzo"],
        "objective_variables": [
            "Retorno total",
            "CAGR",
            "Ratio de Sharpe",
            "Maximum Drawdown"
        ],
        "predictive_variables": [
            "Retornos históricos",
            "Indicadores técnicos (SMA/EMA/RSI/Bollinger/Volatilidad)",
            "Features normalizadas (para RL)"
        ],
        "assumptions_restrictions": [
            "Separación temporal (anti data leakage).",
            "Datos diarios (no intradía).",
            "Ejecución aproximada a precio de cierre (baseline).",
            "Fuentes gratuitas: posibles inconsistencias (yfinance).",
            "Costos/Slippage simplificados (por defecto 0)."
        ],
        "why_ai": [
            "Mercados no estacionarios y con cambios de régimen.",
            "Necesidad de control secuencial (RL) y adaptación.",
            "Alta dimensionalidad (multi-activo) y restricciones complejas."
        ]
    }

    experimental = {
        "split": split,
        "metrics_used": list(next(iter(metrics.values())).keys()) if metrics else [],
        "baselines": cfg["experimental"]["baselines"],
        "notes": [
            "Split cronológico para evitar fuga de información (time series).",
            "Modelos comparados con métricas de riesgo/retorno."
        ]
    }

    models_info = {
        "forecasting": forecasting,
        "optimization": {
            "status": optimization.get("status"),
            "notes": optimization.get("notes", []),
            "weights": optimization.get("weights", None)
        },
        "rl": {
            "status": rl.get("status"),
            "notes": rl.get("notes", [])
        }
    }

    # Casos éxito/falla (plantillas, ajustar manualmente)
    analysis = {
        "success_cases": [
            "Mejor control de drawdown en periodos de alta volatilidad (si Sharpe/Calmar mejora).",
            "Estabilidad operativa (rebalance mensual vs drift)."
        ],
        "failure_cases": [
            "Forecasting puede fallar bajo cambios de régimen.",
            "Optimización MVO depende de covarianza lineal.",
            "RL puede volverse conservador o inestable si reward está mal diseñado."
        ],
        "error_examples": [
            "Shock de mercado: retorno extremo (outlier) altera estimación de riesgo.",
            "Alta correlación entre activos reduce diversificación efectiva."
        ],
        "impact": [
            "Errores de predicción pueden sesgar mu y sobreponderar sectores.",
            "Errores de ejecución pueden subestimar slippage y turnover real."
        ]
    }

    validation = {
        "generalization_evidence": [
            f"Evaluación out-of-sample en {test_start} → {test_end}.",
            "Análisis por régimen recomendado (bull/bear/high-vol).",
            "Opcional: bootstrap/permutation test sobre retornos."
        ],
        "limitations": [
            "Datos diarios: ceguera a volatilidad intradía.",
            "Sin slippage/impacto de mercado realista por defecto.",
            "Dependencia de Yahoo Finance/yfinance.",
            "RL multi-activo requiere mayor complejidad (acción vectorial)."
        ]
    }

    return {
        "generated_at": str(pd.Timestamp.utcnow()),
        "project": cfg["project"],
        "context": context,
        "data_summary": data_summary,
        "eda": eda,
        "preprocessing": cfg["preprocessing"],
        "features": cfg["features"],
        "experimental_design": experimental,
        "models": models_info,
        "results": {
            "metrics_by_model": metrics,
            "comparison_table_csv": comparison_table_path,
            "equity_curves_figure": equity_fig
        },
        "analysis": analysis,
        "validation": validation
    }
