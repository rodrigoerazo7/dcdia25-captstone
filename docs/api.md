# Portfolio Reports API

API para consultar reportes de optimización de portfolios financieros.

**Base URL:** `https://dcdia25-captstone-archive.vercel.app`

---

## Endpoints

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/portfolios` | Lista todos los portfolios disponibles |
| GET | `/api/reports/latest` | Obtiene el reporte de un portfolio |

---

## GET `/api/portfolios`

Lista todos los portfolios disponibles con sus tickers.

### Request

```
GET /api/portfolios
```

### Response

```json
{
  "status": "ok",
  "run_id": "outputs-20260129-023417-EXP-RL-001",
  "total": 19,
  "portfolios": [
    {
      "name": "FANG",
      "tickers": ["META", "AMZN", "NFLX", "GOOGL"],
      "n_assets": 4,
      "has_report": true
    },
    {
      "name": "MAG7",
      "tickers": ["META", "AAPL", "AMZN", "GOOGL", "MSFT", "NVDA", "TSLA"],
      "n_assets": 7,
      "has_report": true
    }
  ]
}
```

### Ejemplo

```bash
curl "https://dcdia25-captstone-archive.vercel.app/api/portfolios"
```

---

## GET `/api/reports/latest`

Obtiene el reporte más reciente de optimización.

### Parámetros de Query

| Parámetro | Tipo | Requerido | Descripción |
|-----------|------|-----------|-------------|
| `tag` | string | No | Tag del experimento (default: `EXP-RL-001`) |
| `portfolio` | string | No | Filtrar por nombre de portfolio |

### Request

```
GET /api/reports/latest?portfolio=MAG7
```

### Response

```json
{
  "tag": "EXP-RL-001",
  "run_id": "outputs-20260129-023417-EXP-RL-001",
  "latest_run_dir": "portfolios/outputs-20260129-023417-EXP-RL-001",
  "portfolio_filter": "MAG7",
  "summary": [...],
  "portfolios": [
    {
      "portfolio": "MAG7",
      "report": {
        "generated_at": "2026-01-29 05:36:04",
        "project": {...},
        "data_summary": {...},
        "models": {...},
        "results": {...}
      }
    }
  ]
}
```

### Ejemplos

```bash
# Todos los portfolios
curl "https://dcdia25-captstone-archive.vercel.app/api/reports/latest"

# Solo MAG7
curl "https://dcdia25-captstone-archive.vercel.app/api/reports/latest?portfolio=MAG7"

# Solo FANG con tag específico
curl "https://dcdia25-captstone-archive.vercel.app/api/reports/latest?tag=EXP-RL-001&portfolio=FANG"
```

---

## Portfolios Disponibles

| Portfolio | Tickers | Descripción |
|-----------|---------|-------------|
| `FANG` | META, AMZN, NFLX, GOOGL | Big Tech |
| `FAANG` | META, AAPL, AMZN, NFLX, GOOGL | Big Tech + Apple |
| `MAG7` | META, AAPL, AMZN, GOOGL, MSFT, NVDA, TSLA | Magnificent 7 |
| `SP500_TOP10` | AAPL, MSFT, GOOGL, AMZN, NVDA, META, BRK-B, UNH, JNJ, V | Top 10 S&P 500 |
| `DIVERSIFIED_SECTORS` | AAPL, JPM, JNJ, XOM, PG, HD, VZ, NEE, AMT, BLK | Sectores diversificados |
| `DIVIDEND_KINGS` | JNJ, PG, KO, PEP, MMM, EMR, CL, LOW, SWK, ITW | Dividendos |
| `GLOBAL_ETF` | SPY, QQQ, EFA, EEM, VWO, GLD, TLT, VNQ, LQD, HYG | ETFs globales |
| `TECH_SEMICONDUCTORS` | NVDA, AMD, INTC, AVGO, QCOM, TSM, MU, AMAT, LRCX, KLAC | Semiconductores |
| `HEALTHCARE` | JNJ, UNH, PFE, ABBV, MRK, LLY, TMO, ABT, DHR, BMY | Salud |
| `FINANCIALS` | JPM, BAC, WFC, GS, MS, C, BLK, SCHW, AXP, USB | Financieras |
| `CLEAN_ENERGY` | ENPH, SEDG, FSLR, NEE, PLUG, RUN, ICLN, TAN, BEP, CSIQ | Energía limpia |
| `IPSA_TOP10` | COPEC.SN, SQM-B.SN, BSANTANDER.SN, ... | Top 10 IPSA (Chile) |
| `CHILE_RETAIL` | CENCOSUD.SN, FALABELLA.SN, RIPLEY.SN, SMU.SN, FORUS.SN | Retail chileno |
| `CHILE_BANCOS` | BSANTANDER.SN, CHILE.SN, BCI.SN, ITAUCORP.SN, SECURITY.SN | Bancos chilenos |
| `CHILE_COMMODITIES` | SQM-B.SN, COPEC.SN, CMPC.SN, CAP.SN, MOLYMET.SN | Commodities Chile |
| `CHILE_UTILITIES` | ENELAM.SN, ENELCHILE.SN, COLBUN.SN, AGUAS-A.SN, ECL.SN | Utilities Chile |

---

## Estructura del Reporte

### Campos Principales

| Campo | Descripción |
|-------|-------------|
| `generated_at` | Fecha de generación del reporte |
| `project` | Metadatos del proyecto |
| `data_summary` | Resumen de datos (tickers, fechas, observaciones) |
| `eda` | Análisis exploratorio (tablas y figuras) |
| `models` | Resultados de modelos (forecasting, optimization, RL) |
| `results` | Métricas por modelo y comparación |
| `analysis` | Casos de éxito/fallo e impacto |
| `validation` | Evidencia de generalización y limitaciones |

### Métricas de Resultados

| Métrica | Descripción |
|---------|-------------|
| `total_return` | Retorno total del período |
| `CAGR_approx` | Tasa de crecimiento anual compuesta |
| `ann_vol` | Volatilidad anualizada |
| `sharpe` | Ratio de Sharpe |
| `max_drawdown` | Máxima caída desde el pico |
| `calmar` | Ratio Calmar (CAGR / MaxDrawdown) |
| `final_curve` | Valor final de la curva de equity |

### Modelos Comparados

| Modelo | Descripción |
|--------|-------------|
| `BuyHold_{TICKER}` | Estrategia buy & hold por activo individual |
| `MVO_MaxSharpe` | Optimización Mean-Variance (maximiza Sharpe) |
| `PPO` | Agente de Reinforcement Learning |

---

## Códigos de Error

| Código | Descripción |
|--------|-------------|
| `200` | OK - Respuesta exitosa |
| `400` | Bad Request - Parámetros inválidos |
| `404` | Not Found - Portfolio no encontrado |
| `500` | Internal Server Error |

### Ejemplo de Error 404

```json
{
  "error": "Portfolio 'INVALID' not found.",
  "available_portfolios": ["FANG", "FAANG", "MAG7", ...]
}
```

---

## Ejemplos de Código

### Python

```python
import requests

