from __future__ import annotations

import os
import hashlib
from typing import Dict, Any, List

import pandas as pd

try:
    import yaml
except ImportError as e:
    raise SystemExit("Falta pyyaml. Instalar con: pip install pyyaml") from e

try:
    import yfinance as yf
except ImportError as e:
    raise SystemExit("Falta yfinance. Instalar con: pip install yfinance") from e


def load_config(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    portfolios_file = cfg.get("run", {}).get("portfolios_file")
    if portfolios_file:
        with open(portfolios_file, "r", encoding="utf-8") as f:
            portfolios_cfg = yaml.safe_load(f)

        if "portfolios" not in portfolios_cfg:
            raise ValueError("portfolios.yaml debe contener la clave 'portfolios'")

        cfg["portfolios"] = portfolios_cfg["portfolios"]

    return cfg


def _cache_key(cfg: Dict[str, Any]) -> str:
    d = cfg["data"]
    raw = f"{d['tickers']}_{d['start_date']}_{d['end_date']}_{d['interval']}_{d['auto_adjust']}"
    return hashlib.md5(raw.encode("utf-8")).hexdigest()


def fetch_prices_with_cache(cfg: Dict[str, Any]) -> pd.DataFrame:
    d = cfg["data"]
    cache_dir = d["cache_dir"]
    key = _cache_key(cfg)
    cache_file = os.path.join(cache_dir, f"prices_{key}.parquet")

    if os.path.exists(cache_file):
        prices = pd.read_parquet(cache_file)
        prices.index = pd.to_datetime(prices.index)
        return prices

    tickers: List[str] = d["tickers"]
    data = yf.download(
        tickers=tickers,
        start=d["start_date"],
        end=d["end_date"],
        interval=d["interval"],
        auto_adjust=bool(d["auto_adjust"]),
        progress=False,
        group_by="column"
    )

    if data.empty:
        raise SystemExit("No se pudo descargar data (respuesta de yfinance vacía).")

    # Caso multiindex (varios tickers) vs simple
    if isinstance(data.columns, pd.MultiIndex):
        # Usamos Close ajustado
        if "Close" not in data.columns.get_level_values(0):
            raise SystemExit("No se encontró columna Close en yfinance.")
        prices = data["Close"].copy()
    else:
        if "Close" not in data.columns:
            raise SystemExit("No se encontró columna Close en yfinance.")
        prices = data[["Close"]].copy()
        prices.columns = [tickers[0]]

    prices = prices.sort_index()
    prices.to_parquet(cache_file)
    return prices
