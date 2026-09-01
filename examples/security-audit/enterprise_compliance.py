"""Compliance checks and reporting."""

from __future__ import annotations

import re
from datetime import datetime
from typing import Any

from enterprise_types import ComplianceCheck


class ComplianceManager:
    """Compliance management and automation."""

    def __init__(self, config: dict[str, Any]):
        self.config = config
        self.standards = config.get("standards", {})

    def check_gdpr_compliance(
        self,
        security_headers: dict[str, str],
        content: str,
    ) -> list[ComplianceCheck]:
        checks: list[ComplianceCheck] = []
        if "content-security-policy" not in security_headers:
            checks.append(
                ComplianceCheck(
                    standard="GDPR",
                    control="Data Protection Headers",
                    status="non_compliant",
                    evidence=["Missing Content-Security-Policy header"],
                    risk_level="medium",
                    remediation="Implement Content-Security-Policy header to protect against data injection",
                ),
            )

        personal_data_patterns = [
            r"\b\d{11}\b",
            r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
            r"\b\d{3}-\d{2}-\d{4}\b",
        ]
        found_personal_data: list[str] = []
        for pattern in personal_data_patterns:
            found_personal_data.extend(re.findall(pattern, content, re.IGNORECASE))

        if found_personal_data:
            checks.append(
                ComplianceCheck(
                    standard="GDPR",
                    control="Personal Data Protection",
                    status="non_compliant",
                    evidence=[f"Found potential personal data: {len(found_personal_data)} instances"],
                    risk_level="high",
                    remediation="Remove or properly protect personal data from public content",
                ),
            )
        return checks

    def check_iso27001_compliance(
        self,
        security_headers: dict[str, str],
        ssl_config: dict[str, Any],
    ) -> list[ComplianceCheck]:
        checks: list[ComplianceCheck] = []
        required_headers = [
            "strict-transport-security",
            "x-frame-options",
            "x-content-type-options",
        ]
        missing_headers = [h for h in required_headers if h not in security_headers]
        if missing_headers:
            checks.append(
                ComplianceCheck(
                    standard="ISO27001",
                    control="A.13.1.1 Network Security Controls",
                    status="partial",
                    evidence=[f"Missing security headers: {', '.join(missing_headers)}"],
                    risk_level="medium",
                    remediation="Implement missing security headers for network protection",
                ),
            )

        if ssl_config.get("protocol_version", "") in ["SSLv2", "SSLv3", "TLSv1", "TLSv1.1"]:
            checks.append(
                ComplianceCheck(
                    standard="ISO27001",
                    control="A.10.1.1 Cryptographic Controls",
                    status="non_compliant",
                    evidence=[f"Weak SSL protocol: {ssl_config.get('protocol_version')}"],
                    risk_level="high",
                    remediation="Upgrade to TLS 1.2 or higher and disable weak protocols",
                ),
            )
        return checks

    def generate_compliance_report(self, checks: list[ComplianceCheck]) -> dict[str, Any]:
        report: dict[str, Any] = {
            "timestamp": datetime.now().isoformat(),
            "total_checks": len(checks),
            "compliant": len([c for c in checks if c.status == "compliant"]),
            "non_compliant": len([c for c in checks if c.status == "non_compliant"]),
            "partial": len([c for c in checks if c.status == "partial"]),
            "by_standard": {},
            "high_risk_issues": [c for c in checks if c.risk_level == "high"],
            "recommendations": [
                "Implement missing security headers to improve compliance",
                "Upgrade SSL/TLS configuration to meet modern standards",
                "Review and remove personal data from public content",
                "Establish regular compliance monitoring processes",
            ],
        }
        for check in checks:
            report["by_standard"].setdefault(
                check.standard,
                {"total": 0, "compliant": 0, "non_compliant": 0, "partial": 0},
            )
            report["by_standard"][check.standard]["total"] += 1
            report["by_standard"][check.standard][check.status] += 1
        return report