BASE_URL = "https://dcdia25-captstone-archive.vercel.app/api"

# Listar portfolios disponibles
portfolios = requests.get(f"{BASE_URL}/portfolios").json()
print(f"Portfolios disponibles: {portfolios['total']}")

for p in portfolios["portfolios"]:
    print(f"  - {p['name']}: {p['n_assets']} activos")

# Obtener reporte de MAG7
report = requests.get(f"{BASE_URL}/reports/latest", params={"portfolio": "MAG7"}).json()
metrics = report["portfolios"][0]["report"]["results"]["metrics_by_model"]

print("\nMétricas MVO MaxSharpe (MAG7):")
mvo = metrics["MVO_MaxSharpe"]
print(f"  Retorno Total: {mvo['total_return']:.2%}")
print(f"  CAGR: {mvo['CAGR_approx']:.2%}")
print(f"  Sharpe Ratio: {mvo['sharpe']:.2f}")
print(f"  Max Drawdown: {mvo['max_drawdown']:.2%}")
```

### JavaScript

```javascript
const BASE_URL = "https://dcdia25-captstone-archive.vercel.app/api";

// Listar portfolios
async function listPortfolios() {
  const res = await fetch(`${BASE_URL}/portfolios`);
  const data = await res.json();
  console.log(`Portfolios disponibles: ${data.total}`);
  data.portfolios.forEach(p => {
    console.log(`  - ${p.name}: ${p.n_assets} activos`);
  });
}

// Obtener reporte
async function getReport(portfolio) {
  const res = await fetch(`${BASE_URL}/reports/latest?portfolio=${portfolio}`);
  const data = await res.json();
  const metrics = data.portfolios[0].report.results.metrics_by_model;
  
  console.log(`\nMétricas MVO MaxSharpe (${portfolio}):`);
  const mvo = metrics.MVO_MaxSharpe;
  console.log(`  Total Return: ${(mvo.total_return * 100).toFixed(2)}%`);
  console.log(`  Sharpe Ratio: ${mvo.sharpe.toFixed(2)}`);
}

listPortfolios();
getReport("MAG7");
```

### cURL

```bash
# Listar portfolios
curl "https://dcdia25-captstone-archive.vercel.app/api/portfolios"

# Obtener reporte de MAG7
curl "https://dcdia25-captstone-archive.vercel.app/api/reports/latest?portfolio=MAG7"

# Obtener reporte con jq (formato legible)
curl -s "https://dcdia25-captstone-archive.vercel.app/api/reports/latest?portfolio=MAG7" | jq '.portfolios[0].report.results.metrics_by_model'
```

---

## Información del Proyecto

| Campo | Valor |
|-------|-------|
| **Organización** | Universidad de Chile |
| **Curso** | Diplomado Ciencia de Datos e Inteligencia Artificial |
| **Módulo** | 09 |
| **Versión** | v3.1.1 |
| **Run ID** | outputs-20260129-023417-EXP-RL-001 |

---

## Configuración de Vercel

```json
{
  "cleanUrls": true,
  "functions": {
    "api/**/*.js": {
      "includeFiles": "portfolios/outputs-20260129-023417-EXP-RL-001/**"
    }
  }
}
```

---

## Limitaciones

- Datos diarios (sin volatilidad intradía)
- Sin slippage/impacto de mercado realista por defecto
- Dependencia de Yahoo Finance (yfinance)
- RL multi-activo requiere mayor complejidad (acción vectorial)
