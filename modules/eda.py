from __future__ import annotations

import os
from typing import Dict, Any

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def run_eda(
    prices: pd.DataFrame,
    returns: pd.DataFrame,
    features: pd.DataFrame,
    cfg: Dict[str, Any]
) -> Dict[str, Any]:
    figs_dir = cfg["data"]["figures_dir"]
    tables_dir = cfg["data"]["tables_dir"]

    # Tablas
    meta = pd.DataFrame({
        "n_rows_prices": [len(prices)],
        "n_assets": [prices.shape[1]],
        "start": [str(prices.index.min().date())],
        "end": [str(prices.index.max().date())],
        "n_rows_features": [len(features)],
        "n_features": [features.shape[1]]
    })
    meta_path = os.path.join(tables_dir, "eda_meta.csv")
    meta.to_csv(meta_path, index=False)

    ret_stats = returns.describe().T
    ret_stats["skew"] = returns.skew()
    ret_stats["kurt"] = returns.kurtosis()
    ret_stats_path = os.path.join(tables_dir, "eda_returns_stats.csv")
    ret_stats.to_csv(ret_stats_path)

    corr = returns.corr()
    corr_path = os.path.join(tables_dir, "eda_returns_corr.csv")
    corr.to_csv(corr_path)

    # Outliers por z-score
    z = (returns - returns.mean()) / (returns.std(ddof=0) + 1e-12)
    out_rate = (z.abs() > 3).mean().to_frame("outlier_rate_|z|>3")
    out_path = os.path.join(tables_dir, "eda_outliers.csv")
    out_rate.to_csv(out_path)

    # Figuras
    # Precios normalizados
    norm = (prices / prices.iloc[0]) * 100.0
    plt.figure(figsize=(12, 5))
    plt.plot(norm.index, norm.values)
    plt.title("Precios normalizados (Base=100)")
    plt.xlabel("Fecha"); plt.ylabel("Índice"); plt.grid(True)
    fig_prices = os.path.join(figs_dir, "eda_prices_normalized.png")
    plt.tight_layout(); plt.savefig(fig_prices, dpi=140); plt.close()

    # Histograma retorno promedio
    agg = returns.mean(axis=1)
    plt.figure(figsize=(10, 5))
    plt.hist(agg.values, bins=60)
    plt.title("Histograma retorno diario promedio (cross-assets)")
    plt.xlabel("Retorno"); plt.ylabel("Frecuencia"); plt.grid(True)
    fig_hist = os.path.join(figs_dir, "eda_returns_hist.png")
    plt.tight_layout(); plt.savefig(fig_hist, dpi=140); plt.close()

    # Correlación
    plt.figure(figsize=(7, 6))
    plt.imshow(corr.values, aspect="auto")
    plt.title("Matriz de correlación (retornos)")
    plt.xticks(range(len(corr.columns)), corr.columns, rotation=45, ha="right")
    plt.yticks(range(len(corr.index)), corr.index)
    plt.colorbar()
    fig_corr = os.path.join(figs_dir, "eda_corr_matrix.png")
    plt.tight_layout(); plt.savefig(fig_corr, dpi=140); plt.close()

    return {
        "tables": {
            "meta": meta_path,
            "returns_stats": ret_stats_path,
            "returns_corr": corr_path,
            "outliers": out_path
        },
        "figures": {
            "prices_normalized": fig_prices,
            "returns_hist": fig_hist,
            "corr_matrix": fig_corr
        },
        "notes": [
            "EDA incluye estadísticos de retornos, correlación y outliers via z-score.",
            "Posibles sesgos: survivorship bias, data-source bias (yfinance), cambios de régimen."
        ]
    }
