from __future__ import annotations

from typing import Optional


class DriftDetector:
    def __init__(self, z_threshold: float = 2.0, min_samples: int = 10):
        self._history: dict[str, list[float]] = {}
        self.z_threshold = z_threshold
        self.min_samples = min_samples

    def observe(self, metric_name: str, value: float) -> None:
        if metric_name not in self._history:
            self._history[metric_name] = []
        self._history[metric_name].append(value)
        if len(self._history[metric_name]) > 200:
            self._history[metric_name] = self._history[metric_name][-200:]

    def is_drifting(self, metric_name: str) -> bool:
        vals = self._history.get(metric_name, [])
        if len(vals) < self.min_samples:
            return False
        mean = sum(vals) / len(vals)
        var = sum((v - mean) ** 2 for v in vals) / (len(vals) - 1)
        if var <= 0:
            return False
        std = var ** 0.5
        latest = vals[-1]
        return abs(latest - mean) / std > self.z_threshold

    def drift_score(self, metric_name: str) -> float:
        vals = self._history.get(metric_name, [])
        if len(vals) < self.min_samples:
            return 0.0
        mean = sum(vals) / len(vals)
        var = sum((v - mean) ** 2 for v in vals) / (len(vals) - 1)
        if var <= 0:
            return 0.0
        std = var ** 0.5
        return abs(vals[-1] - mean) / std
