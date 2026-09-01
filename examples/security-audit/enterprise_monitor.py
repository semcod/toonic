"""Enterprise security monitor orchestration."""

from __future__ import annotations

import json
import ssl
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Any

import aiohttp
import yaml

from enterprise_anomaly import AnomalyDetector
from enterprise_compliance import ComplianceManager
from enterprise_threat_intel import ThreatIntelligenceManager
from enterprise_types import (
    CONSTANT_20,
    CONSTANT_30,
    CONSTANT_40,
    CONSTANT_50,
    CONSTANT_128,
    CONSTANT_400,
    ComplianceCheck,
    SecurityEvent,
    logger,
)


class EnterpriseSecurityMonitor:
    """Enterprise-grade security monitoring system."""

    def __init__(self, config_file: str = "enterprise_config.yaml"):
        self.config = self.load_config(config_file)
        self.anomaly_detector = AnomalyDetector(self.config.get("anomaly_detection", {}))
        self.threat_manager = ThreatIntelligenceManager(self.config.get("threat_intelligence", {}))
        self.compliance_manager = ComplianceManager(self.config.get("compliance", {}))
        self.security_events: list[SecurityEvent] = []

    def load_config(self, config_file: str) -> dict[str, Any]:
        default_config: dict[str, Any] = {
            "anomaly_detection": {
                "enabled": True,
                "anomaly_threshold": 2.0,
                "window_size": 100,
            },
            "threat_intelligence": {
                "enabled": True,
                "threat_feeds": {
                    "malware_domains": {
                        "enabled": True,
                        "url": "https://example.com/threat-feed",
                    },
                },
            },
            "compliance": {"enabled": True, "standards": ["GDPR", "ISO27001", "SOC2"]},
            "reporting": {
                "enabled": True,
                "frequency": "daily",
                "formats": ["json", "pdf", "markdown"],
            },
        }
        config_path = Path(config_file)
        if config_path.exists():
            with open(config_path, encoding="utf-8") as handle:
                user_config = yaml.safe_load(handle)
                if isinstance(user_config, dict):
                    default_config.update(user_config)
        return default_config

    async def collect_metrics(self) -> list[dict[str, Any]]:
        metrics: list[dict[str, Any]] = []
        try:
            async with aiohttp.ClientSession() as session:
                start_time = datetime.now()
                async with session.get("https://obywatel.bielik.ai") as response:
                    end_time = datetime.now()
                    response_time = (end_time - start_time).total_seconds() * 1000
                    metrics.append(
                        {
                            "timestamp": datetime.now(),
                            "response_time": response_time,
                            "status_code": response.status,
                            "content_length": response.headers.get("content-length", 0),
                            "error_rate": 1.0 if response.status >= CONSTANT_400 else 0.0,
                        },
                    )
        except Exception as exc:
            logger.error("Failed to collect metrics: %s", exc)
            metrics.append(
                {
                    "timestamp": datetime.now(),
                    "response_time": 0,
                    "status_code": 0,
                    "content_length": 0,
                    "error_rate": 1.0,
                },
            )
        return metrics

    async def analyze_security_headers(self) -> dict[str, str]:
        headers: dict[str, str] = {}
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get("https://obywatel.bielik.ai") as response:
                    response_headers = dict(response.headers)
                    for header in (
                        "content-security-policy",
                        "x-frame-options",
                        "x-content-type-options",
                        "referrer-policy",
                        "strict-transport-security",
                        "permissions-policy",
                    ):
                        if header in response_headers:
                            headers[header] = response_headers[header]
        except Exception as exc:
            logger.error("Failed to analyze security headers: %s", exc)
        return headers

    async def analyze_ssl_configuration(self) -> dict[str, Any]:
        ssl_config: dict[str, Any] = {}
        try:
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            async with aiohttp.ClientSession() as session:
                async with session.get("https://obywatel.bielik.ai", ssl=context) as response:
                    ssl_info = response.connection.get_extra_info("ssl_object")
                    if ssl_info:
                        ssl_config = {
                            "protocol_version": ssl_info.version(),
                            "cipher_name": ssl_info.cipher()[0],
                            "cipher_bits": ssl_info.cipher()[1],
                            "compression": ssl_info.compression(),
                        }
        except Exception as exc:
            logger.error("Failed to analyze SSL configuration: %s", exc)
        return ssl_config

    async def run_enterprise_analysis(self) -> dict[str, Any]:
        logger.info("Starting enterprise security analysis...")
        metrics = await self.collect_metrics()
        security_headers = await self.analyze_security_headers()
        ssl_config = await self.analyze_ssl_configuration()

        content = ""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get("https://obywatel.bielik.ai") as response:
                    content = await response.text()
        except Exception as exc:
            logger.error("Failed to fetch content: %s", exc)

        anomalies: list[SecurityEvent] = []
        if self.config["anomaly_detection"]["enabled"]:
            self.anomaly_detector.collect_baseline(metrics)
            anomalies = self.anomaly_detector.detect_anomalies(metrics)

        threat_events: list[SecurityEvent] = []
        if self.config["threat_intelligence"]["enabled"]:
            threats = await self.threat_manager.fetch_threat_intelligence()
            threat_events = self.threat_manager.check_indicators(content, threats)

        compliance_checks: list[ComplianceCheck] = []
        if self.config["compliance"]["enabled"]:
            standards = self.config["compliance"]["standards"]
            if "GDPR" in standards:
                compliance_checks.extend(
                    self.compliance_manager.check_gdpr_compliance(security_headers, content),
                )
            if "ISO27001" in standards:
                compliance_checks.extend(
                    self.compliance_manager.check_iso27001_compliance(security_headers, ssl_config),
                )

        compliance_report = (
            self.compliance_manager.generate_compliance_report(compliance_checks)
            if compliance_checks
            else {}
        )

        results: dict[str, Any] = {
            "timestamp": datetime.now().isoformat(),
            "metrics": metrics,
            "security_headers": security_headers,
            "ssl_configuration": ssl_config,
            "anomalies": [asdict(event) for event in anomalies],
            "threat_events": [asdict(event) for event in threat_events],
            "compliance_checks": [asdict(check) for check in compliance_checks],
            "compliance_report": compliance_report,
            "summary": {
                "total_events": len(anomalies) + len(threat_events),
                "anomaly_count": len(anomalies),
                "threat_count": len(threat_events),
                "compliance_score": self._calculate_compliance_score(compliance_checks),
                "security_score": self._calculate_security_score(security_headers, ssl_config),
            },
        }
        await self._save_results(results)
        logger.info("Enterprise analysis completed. Events: %s", results["summary"]["total_events"])
        return results

    def _calculate_compliance_score(self, checks: list[ComplianceCheck]) -> float:
        if not checks:
            return 0.0
        total_score = 0
        for check in checks:
            if check.status == "compliant":
                total_score += 100
            elif check.status == "partial":
                total_score += CONSTANT_50
        return total_score / len(checks)

    def _calculate_security_score(self, headers: dict[str, str], ssl_config: dict[str, Any]) -> float:
        score = 0.0
        required_headers = [
            "content-security-policy",
            "x-frame-options",
            "x-content-type-options",
            "referrer-policy",
            "strict-transport-security",
            "permissions-policy",
        ]
        score += (len(headers) / len(required_headers)) * CONSTANT_40
        if ssl_config.get("protocol_version", "") in ["TLSv1.2", "TLSv1.3"]:
            score += CONSTANT_20
        if ssl_config.get("cipher_bits", 0) >= CONSTANT_128:
            score += 10
        score += CONSTANT_30
        return min(score, 100.0)

    async def _save_results(self, results: dict[str, Any]) -> None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        json_file = f"enterprise_analysis_{timestamp}.json"
        with open(json_file, "w", encoding="utf-8") as handle:
            json.dump(results, handle, indent=2, default=str)
        md_file = f"enterprise_analysis_{timestamp}.md"
        await self._generate_markdown_report(results, md_file)
        logger.info("Results saved to %s and %s", json_file, md_file)

    async def _generate_markdown_report(self, results: dict[str, Any], filename: str) -> None:
        report = f"""# Enterprise Security Analysis Report

**Generated:** {results["timestamp"]}
**Target:** obywatel.bielik.ai

## Executive Summary

- **Security Score:** {results["summary"]["security_score"]:.1f}/100
- **Compliance Score:** {results["summary"]["compliance_score"]:.1f}/100
- **Total Security Events:** {results["summary"]["total_events"]}
- **Anomalies Detected:** {results["summary"]["anomaly_count"]}
- **Threat Indicators:** {results["summary"]["threat_count"]}

## Security Analysis

### Security Headers
{len(results["security_headers"])}/6 required headers present

"""
        for header in results["security_headers"]:
            report += f"- **{header}:** Present\n"

        report += f"""
### SSL/TLS Configuration
- **Protocol:** {results["ssl_configuration"].get("protocol_version", "Unknown")}
- **Cipher:** {results["ssl_configuration"].get("cipher_name", "Unknown")}
- **Cipher Strength:** {results["ssl_configuration"].get("cipher_bits", 0)} bits

## Security Events

### Anomalies Detected
"""
        for anomaly in results["anomalies"]:
            report += f"""
#### {anomaly["event_type"].replace("_", " ").title()}
- **Severity:** {anomaly["severity"]}
- **Confidence:** {anomaly["confidence"]:.2f}
- **Details:** {anomaly["details"]}
- **Remediation:** {anomaly.get("remediation", "N/A")}
"""

        report += "\n### Threat Intelligence Events\n"
        for threat in results["threat_events"]:
            report += f"""
#### {threat["event_type"].replace("_", " ").title()}
- **Severity:** {threat["severity"]}
- **Indicator:** {threat["details"].get("indicator", "N/A")}
- **Threat Type:** {threat["details"].get("threat_type", "N/A")}
- **Confidence:** {threat["confidence"]:.2f}
"""

        if results["compliance_report"]:
            report += f"""
## Compliance Analysis

### Overall Compliance Status
- **Total Checks:** {results["compliance_report"]["total_checks"]}
- **Compliant:** {results["compliance_report"]["compliant"]}
- **Non-Compliant:** {results["compliance_report"]["non_compliant"]}
- **Partial:** {results["compliance_report"]["partial"]}

### High Risk Issues
"""
            for issue in results["compliance_report"]["high_risk_issues"]:
                report += f"""
- **{issue.standard} - {issue.control}:** {issue.status}
  - **Risk Level:** {issue.risk_level}
  - **Remediation:** {issue.remediation}
"""

        report += """
## Recommendations

1. **Implement Missing Security Headers**
2. **Upgrade SSL/TLS Configuration**
3. **Monitor Anomalies and Threats**
4. **Address Compliance Issues**
5. **Establish Regular Security Reviews**

---
*Report generated by Enterprise Security Monitor*
"""
        with open(filename, "w", encoding="utf-8") as handle:
            handle.write(report)
