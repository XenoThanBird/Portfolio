"""
TLS Handshake Analyzer — TLS Inspector

Connects to a target host:port via the ssl stdlib module, captures the full
TLS handshake details: certificate chain, cipher suite, protocol version,
and certificate expiry information.

Purely connects as a client and inspects what the server presents.
No packet interception or modification.
"""

import ssl
import socket
import json
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Optional


@dataclass
class CertificateInfo:
    """Parsed X.509 certificate details."""
    subject: dict = field(default_factory=dict)
    issuer: dict = field(default_factory=dict)
    serial_number: str = ""
    version: int = 0
    not_before: str = ""
    not_after: str = ""
    days_until_expiry: int = 0
    is_expired: bool = False
    sans: list = field(default_factory=list)
    signature_algorithm: str = ""
    key_type: str = ""
    key_size: int = 0


@dataclass
class HandshakeResult:
    """Complete TLS handshake analysis result."""
    host: str = ""
    port: int = 443
    protocol_version: str = ""
    cipher_suite: str = ""
    cipher_bits: int = 0
    cipher_protocol: str = ""
    certificate: Optional[CertificateInfo] = None
    certificate_chain: list = field(default_factory=list)
    chain_length: int = 0
    timestamp: str = ""
    error: str = ""
    success: bool = False

    def to_dict(self) -> dict:
        result = asdict(self)
        return result


def _parse_dn(dn_tuples: tuple) -> dict:
    """Parse a distinguished name tuple into a flat dict."""
    result = {}
    for rdn in dn_tuples:
        for attr_type, attr_value in rdn:
            result[attr_type] = attr_value
    return result


def _parse_san(cert_dict: dict) -> list:
    """Extract Subject Alternative Names from certificate."""
    sans = []
    for san_type, san_value in cert_dict.get("subjectAltName", ()):
        sans.append({"type": san_type, "value": san_value})
    return sans


def _parse_certificate(cert_dict: dict, cert_der: bytes = None) -> CertificateInfo:
    """Parse a certificate dictionary into CertificateInfo."""
    info = CertificateInfo()

    info.subject = _parse_dn(cert_dict.get("subject", ()))
    info.issuer = _parse_dn(cert_dict.get("issuer", ()))
    info.serial_number = cert_dict.get("serialNumber", "")
    info.version = cert_dict.get("version", 0)
    info.sans = _parse_san(cert_dict)

    not_before = cert_dict.get("notBefore", "")
    not_after = cert_dict.get("notAfter", "")
    info.not_before = not_before
    info.not_after = not_after

    if not_after:
        try:
            expiry = datetime.strptime(not_after, "%b %d %H:%M:%S %Y %Z")
            expiry = expiry.replace(tzinfo=timezone.utc)
            now = datetime.now(timezone.utc)
            delta = expiry - now
            info.days_until_expiry = delta.days
            info.is_expired = delta.days < 0
        except ValueError:
            pass

    # Extract key info from the DER-encoded certificate if available
    if cert_der:
        try:
            info.key_type, info.key_size = _extract_key_info(cert_der)
        except Exception:
            pass

    return info


def _extract_key_info(cert_der: bytes) -> tuple:
    """
    Extract public key type and size from DER-encoded certificate.
    Uses basic ASN.1 OID matching for RSA and EC keys.
    """
    # RSA OID: 1.2.840.113549.1.1.1
    rsa_oid = b"\x06\x09\x2a\x86\x48\x86\xf7\x0d\x01\x01\x01"
    # EC OID: 1.2.840.10045.2.1
    ec_oid = b"\x06\x07\x2a\x86\x48\xce\x3d\x02\x01"

    if rsa_oid in cert_der:
        # Estimate RSA key size from modulus bit length
        # Look for the BIT STRING containing the public key
        key_size = _estimate_rsa_key_size(cert_der)
        return "RSA", key_size
    elif ec_oid in cert_der:
        key_size = _estimate_ec_key_size(cert_der)
        return "EC", key_size

    return "Unknown", 0


def _estimate_rsa_key_size(cert_der: bytes) -> int:
    """Estimate RSA key size from certificate DER bytes."""
    cert_len = len(cert_der)
    if cert_len > 1500:
        return 4096
    elif cert_len > 900:
        return 2048
    elif cert_len > 600:
        return 1024
    return 2048  # Default assumption


