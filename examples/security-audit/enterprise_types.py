"""Shared types and constants for enterprise security monitoring."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any

CONSTANT_3 = 3
CONSTANT_20 = 20
CONSTANT_30 = 30
CONSTANT_40 = 40
CONSTANT_50 = 50
CONSTANT_128 = 128
CONSTANT_400 = 400

logger = logging.getLogger(__name__)


@dataclass
class SecurityEvent:
    """Security event data structure."""

    timestamp: datetime
    event_type: str
    severity: str
    source: str
    details: dict[str, Any]
    confidence: float
    remediation: str | None = None


@dataclass
class ThreatIntelligence:
    """Threat intelligence data structure."""

    indicator: str
    indicator_type: str
    threat_type: str
    confidence: float
    source: str
    first_seen: datetime
    last_seen: datetime
    tags: list[str]


@dataclass
class ComplianceCheck:
    """Compliance check result."""

    standard: str
    control: str
    status: str
    evidence: list[str]
    risk_level: str
    remediation: str
