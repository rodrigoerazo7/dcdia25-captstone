from __future__ import annotations

import json
import os
os.environ["MPLBACKEND"] = "Agg"

from typing import Dict, Any, List

import pandas as pd

from utils.run_utils import apply_timestamped_outputs, inject_run_metadata, append_run_index
from modules.data_ingestion import load_config, fetch_prices_with_cache
from modules.preprocessing import preprocess_prices, compute_returns, build_features
from modules.eda import run_eda
from modules.forecasting import run_forecasting_sarima
from modules.optimization import run_mvo_optimization
from modules.rl_agent import run_rl_ppo
from modules.evaluation import (
    run_baselines,
    evaluate_portfolio_curves,
    compare_models_table,
    build_report_payload
)


def ensure_dirs_global(cfg: Dict[str, Any]) -> None:
    # Directorios globales (cache). En modo multi-portafolios los procesados se guardan por portafolio.
    os.makedirs(cfg["data"]["cache_dir"], exist_ok=True)


def ensure_dirs_portfolio(cfg: Dict[str, Any]) -> None:
    # Directorios por portafolio (salidas y procesados dentro del output del portafolio)
    os.makedirs(cfg["data"]["outputs_dir"], exist_ok=True)
    os.makedirs(cfg["data"]["processed_dir"], exist_ok=True)
    os.makedirs(cfg["data"]["figures_dir"], exist_ok=True)
    os.makedirs(cfg["data"]["tables_dir"], exist_ok=True)


def get_portfolios(cfg: Dict[str, Any]) -> List[Dict[str, Any]]:
    portfolios = cfg.get("portfolios", [])
    if isinstance(portfolios, list) and len(portfolios) > 0:
        return portfolios

    # Fallback: un único portafolio usando data.tickers
    return [{"name": "DEFAULT", "tickers": cfg.get("data", {}).get("tickers", [])}]


def main() -> None:
    # 0) Config + setup de la instancia (proceso actual) (timestamp + tag + outputs)
    cfg = load_config("config.yaml")
    run_meta = apply_timestamped_outputs(cfg)
    ensure_dirs_global(cfg)

    base_output = cfg["data"]["outputs_dir"]
    portfolios_root = os.path.join("portfolios", base_output)
    os.makedirs(portfolios_root, exist_ok=True)

    portfolios = get_portfolios(cfg)
    portfolio_summaries: List[Dict[str, Any]] = []

    # 1) Loop de portafolios (cada portafolio genera su propio output auditable)
    for p in portfolios:
        pname = str(p.get("name", "PORTFOLIO")).strip()
        ptickers = p.get("tickers", [])

        if isinstance(ptickers, str):
            ptickers = [ptickers]

        if not ptickers:
            print(f"[WARN] Portafolio {pname} no tiene tickers. Se omite.")
            continue

        # 1.1) Configurar tickers del portafolio actual
        cfg["data"]["tickers"] = ptickers

        # 1.2) Redirigir outputs a subcarpeta del portafolio
        port_out = os.path.join(portfolios_root, pname)

        cfg["data"]["outputs_dir"] = port_out
        cfg["data"]["processed_dir"] = os.path.join(port_out, "processed")  # procesados por portafolio
        cfg["data"]["figures_dir"] = os.path.join(port_out, "figures")
        cfg["data"]["tables_dir"] = os.path.join(port_out, "tables")

        ensure_dirs_portfolio(cfg)

        # 2) Datos
        prices = fetch_prices_with_cache(cfg)
        prices_clean = preprocess_prices(prices, cfg)
        returns = compute_returns(prices_clean, cfg)

        # 3) Features (para RL y EDA enriquecido)
        features_df = build_features(prices_clean, returns, cfg)

        # Guardar datos procesados (por portafolio)
        prices_path = os.path.join(cfg["data"]["processed_dir"], "prices_clean.csv")
        returns_path = os.path.join(cfg["data"]["processed_dir"], "returns.csv")
        feats_path = os.path.join(cfg["data"]["processed_dir"], "features.csv")
        prices_clean.to_csv(prices_path)
        returns.to_csv(returns_path)
        features_df.to_csv(feats_path)

        # 4) EDA
        eda_outputs = run_eda(prices_clean, returns, features_df, cfg)

        # 5) Forecasting (SARIMA/SARIMAX mensual)
        forecast_outputs = run_forecasting_sarima(prices_clean, cfg)

        # 6) Optimización (MVO)
        opt_outputs = run_mvo_optimization(returns, forecast_outputs, cfg)

        # 7) Baselines + RL
        baseline_outputs = run_baselines(prices_clean, returns, cfg)
        rl_outputs = run_rl_ppo(features_df, prices_clean, cfg)  # puede quedar como skipped

        # 8) Evaluación comparativa (curvas + métricas)
        all_models = {}
        all_models.update(baseline_outputs.get("models", {}))
        all_models.update(opt_outputs.get("models", {}))
        all_models.update(rl_outputs.get("models", {}))

        metrics = evaluate_portfolio_curves(all_models, cfg)
        comparison = compare_models_table(metrics)

        # Persistir tablas (por portafolio)
        comparison_path = os.path.join(cfg["data"]["tables_dir"], "model_comparison.csv")
        comparison.to_csv(comparison_path, index=True)

        # 9) Report payload JSON (por portafolio)
        report_payload = build_report_payload(
            cfg=cfg,
            prices=prices_clean,
            returns=returns,
            features=features_df,
            eda=eda_outputs,
            forecasting=forecast_outputs,
            optimization=opt_outputs,
            baselines=baseline_outputs,
            rl=rl_outputs,
            metrics=metrics,
            comparison_table_path=comparison_path
        )

        # 9.1) Metadata del portafolio 
        report_payload.setdefault("portfolio_metadata", {})
        report_payload["portfolio_metadata"].update({
            "name": pname,
            "tickers": ptickers
        })

        # 10) Inyecta metadata del proceso y guarda reporte (por portafolio)
        report_payload = inject_run_metadata(report_payload, run_meta)

        report_path = os.path.join(cfg["data"]["outputs_dir"], "report_data.json")
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report_payload, f, ensure_ascii=False, indent=2)

        # 10.1) Resumen por portafolio para el índice global 
        best_model = ""
        if isinstance(comparison, pd.DataFrame) and len(comparison) > 0:
            best_model = str(comparison.index[0])

        portfolio_summaries.append({
            "portfolio": pname,
            "tickers": ",".join([str(t) for t in ptickers]),
            "output_dir": port_out,
            "report_path": report_path,
            "comparison_table": comparison_path,
            "best_model": best_model
        })

        print(f"[OK] Portafolio: {pname}")
        print(f"     Output: {port_out}")
        print(f"     Report JSON: {report_path}")
        print(f"     Tabla comparación: {comparison_path}")
        print(f"     Figuras: {cfg['data']['figures_dir']}")

    # 11) Resumen global del run (consolidado de portafolios)
    summary_df = pd.DataFrame(portfolio_summaries)
    summary_root = os.path.join("portfolios", base_output)
    os.makedirs(summary_root, exist_ok=True)

    summary_path = os.path.join(summary_root, "portfolios_summary.csv")
    summary_df.to_csv(summary_path, index=False)

    # 12) Registrar índice del run (una fila por run)
    append_run_index(run_meta, cfg, summary_path)

    print("Pipeline completado.")
    print(f"Instancia (run): {base_output}")
    print("Resumen portafolios:", summary_path)


if __name__ == "__main__":
    main()