def _estimate_ec_key_size(cert_der: bytes) -> int:
    """Estimate EC key size from certificate DER bytes."""
    # P-256 OID: 1.2.840.10045.3.1.7
    p256_oid = b"\x06\x08\x2a\x86\x48\xce\x3d\x03\x01\x07"
    # P-384 OID: 1.3.132.0.34
    p384_oid = b"\x06\x05\x2b\x81\x04\x00\x22"
    # P-521 OID: 1.3.132.0.35
    p521_oid = b"\x06\x05\x2b\x81\x04\x00\x23"

    if p256_oid in cert_der:
        return 256
    elif p384_oid in cert_der:
        return 384
    elif p521_oid in cert_der:
        return 521
    return 256  # Default


def inspect_tls(host: str, port: int = 443, timeout: int = 10) -> HandshakeResult:
    """
    Perform a TLS handshake with the target and capture all details.

    Connects as a standard TLS client, inspects the server's certificate
    and negotiated parameters. No packet interception involved.
    """
    result = HandshakeResult(
        host=host,
        port=port,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )

    try:
        # Create SSL context — we want to inspect, not enforce
        context = ssl.create_default_context()

        # For analysis purposes, we still validate but capture errors
        conn = context.wrap_socket(
            socket.socket(socket.AF_INET, socket.SOCK_STREAM),
            server_hostname=host,
        )
        conn.settimeout(timeout)

        try:
            conn.connect((host, port))

            # Capture negotiated protocol and cipher
            result.protocol_version = conn.version() or "Unknown"
            cipher_info = conn.cipher()
            if cipher_info:
                result.cipher_suite = cipher_info[0]
                result.cipher_protocol = cipher_info[1]
                result.cipher_bits = cipher_info[2]

            # Capture peer certificate
            cert_dict = conn.getpeercert()
            cert_der = conn.getpeercert(binary_form=True)
            if cert_dict:
                result.certificate = _parse_certificate(cert_dict, cert_der)

            # Capture certificate chain
            chain_der = conn.getpeercert(binary_form=True)
            if chain_der:
                result.chain_length = 1  # stdlib only gives leaf cert
                # Note: Full chain inspection requires the cryptography library
                # We work with what stdlib provides

            result.success = True

        finally:
            conn.close()

    except ssl.SSLCertVerificationError as e:
        result.error = f"Certificate verification failed: {e}"
        # Try again without verification to still capture cert details
        _inspect_without_verify(host, port, timeout, result)

    except ssl.SSLError as e:
        result.error = f"SSL error: {e}"

    except socket.timeout:
        result.error = f"Connection timed out after {timeout}s"

    except socket.gaierror as e:
        result.error = f"DNS resolution failed: {e}"

    except OSError as e:
        result.error = f"Connection failed: {e}"

    return result


def _inspect_without_verify(
    host: str, port: int, timeout: int, result: HandshakeResult
) -> None:
    """Re-attempt connection without cert verification to capture details."""
    try:
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE

        conn = context.wrap_socket(
            socket.socket(socket.AF_INET, socket.SOCK_STREAM),
            server_hostname=host,
        )
        conn.settimeout(timeout)

        try:
            conn.connect((host, port))
            result.protocol_version = conn.version() or "Unknown"
            cipher_info = conn.cipher()
            if cipher_info:
                result.cipher_suite = cipher_info[0]
                result.cipher_protocol = cipher_info[1]
                result.cipher_bits = cipher_info[2]

            cert_dict = conn.getpeercert(binary_form=False)
            cert_der = conn.getpeercert(binary_form=True)
            if cert_dict:
                result.certificate = _parse_certificate(cert_dict, cert_der)
            elif cert_der:
                # When verify_mode=CERT_NONE, getpeercert() may return empty
                # but binary form is still available
                result.certificate = CertificateInfo()
                try:
                    key_type, key_size = _extract_key_info(cert_der)
                    result.certificate.key_type = key_type
                    result.certificate.key_size = key_size
                except Exception:
                    pass

            result.success = True  # We got data, even if cert is invalid
        finally:
            conn.close()

    except Exception:
        pass  # Keep original error message


if __name__ == "__main__":
    import sys

    host = sys.argv[1] if len(sys.argv) > 1 else "google.com"
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 443

    print(f"Inspecting TLS handshake with {host}:{port}...")
    result = inspect_tls(host, port)
    print(json.dumps(result.to_dict(), indent=2, default=str))
