"""Represents a DataDog Monitor
"""
from dataclasses import dataclass, field
from typing import Optional

from flask_datadog.generator import endpoint_util
from flask_datadog.shared.ddog_constants import MonitorSpec, MonitorType, ThresholdType


class DatadogMonitorFormatException(Exception):
    pass


@dataclass(frozen=True)
class AlertThresholds:
    critical_threshold: float
    critical_recovery: Optional[float] = None
    warning_threshold: Optional[float] = None
    warning_recovery: Optional[float] = None


@dataclass(frozen=True)
class DatadogMonitor:

    endpoint_path: str
    method: str
    monitor_type: MonitorType
    mon_spec: dict

    @property
    def alert_period(self) -> str:
        if not MonitorSpec.ALERT_PERIOD in self.mon_spec:
            raise DatadogMonitorFormatException(f'{MonitorSpec.ALERT_PERIOD} required')
        return self.mon_spec[MonitorSpec.ALERT_PERIOD]

    @property
    def name(self) -> str:
        cleaned_endpoint_path: str = endpoint_util.clean_endpoint_for_naming(
            self.endpoint_path,
        )
        return f'{self.method}_{cleaned_endpoint_path}-{self.monitor_type.name}'

    @property
    def resource_name(self) -> str:
        """Datadog format resource name.

        Used for tagging a monitor.
        """
        return f'{self.method}_{self.endpoint_path}'.lower()

    def get_alert_thresholds(self) -> AlertThresholds:
        """Alert thresholds with defaults
        """
        critical_threshold: float = self.mon_spec.get(ThresholdType.CRITICAL_THRESHOLD, None)
        critical_recovery: float = self.mon_spec.get(ThresholdType.CRITICAL_RECOVERY, None)
        warning_threshold: float = self.mon_spec.get(ThresholdType.WARNING_THRESHOLD, None)
        warning_recovery: float = self.mon_spec.get(ThresholdType.WARNING_RECOVERY, None)

        if all(x is None for x in [
            critical_recovery,
            critical_threshold,
            warning_recovery,
            warning_threshold]
            ):
            critical_threshold = .1
            critical_recovery = .08
            warning_threshold = .05
            warning_recovery = .03

        return AlertThresholds(
            critical_threshold=critical_threshold,
            critical_recovery=critical_recovery,
            warning_threshold=warning_threshold,
            warning_recovery=warning_recovery,
        )

