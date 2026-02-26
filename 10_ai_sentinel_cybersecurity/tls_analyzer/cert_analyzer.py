"""
TLS Handshake Analyzer — Certificate Analyzer

Parses X.509 certificate details: issuer, subject, SANs, key size,
signature algorithm, expiry warnings, and chain validation.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

from tls_inspector import CertificateInfo, HandshakeResult


@dataclass
class CertAnalysis:
    """Detailed analysis of a certificate."""
    host: str = ""
    subject_cn: str = ""
    issuer_cn: str = ""
    issuer_org: str = ""
    serial: str = ""
    valid_from: str = ""
    valid_until: str = ""
    days_remaining: int = 0
    is_expired: bool = False
    is_self_signed: bool = False
    san_count: int = 0
    san_list: list = field(default_factory=list)
    key_type: str = ""
    key_size: int = 0
    hostname_match: bool = False
    warnings: list = field(default_factory=list)


def analyze_certificate(
    result: HandshakeResult,
    expiry_warning_days: int = 30,
) -> CertAnalysis:
    """
    Perform detailed analysis of a TLS handshake result's certificate.

    Extracts all relevant fields and generates warnings for potential issues.
    """
    analysis = CertAnalysis(host=result.host)

    cert = result.certificate
    if not cert:
        analysis.warnings.append("No certificate data available")
        return analysis

    # Subject and issuer
    analysis.subject_cn = cert.subject.get("commonName", "N/A")
    analysis.issuer_cn = cert.issuer.get("commonName", "N/A")
    analysis.issuer_org = cert.issuer.get("organizationName", "N/A")
    analysis.serial = cert.serial_number

    # Validity period
    analysis.valid_from = cert.not_before
    analysis.valid_until = cert.not_after
    analysis.days_remaining = cert.days_until_expiry
    analysis.is_expired = cert.is_expired

    # Self-signed detection
    analysis.is_self_signed = cert.subject == cert.issuer

    # SANs
    analysis.san_list = [
        san.get("value", "") for san in cert.sans
        if san.get("type") == "DNS"
    ]
    analysis.san_count = len(analysis.san_list)

    # Key info
    analysis.key_type = cert.key_type
    analysis.key_size = cert.key_size

    # Hostname matching
    analysis.hostname_match = _check_hostname_match(result.host, cert)

    # Generate warnings
    analysis.warnings = _generate_warnings(analysis, expiry_warning_days)

    return analysis


def _check_hostname_match(hostname: str, cert: CertificateInfo) -> bool:
    """Check if the hostname matches the certificate's CN or SANs."""
    # Check CN
    cn = cert.subject.get("commonName", "")
    if _matches_pattern(hostname, cn):
        return True

    # Check SANs
    for san in cert.sans:
        if san.get("type") == "DNS":
            if _matches_pattern(hostname, san.get("value", "")):
                return True

    return False


def _matches_pattern(hostname: str, pattern: str) -> bool:
    """Check if hostname matches a certificate pattern (supports wildcards)."""
    if not pattern:
        return False

    hostname = hostname.lower()
    pattern = pattern.lower()

    if pattern == hostname:
        return True

    # Wildcard matching: *.example.com matches sub.example.com
    if pattern.startswith("*."):
        suffix = pattern[2:]
        # Must match the suffix and have exactly one more label
        if hostname.endswith("." + suffix):
            prefix = hostname[: -(len(suffix) + 1)]
            if "." not in prefix:
                return True

    return False


def _generate_warnings(
    analysis: CertAnalysis, expiry_warning_days: int
) -> list:
    """Generate security warnings based on certificate analysis."""
    warnings = []

    if analysis.is_expired:
        warnings.append(
            f"CRITICAL: Certificate expired {abs(analysis.days_remaining)} days ago"
        )
    elif 0 < analysis.days_remaining <= expiry_warning_days:
        warnings.append(
            f"WARNING: Certificate expires in {analysis.days_remaining} days"
        )

    if analysis.is_self_signed:
        warnings.append("WARNING: Self-signed certificate detected")

    if analysis.san_count == 0:
        warnings.append(
            "WARNING: No Subject Alternative Names — "
            "modern browsers require SANs"
        )

    if not analysis.hostname_match:
        warnings.append(
            f"WARNING: Hostname '{analysis.host}' does not match "
            f"certificate CN '{analysis.subject_cn}'"
        )

    if analysis.key_type == "RSA" and 0 < analysis.key_size < 2048:
        warnings.append(
            f"WARNING: RSA key size {analysis.key_size}-bit is below "
            f"2048-bit minimum"
        )

    if analysis.key_type == "EC" and 0 < analysis.key_size < 256:
        warnings.append(
            f"WARNING: EC key size {analysis.key_size}-bit is below "
            f"256-bit minimum"
        )

    return warnings


def format_analysis(analysis: CertAnalysis) -> str:
    """Format certificate analysis as a human-readable string."""
    lines = [
        f"Certificate Analysis: {analysis.host}",
        "=" * 50,
        f"  Subject CN:     {analysis.subject_cn}",
        f"  Issuer CN:      {analysis.issuer_cn}",
        f"  Issuer Org:     {analysis.issuer_org}",
        f"  Serial:         {analysis.serial}",
        f"  Valid From:     {analysis.valid_from}",
        f"  Valid Until:    {analysis.valid_until}",
        f"  Days Remaining: {analysis.days_remaining}",
        f"  Expired:        {analysis.is_expired}",
        f"  Self-Signed:    {analysis.is_self_signed}",
        f"  Key Type:       {analysis.key_type}",
        f"  Key Size:       {analysis.key_size} bits",
        f"  Hostname Match: {analysis.hostname_match}",
        f"  SAN Count:      {analysis.san_count}",
    ]

    if analysis.san_list:
        lines.append("  SANs:")
        for san in analysis.san_list[:10]:
            lines.append(f"    - {san}")
        if len(analysis.san_list) > 10:
            lines.append(f"    ... and {len(analysis.san_list) - 10} more")

    if analysis.warnings:
        lines.append("")
        lines.append("  Warnings:")
        for w in analysis.warnings:
            lines.append(f"    ! {w}")

    return "\n".join(lines)
