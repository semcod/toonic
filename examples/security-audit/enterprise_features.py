#!/usr/bin/env python3
"""
Enterprise Security Features for obywatel.bielik.ai

Advanced security monitoring with ML-based anomaly detection,
threat intelligence integration, and compliance automation.

Usage:
    python3 enterprise_features.py --config enterprise_config.yaml
"""

from __future__ import annotations

import asyncio
import logging

from enterprise_anomaly import AnomalyDetector
from enterprise_compliance import ComplianceManager
from enterprise_monitor import EnterpriseSecurityMonitor
from enterprise_threat_intel import ThreatIntelligenceManager
from enterprise_types import (
    CONSTANT_3,
    CONSTANT_50,
    ComplianceCheck,
    SecurityEvent,
    ThreatIntelligence,
)

__all__ = [
    "AnomalyDetector",
    "ComplianceCheck",
    "ComplianceManager",
    "EnterpriseSecurityMonitor",
    "SecurityEvent",
    "ThreatIntelligence",
    "ThreatIntelligenceManager",
]


async def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Enterprise Security Monitoring")
    parser.add_argument("--config", default="enterprise_config.yaml", help="Configuration file")
    parser.add_argument("--output", help="Output directory for reports")
    args = parser.parse_args()

    monitor = EnterpriseSecurityMonitor(args.config)
    results = await monitor.run_enterprise_analysis()

    print("\n🔒 Enterprise Security Analysis Results")
    print("=" * CONSTANT_50)
    print(f"Security Score: {results['summary']['security_score']:.1f}/100")
    print(f"Compliance Score: {results['summary']['compliance_score']:.1f}/100")
    print(f"Total Events: {results['summary']['total_events']}")
    print(f"Anomalies: {results['summary']['anomaly_count']}")
    print(f"Threat Indicators: {results['summary']['threat_count']}")

    if results["summary"]["total_events"] > 0:
        print("\n🚨 Security Events Detected:")
        for event in results["anomalies"][:CONSTANT_3]:
            print(f"  • {event['event_type']}: {event['severity']} severity")
        for event in results["threat_events"][:CONSTANT_3]:
            print(f"  • {event['event_type']}: {event['severity']} severity")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    asyncio.run(main())
