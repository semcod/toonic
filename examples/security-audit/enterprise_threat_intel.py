"""Threat intelligence integration."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from enterprise_types import CONSTANT_30, SecurityEvent, ThreatIntelligence, logger


class ThreatIntelligenceManager:
    """Threat intelligence integration and analysis."""

    def __init__(self, config: dict[str, Any]):
        self.config = config
        self.threat_feeds = config.get("threat_feeds", {})
        self.local_indicators: list[Any] = []

    async def fetch_threat_intelligence(self) -> list[ThreatIntelligence]:
        threats: list[ThreatIntelligence] = []
        for feed_name, feed_config in self.threat_feeds.items():
            try:
                if feed_config.get("enabled", False):
                    feed_threats = await self._fetch_feed(feed_name, feed_config)
                    threats.extend(feed_threats)
            except Exception as exc:
                logger.error("Failed to fetch from threat feed %s: %s", feed_name, exc)
        return threats

    async def _fetch_feed(
        self,
        feed_name: str,
        feed_config: dict[str, Any],
    ) -> list[ThreatIntelligence]:
        del feed_config
        if feed_name == "malware_domains":
            return [
                ThreatIntelligence(
                    indicator="malicious-example.com",
                    indicator_type="domain",
                    threat_type="malware_c2",
                    confidence=0.9,
                    source="malware_domains_feed",
                    first_seen=datetime.now() - timedelta(days=CONSTANT_30),
                    last_seen=datetime.now(),
                    tags=["malware", "c2", "command_and_control"],
                ),
            ]
        return []

    def check_indicators(
        self,
        content: str,
        threats: list[ThreatIntelligence],
    ) -> list[SecurityEvent]:
        events: list[SecurityEvent] = []
        for threat in threats:
            if threat.indicator_type == "domain" and threat.indicator in content:
                events.append(
                    SecurityEvent(
                        timestamp=datetime.now(),
                        event_type="threat_indicator_detected",
                        severity="high" if threat.confidence > 0.8 else "medium",
                        source="threat_intelligence",
                        details={
                            "indicator": threat.indicator,
                            "indicator_type": threat.indicator_type,
                            "threat_type": threat.threat_type,
                            "confidence": threat.confidence,
                            "source": threat.source,
                        },
                        confidence=threat.confidence,
                        remediation=f"Block access to {threat.indicator} and investigate connections",
                    ),
                )
        return events
