from __future__ import annotations

from typing import Dict, Any

import numpy as np
import pandas as pd


def run_rl_ppo(features: pd.DataFrame, prices: pd.DataFrame, cfg: Dict[str, Any]) -> Dict[str, Any]:
    rl_cfg = cfg.get("rl", {})
    enabled = bool(rl_cfg.get("enabled", False))
    if not enabled:
        return {
            "status": "disabled",
            "models": {},
            "notes": [
                "RL/PPO deshabilitado por config. El módulo queda documentado para el reporte."
            ]
        }

    # Imports opcionales
    try:
        import gymnasium as gym
        from gymnasium import spaces
        from stable_baselines3 import PPO
    except Exception:
        return {
            "status": "skipped",
            "models": {},
            "notes": [
                "Faltan dependencias RL: gymnasium y/o stable-baselines3. "
                "Instalar con: pip install gymnasium stable-baselines3"
            ]
        }

    # Entorno mínimo (1 activo) para demostrar pipeline
    # Nota: Para multi-activo real, extender estado/acción y lógica de portafolio.
    class StockTradingEnv(gym.Env):
        metadata = {"render_modes": []}

        def __init__(self, X: pd.DataFrame, px: pd.Series, lam_vol: float = 0.1):
            super().__init__()
            self.X = X
            self.px = px.loc[X.index]
            self.lam_vol = lam_vol

            self.t = 0
            self.n = len(X)
            self.action_space = spaces.Box(low=-1.0, high=1.0, shape=(1,), dtype=np.float32)

            # Observación: vector features + balance + position
            self.obs_dim = X.shape[1] + 2
            self.observation_space = spaces.Box(low=-np.inf, high=np.inf, shape=(self.obs_dim,), dtype=np.float32)

            self.balance = 1.0
            self.position = 0.0  # fracción invertida

            self.returns = self.px.pct_change().fillna(0.0).values

        def reset(self, seed=None, options=None):
            super().reset(seed=seed)
            self.t = 0
            self.balance = 1.0
            self.position = 0.0
            return self._obs(), {}

        def _obs(self):
            x = self.X.iloc[self.t].values.astype(np.float32)
            return np.concatenate([x, np.array([self.balance, self.position], dtype=np.float32)])

        def step(self, action):
            a = float(np.clip(action[0], -1.0, 1.0))
            # Map: [-1,1] -> [0,1] allocation (long-only simplificado)
            alloc = (a + 1.0) / 2.0

            r = self.returns[self.t]
            # Reward: retorno del portafolio - lambda * |retorno| (proxy volatilidad instantánea)
            port_r = alloc * r
            reward = port_r - self.lam_vol * abs(r)

            self.balance *= (1.0 + port_r)
            self.position = alloc

            self.t += 1
            done = (self.t >= self.n - 1)
            return self._obs(), float(reward), done, False, {}

    # Preparar datos: 1 ticker
    ticker = prices.columns[0]
    px = prices[ticker]
    X = features.copy()

    env = StockTradingEnv(X, px, lam_vol=float(rl_cfg.get("reward_lambda_vol", 0.1)))

    model = PPO("MlpPolicy", env, verbose=0)
    model.learn(total_timesteps=int(rl_cfg.get("timesteps", 100000)))

    # Backtest simple: reconstruir curva
    obs, _ = env.reset()
    vals = [1.0]
    done = False
    while not done:
        action, _ = model.predict(obs, deterministic=True)
        obs, reward, done, _, _ = env.step(action)
        vals.append(env.balance)

    curve = pd.Series(vals, index=[X.index[0]] + list(X.index[:len(vals)-1]), name="PPO")

    return {
        "status": "ok",
        "models": {
            "PPO": {
                "curve": curve,
                "description": "Agente PPO (MlpPolicy) en entorno simplificado 1-activo, reward retorno - lambda*vol."
            }
        },
        "notes": [
            "Este entorno es un MVP conceptual. Para portafolio multi-activo se requiere acción vectorial y costos.",
            "Se recomienda entrenamiento con más pasos y validación walk-forward."
        ]
    }
