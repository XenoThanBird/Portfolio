"""
TLS Handshake Analyzer — Compliance Checker

Checks TLS configurations against security baselines: flags deprecated
protocols, weak ciphers, short keys, and expiring certificates.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from tls_inspector import HandshakeResult
from cert_analyzer import CertAnalysis


class CheckStatus(Enum):
    """Compliance check result status."""
    PASS = "PASS"
    FAIL = "FAIL"
    WARNING = "WARNING"
    INFO = "INFO"


@dataclass
class ComplianceCheck:
    """A single compliance check result."""
    category: str = ""
    check_name: str = ""
    status: CheckStatus = CheckStatus.INFO
    actual_value: str = ""
    expected: str = ""
    detail: str = ""


@dataclass
class ComplianceReport:
    """Full compliance report for a host."""
    host: str = ""
    port: int = 443
    checks: list = field(default_factory=list)
    pass_count: int = 0
    fail_count: int = 0
    warning_count: int = 0
    overall_status: CheckStatus = CheckStatus.PASS

    def add_check(self, check: ComplianceCheck) -> None:
        self.checks.append(check)
        if check.status == CheckStatus.PASS:
            self.pass_count += 1
        elif check.status == CheckStatus.FAIL:
            self.fail_count += 1
            self.overall_status = CheckStatus.FAIL
        elif check.status == CheckStatus.WARNING:
            self.warning_count += 1
            if self.overall_status != CheckStatus.FAIL:
                self.overall_status = CheckStatus.WARNING


# Default compliance rules
DEFAULT_DEPRECATED_PROTOCOLS = ["TLSv1", "TLSv1.1", "SSLv3", "SSLv2"]
DEFAULT_WEAK_CIPHERS = ["RC4", "DES", "3DES", "NULL", "EXPORT", "MD5"]
DEFAULT_MIN_KEY_SIZES = {"RSA": 2048, "EC": 256, "DSA": 2048}
DEFAULT_EXPIRY_WARNING_DAYS = 30


def check_compliance(
    result: HandshakeResult,
    analysis: CertAnalysis,
    deprecated_protocols: list = None,
    weak_ciphers: list = None,
    min_key_sizes: dict = None,
    expiry_warning_days: int = DEFAULT_EXPIRY_WARNING_DAYS,
    require_sans: bool = True,
) -> ComplianceReport:
    """
    Run all compliance checks against a TLS handshake result.

    Checks protocol version, cipher strength, key sizes, certificate
    validity, and SAN presence against configurable baselines.
    """
    if deprecated_protocols is None:
        deprecated_protocols = DEFAULT_DEPRECATED_PROTOCOLS
    if weak_ciphers is None:
        weak_ciphers = DEFAULT_WEAK_CIPHERS
    if min_key_sizes is None:
        min_key_sizes = DEFAULT_MIN_KEY_SIZES

    report = ComplianceReport(host=result.host, port=result.port)

    # Protocol version check
    report.add_check(_check_protocol(result, deprecated_protocols))

    # Cipher suite check
    report.add_check(_check_cipher(result, weak_ciphers))

    # Cipher strength check
    report.add_check(_check_cipher_bits(result))

    # Key size check
    report.add_check(_check_key_size(analysis, min_key_sizes))

    # Certificate expiry check
    report.add_check(_check_expiry(analysis, expiry_warning_days))

    # Self-signed check
    report.add_check(_check_self_signed(analysis))

    # SAN presence check
    if require_sans:
        report.add_check(_check_sans(analysis))

    # Hostname match check
    report.add_check(_check_hostname(analysis))

    return report


def _check_protocol(
    result: HandshakeResult, deprecated: list
) -> ComplianceCheck:
    """Check if the negotiated protocol is deprecated."""
    check = ComplianceCheck(
        category="Protocol",
        check_name="TLS Protocol Version",
        actual_value=result.protocol_version,
    )

    if not result.protocol_version:
        check.status = CheckStatus.WARNING
        check.detail = "Could not determine protocol version"
        return check

    if result.protocol_version in deprecated:
        check.status = CheckStatus.FAIL
        check.expected = "TLSv1.2 or higher"
        check.detail = (
            f"Deprecated protocol {result.protocol_version} in use"
        )
    elif result.protocol_version in ("TLSv1.3",):
        check.status = CheckStatus.PASS
        check.expected = "TLSv1.2 or higher"
        check.detail = "Using latest TLS 1.3 protocol"
    elif result.protocol_version in ("TLSv1.2",):
        check.status = CheckStatus.PASS
        check.expected = "TLSv1.2 or higher"
        check.detail = "Using TLS 1.2 — acceptable"
    else:
        check.status = CheckStatus.INFO
        check.detail = f"Protocol: {result.protocol_version}"

    return check


def _check_cipher(
    result: HandshakeResult, weak_ciphers: list
) -> ComplianceCheck:
    """Check if the negotiated cipher suite contains weak algorithms."""
    check = ComplianceCheck(
        category="Cipher",
        check_name="Cipher Suite Strength",
        actual_value=result.cipher_suite,
    )

    if not result.cipher_suite:
        check.status = CheckStatus.WARNING
        check.detail = "Could not determine cipher suite"
        return check

    cipher_upper = result.cipher_suite.upper()
    found_weak = [
        w for w in weak_ciphers if w.upper() in cipher_upper
    ]

    if found_weak:
        check.status = CheckStatus.FAIL
        check.expected = "No weak cipher components"
        check.detail = (
            f"Weak cipher component(s) detected: {', '.join(found_weak)}"
        )
    else:
        check.status = CheckStatus.PASS
        check.expected = "No weak cipher components"
        check.detail = "Cipher suite appears strong"

    return check


def _check_cipher_bits(result: HandshakeResult) -> ComplianceCheck:
    """Check the cipher bit strength."""
    check = ComplianceCheck(
        category="Cipher",
        check_name="Cipher Bit Strength",
        actual_value=f"{result.cipher_bits} bits",
        expected="128 bits or higher",
    )

    if result.cipher_bits >= 256:
        check.status = CheckStatus.PASS
        check.detail = f"{result.cipher_bits}-bit encryption — excellent"
    elif result.cipher_bits >= 128:
        check.status = CheckStatus.PASS
        check.detail = f"{result.cipher_bits}-bit encryption — acceptable"
    elif result.cipher_bits > 0:
        check.status = CheckStatus.FAIL
        check.detail = (
            f"{result.cipher_bits}-bit encryption is below minimum"
        )
    else:
        check.status = CheckStatus.WARNING
        check.detail = "Could not determine cipher bit strength"

    return check


def _check_key_size(
    analysis: CertAnalysis, min_sizes: dict
) -> ComplianceCheck:
    """Check the public key size against minimums."""
    check = ComplianceCheck(
        category="Key",
        check_name="Public Key Size",
        actual_value=f"{analysis.key_type} {analysis.key_size} bits",
    )

    if not analysis.key_type or analysis.key_size == 0:
        check.status = CheckStatus.INFO
        check.detail = "Could not determine key type/size"
        return check

    min_size = min_sizes.get(analysis.key_type, 0)
    check.expected = f"{analysis.key_type} >= {min_size} bits"

    if min_size == 0:
        check.status = CheckStatus.INFO
        check.detail = f"No minimum defined for {analysis.key_type}"
    elif analysis.key_size >= min_size:
        check.status = CheckStatus.PASS
        check.detail = (
            f"{analysis.key_type} {analysis.key_size}-bit meets minimum "
            f"({min_size}-bit)"
        )
    else:
        check.status = CheckStatus.FAIL
        check.detail = (
            f"{analysis.key_type} {analysis.key_size}-bit is below "
            f"minimum ({min_size}-bit)"
        )

    return check


def _check_expiry(
    analysis: CertAnalysis, warning_days: int
) -> ComplianceCheck:
    """Check certificate expiry."""
    check = ComplianceCheck(
        category="Certificate",
        check_name="Certificate Expiry",
        actual_value=f"{analysis.days_remaining} days remaining",
        expected=f"More than {warning_days} days until expiry",
    )

    if analysis.is_expired:
        check.status = CheckStatus.FAIL
        check.detail = (
            f"Certificate expired {abs(analysis.days_remaining)} days ago"
        )
    elif analysis.days_remaining <= warning_days:
        check.status = CheckStatus.WARNING
        check.detail = (
            f"Certificate expires in {analysis.days_remaining} days"
        )
    else:
        check.status = CheckStatus.PASS
        check.detail = (
            f"Certificate valid for {analysis.days_remaining} more days"
        )

    return check


def _check_self_signed(analysis: CertAnalysis) -> ComplianceCheck:
    """Check if certificate is self-signed."""
    check = ComplianceCheck(
        category="Certificate",
        check_name="Certificate Authority",
        actual_value=(
            "Self-signed" if analysis.is_self_signed else "CA-signed"
        ),
        expected="CA-signed certificate",
    )

    if analysis.is_self_signed:
        check.status = CheckStatus.WARNING
        check.detail = "Self-signed certificate — not trusted by browsers"
    else:
        check.status = CheckStatus.PASS
        check.detail = f"Signed by {analysis.issuer_org}"

    return check


def _check_sans(analysis: CertAnalysis) -> ComplianceCheck:
    """Check for Subject Alternative Names."""
    check = ComplianceCheck(
        category="Certificate",
        check_name="Subject Alternative Names",
        actual_value=f"{analysis.san_count} SANs",
        expected="At least 1 SAN entry",
    )

    if analysis.san_count > 0:
        check.status = CheckStatus.PASS
        check.detail = f"{analysis.san_count} SAN(s) present"
    else:
        check.status = CheckStatus.WARNING
        check.detail = "No SANs — modern browsers require SANs for trust"

    return check


def _check_hostname(analysis: CertAnalysis) -> ComplianceCheck:
    """Check hostname matching."""
    check = ComplianceCheck(
        category="Certificate",
        check_name="Hostname Match",
        actual_value=str(analysis.hostname_match),
        expected="Hostname matches certificate",
    )

    if analysis.hostname_match:
        check.status = CheckStatus.PASS
        check.detail = f"Hostname '{analysis.host}' matches certificate"
    else:
        check.status = CheckStatus.FAIL
        check.detail = (
            f"Hostname '{analysis.host}' does not match "
            f"certificate CN '{analysis.subject_cn}'"
        )

    return check


def format_compliance(report: ComplianceReport) -> str:
    """Format compliance report as a human-readable string."""
    status_icons = {
        CheckStatus.PASS: "[PASS]",
        CheckStatus.FAIL: "[FAIL]",
        CheckStatus.WARNING: "[WARN]",
        CheckStatus.INFO: "[INFO]",
    }

    lines = [
        f"Compliance Report: {report.host}:{report.port}",
        "=" * 50,
        f"  Overall: {status_icons[report.overall_status]} "
        f"({report.pass_count} pass, {report.fail_count} fail, "
        f"{report.warning_count} warning)",
        "",
    ]

    current_category = ""
    for check in report.checks:
        if check.category != current_category:
            current_category = check.category
            lines.append(f"  [{current_category}]")

        icon = status_icons[check.status]
        lines.append(f"    {icon} {check.check_name}")
        lines.append(f"           {check.detail}")
        if check.actual_value:
            lines.append(f"           Value: {check.actual_value}")

    return "\n".join(lines)
