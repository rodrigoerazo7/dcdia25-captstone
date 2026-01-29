# utils/run_utils.py
from __future__ import annotations

import csv
import json
import os
import re
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List


@dataclass(frozen=True)
class RunMeta:
    timestamp: str
    tag: str
    output_dir: str
    figures_dir: str
    tables_dir: str


def safe_slug(s: str, max_len: int = 48) -> str:
    s = (s or "").strip()
    s = re.sub(r"\s+", "-", s)
    s = re.sub(r"[^A-Za-z0-9._-]+", "", s)
    s = s.strip("-_.")
    return s[:max_len]


def derive_run_tag(cfg: Dict[str, Any]) -> str:
    # 1) tag explícito en cfg.run.tag
    tag = ""
    run_cfg = cfg.get("run")
    if isinstance(run_cfg, dict):
        tag = run_cfg.get("tag", "") or ""
    tag = safe_slug(tag, max_len=60)
    if tag:
        return tag

    # 2) fallback: tickers + rango temporal
    tickers = cfg.get("data", {}).get("tickers", [])
    if isinstance(tickers, str):
        tickers = [tickers]
    tickers_part = safe_slug("_".join(list(tickers)[:4]), max_len=40) or "run"
    start = safe_slug(str(cfg.get("data", {}).get("start_date", "")), max_len=12)
    end = safe_slug(str(cfg.get("data", {}).get("end_date", "")), max_len=12)
    return safe_slug(f"{tickers_part}_{start}_{end}", max_len=60)


def apply_timestamped_outputs(cfg: Dict[str, Any]) -> RunMeta:
    """
    Modifica cfg EN MEMORIA para que outputs/figures/tables queden versionados.
    No escribe config.yaml.
    """
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    tag = derive_run_tag(cfg)

    base = f"outputs-{ts}"
    if tag:
        base = f"{base}-{tag}"

    figures = os.path.join(base, "figures")
    tables = os.path.join(base, "tables")

    cfg.setdefault("data", {})
    cfg["data"]["outputs_dir"] = base
    cfg["data"]["figures_dir"] = figures
    cfg["data"]["tables_dir"] = tables

    return RunMeta(
        timestamp=ts,
        tag=tag,
        output_dir=base,
        figures_dir=figures,
        tables_dir=tables,
    )


def inject_run_metadata(report_payload: Dict[str, Any], meta: RunMeta) -> Dict[str, Any]:
    report_payload.setdefault("run_metadata", {})
    report_payload["run_metadata"].update(
        {
            "timestamp": meta.timestamp,
            "tag": meta.tag,
            "output_dir": meta.output_dir,
            "figures_dir": meta.figures_dir,
            "tables_dir": meta.tables_dir,
        }
    )
    return report_payload


def _as_list(x) -> List[str]:
    if x is None:
        return []
    if isinstance(x, str):
        return [x]
    if isinstance(x, list):
        return [str(i) for i in x]
    return [str(x)]


def append_run_index(meta: RunMeta, cfg: Dict[str, Any], report_path: str) -> None:
    """
    Registra los datos de cada proceso en:
    - runs_index.csv
    - runs_index.jsonl
    """
    tickers = _as_list(cfg.get("data", {}).get("tickers", []))

    row = {
        "timestamp": meta.timestamp,
        "tag": meta.tag,
        "output_dir": meta.output_dir,
        "report_path": report_path,
        "tickers": ",".join(tickers),
        "start_date": str(cfg.get("data", {}).get("start_date", "")),
        "end_date": str(cfg.get("data", {}).get("end_date", "")),
        "forecasting_enabled": bool(cfg.get("forecasting", {}).get("enabled", True)),
        "optimization_enabled": bool(cfg.get("optimization", {}).get("enabled", True)),
        "rl_enabled": bool(cfg.get("rl", {}).get("enabled", False)),
    }

    csv_path = "runs_index.csv"
    write_header = not os.path.exists(csv_path)
    with open(csv_path, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(row.keys()))
        if write_header:
            w.writeheader()
        w.writerow(row)

    jsonl_path = "runs_index.jsonl"
    with open(jsonl_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
