"""ML-based anomaly detection for security metrics."""

from __future__ import annotations

from datetime import datetime
from typing import Any

import numpy as np

from enterprise_types import CONSTANT_3, SecurityEvent


class AnomalyDetector:
    """ML-based anomaly detection for security events."""

    def __init__(self, config: dict[str, Any]):
        self.config = config
        self.baseline_data: list[dict[str, Any]] = []
        self.anomaly_threshold = config.get("anomaly_threshold", 2.0)
        self.window_size = config.get("window_size", 100)

    def collect_baseline(self, metrics: list[dict[str, Any]]) -> None:
        self.baseline_data.extend(metrics)
        if len(self.baseline_data) > self.window_size * 10:
            self.baseline_data = self.baseline_data[-self.window_size * 10 :]

    def detect_anomalies(self, current_metrics: list[dict[str, Any]]) -> list[SecurityEvent]:
        anomalies: list[SecurityEvent] = []
        if len(self.baseline_data) < self.window_size:
            return anomalies

        baseline_response_times = [m.get("response_time", 0) for m in self.baseline_data]
        baseline_error_rates = [m.get("error_rate", 0) for m in self.baseline_data]
        baseline_mean_rt = np.mean(baseline_response_times)
        baseline_std_rt = np.std(baseline_response_times)
        baseline_mean_er = np.mean(baseline_error_rates)
        baseline_std_er = np.std(baseline_error_rates)

        for metric in current_metrics:
            response_time = metric.get("response_time", 0)
            error_rate = metric.get("error_rate", 0)

            if baseline_std_rt > 0:
                z_score_rt = abs(response_time - baseline_mean_rt) / baseline_std_rt
                if z_score_rt > self.anomaly_threshold:
                    anomalies.append(
                        SecurityEvent(
                            timestamp=datetime.now(),
                            event_type="response_time_anomaly",
                            severity="medium" if z_score_rt < CONSTANT_3 else "high",
                            source="anomaly_detector",
                            details={
                                "response_time": response_time,
                                "baseline_mean": baseline_mean_rt,
                                "z_score": z_score_rt,
                                "threshold": self.anomaly_threshold,
                            },
                            confidence=min(z_score_rt / self.anomaly_threshold, 1.0),
                            remediation="Investigate server performance and potential DoS attacks",
                        ),
                    )

            if baseline_std_er > 0:
                z_score_er = abs(error_rate - baseline_mean_er) / baseline_std_er
                if z_score_er > self.anomaly_threshold:
                    anomalies.append(
                        SecurityEvent(
                            timestamp=datetime.now(),
                            event_type="error_rate_anomaly",
                            severity="high" if error_rate > 0.1 else "medium",
                            source="anomaly_detector",
                            details={
                                "error_rate": error_rate,
                                "baseline_mean": baseline_mean_er,
                                "z_score": z_score_er,
                                "threshold": self.anomaly_threshold,
                            },
                            confidence=min(z_score_er / self.anomaly_threshold, 1.0),
                            remediation="Check application logs for errors and potential security incidents",
                        ),
                    )

        return anomalies
