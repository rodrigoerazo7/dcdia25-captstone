from __future__ import annotations

from typing import Dict, Any, List

import numpy as np
import pandas as pd


def preprocess_prices(prices: pd.DataFrame, cfg: Dict[str, Any]) -> pd.DataFrame:
    """
    Limpieza básica de precios:
    - Ordenar por fecha
    - Forward-fill por ticker (para alinear calendarios)
    - Eliminar columnas completamente NaN
    - Eliminar filas con NaN si se requiere
    """
    pcfg = cfg.get("preprocessing", {})

    df = prices.copy()
    df = df.sort_index()
    df = df.dropna(axis=1, how="all")

    # forward-fill para alinear días faltantes
    df = df.ffill()

    # opcional: eliminar filas con NaN restantes
    drop_any = bool(pcfg.get("drop_any_nan_rows", True))
    if drop_any:
        df = df.dropna(axis=0, how="any")

    return df


def compute_returns(prices: pd.DataFrame, cfg: Dict[str, Any]) -> pd.DataFrame:
    rcfg = cfg.get("returns", {})
    method = str(rcfg.get("method", "simple")).lower()

    if method == "log":
        rets = np.log(prices).diff().fillna(0.0)
    else:
        rets = prices.pct_change().fillna(0.0)

    rets = rets.replace([np.inf, -np.inf], np.nan).fillna(0.0)
    return rets


def _sma(s: pd.Series, w: int) -> pd.Series:
    return s.rolling(w).mean()


def _ema(s: pd.Series, w: int) -> pd.Series:
    return s.ewm(span=w, adjust=False).mean()


def _rsi(s: pd.Series, w: int) -> pd.Series:
    delta = s.diff()
    gain = delta.clip(lower=0.0).rolling(w).mean()
    loss = (-delta.clip(upper=0.0)).rolling(w).mean()
    rs = gain / loss.replace(0.0, np.nan)
    rsi = 100.0 - (100.0 / (1.0 + rs))
    return rsi


def _bollinger(s: pd.Series, w: int, k: float):
    mid = s.rolling(w).mean()
    std = s.rolling(w).std(ddof=0)
    upper = mid + k * std
    lower = mid - k * std
    bandwidth = (upper - lower) / mid.replace(0.0, np.nan)
    return upper, mid, lower, bandwidth


def build_features(
    prices: pd.DataFrame,
    returns: pd.DataFrame,
    cfg: Dict[str, Any]
) -> pd.DataFrame:
    """
    Construye features por activo y las concatena en un solo DataFrame.
    Compatible con dos esquemas de config:
    - Nuevo: features.bollinger_window, features.bollinger_k
    - Legacy: features.bb_window, features.bb_k
    """
    fcfg = cfg.get("features", {})
    enabled = bool(fcfg.get("enabled", True))
    if not enabled:
        # Si no hay features, devolvemos al menos retornos agregados
        out = pd.DataFrame(index=prices.index)
        out["port_ret_eq"] = returns.mean(axis=1)
        return out

    sma_windows: List[int] = [int(x) for x in fcfg.get("sma_windows", [10, 20, 50])]
    ema_windows: List[int] = [int(x) for x in fcfg.get("ema_windows", [12, 26])]
    rsi_window: int = int(fcfg.get("rsi_window", 14))

    # Compatibilidad: bollinger_window vs bb_window
    if "bb_window" in fcfg:
        bb_w = int(fcfg.get("bb_window", 20))
    else:
        bb_w = int(fcfg.get("bollinger_window", 20))

    if "bb_k" in fcfg:
        bb_k = float(fcfg.get("bb_k", 2.0))
    else:
        bb_k = float(fcfg.get("bollinger_k", 2.0))

    vol_window: int = int(fcfg.get("volatility_window", 20))

    feats = pd.DataFrame(index=prices.index)

    for col in prices.columns:
        s = prices[col].astype(float)

        # Precios y retornos
        feats[f"{col}_close"] = s
        feats[f"{col}_ret"] = returns[col].astype(float)

        # SMA
        for w in sma_windows:
            feats[f"{col}_sma_{w}"] = _sma(s, w)

        # EMA
        for w in ema_windows:
            feats[f"{col}_ema_{w}"] = _ema(s, w)

        # RSI
        feats[f"{col}_rsi_{rsi_window}"] = _rsi(s, rsi_window)

        # Bollinger
        up, mid, low, bw = _bollinger(s, bb_w, bb_k)
        feats[f"{col}_bb_upper_{bb_w}"] = up
        feats[f"{col}_bb_mid_{bb_w}"] = mid
        feats[f"{col}_bb_lower_{bb_w}"] = low
        feats[f"{col}_bb_bw_{bb_w}"] = bw

        # Volatilidad rodante
        feats[f"{col}_vol_{vol_window}"] = returns[col].rolling(vol_window).std(ddof=0)

    # Feature global: retorno EW del portafolio (baseline de señal)
    feats["port_ret_eq"] = returns.mean(axis=1)

    # Limpieza final: NaN por ventanas
    feats = feats.replace([np.inf, -np.inf], np.nan)
    feats = feats.dropna(axis=0, how="any")

    return feats
