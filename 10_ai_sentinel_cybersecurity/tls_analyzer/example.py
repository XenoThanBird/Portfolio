"""
TLS Handshake Analyzer — Example Demo

Analyzes well-known public hosts (google.com, github.com) to demonstrate
certificate inspection, compliance checking, and report generation.

No packet interception — purely connects as a TLS client and inspects
what the server presents. Fully legal and ethical.

Usage:
    python example.py
"""

import sys
import os

# Add parent paths for imports when running as script
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tls_inspector import inspect_tls
from cert_analyzer import analyze_certificate, format_analysis
from compliance_checker import check_compliance, format_compliance, CheckStatus
from report_generator import generate_markdown_report, save_reports


# ANSI colors for terminal output
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"


def print_header(text: str) -> None:
    print(f"\n{BOLD}{CYAN}{'=' * 60}{RESET}")
    print(f"{BOLD}{CYAN}  {text}{RESET}")
    print(f"{BOLD}{CYAN}{'=' * 60}{RESET}\n")


def print_section(text: str) -> None:
    print(f"\n{BOLD}{text}{RESET}")
    print("-" * 40)


def status_color(status: CheckStatus) -> str:
    if status == CheckStatus.PASS:
        return GREEN
    elif status == CheckStatus.FAIL:
        return RED
    elif status == CheckStatus.WARNING:
        return YELLOW
    return RESET


def main():
    print_header("TLS Handshake Analyzer — Demo")

    # Target hosts to analyze
    targets = [
        ("google.com", 443),
        ("github.com", 443),
    ]

    all_results = []
    all_analyses = []
    all_reports = []

    for host, port in targets:
        print_section(f"Analyzing {host}:{port}")

        # Step 1: TLS Handshake
        print(f"  Connecting to {host}:{port}...")
        result = inspect_tls(host, port, timeout=10)

        if not result.success:
            print(f"  {RED}Connection failed: {result.error}{RESET}")
            if result.certificate is None:
                print(f"  {YELLOW}Skipping (no data captured){RESET}")
                continue

        print(f"  {GREEN}Connected successfully{RESET}")
        print(f"  Protocol:    {result.protocol_version}")
        print(f"  Cipher:      {result.cipher_suite}")
        print(f"  Cipher Bits: {result.cipher_bits}")

        if result.error:
            print(f"  {YELLOW}Note: {result.error}{RESET}")

        # Step 2: Certificate Analysis
        print_section(f"Certificate Details — {host}")
        analysis = analyze_certificate(result, expiry_warning_days=30)
        print(format_analysis(analysis))

        # Step 3: Compliance Check
        print_section(f"Compliance Check — {host}")
        report = check_compliance(result, analysis)

        for check in report.checks:
            color = status_color(check.status)
            icon = {
                CheckStatus.PASS: "[PASS]",
                CheckStatus.FAIL: "[FAIL]",
                CheckStatus.WARNING: "[WARN]",
                CheckStatus.INFO: "[INFO]",
            }[check.status]
            print(f"  {color}{icon}{RESET} {check.check_name}")
            print(f"         {check.detail}")

        # Overall status
        overall_color = status_color(report.overall_status)
        print(f"\n  {overall_color}{BOLD}Overall: "
              f"{report.overall_status.value}{RESET} "
              f"({report.pass_count} pass, {report.fail_count} fail, "
              f"{report.warning_count} warning)")

        all_results.append(result)
        all_analyses.append(analysis)
        all_reports.append(report)

    # Step 4: Generate Reports
    if all_results:
        print_header("Report Generation")

        # Generate and display markdown report summary
        md_report = generate_markdown_report(
            all_results, all_analyses, all_reports
        )

        # Show first few lines of the report
        preview_lines = md_report.split("\n")[:20]
        print("  Markdown Report Preview:")
        for line in preview_lines:
            print(f"    {line}")
        print(f"    ... ({len(md_report.split(chr(10)))} total lines)")

        # Save reports to temp directory
        import tempfile
        report_dir = os.path.join(tempfile.gettempdir(), "tls_reports")
        saved = save_reports(
            all_results, all_analyses, all_reports,
            output_dir=report_dir,
            formats="both",
        )

        print(f"\n  {GREEN}Reports saved:{RESET}")
        for path in saved:
            print(f"    -> {path}")

        # Summary
        print_header("Summary")
        total_pass = sum(r.pass_count for r in all_reports)
        total_fail = sum(r.fail_count for r in all_reports)
        total_warn = sum(r.warning_count for r in all_reports)

        print(f"  Hosts analyzed: {len(all_results)}")
        print(f"  Total checks:   {total_pass + total_fail + total_warn}")
        print(f"  {GREEN}Passed:  {total_pass}{RESET}")
        print(f"  {RED}Failed:  {total_fail}{RESET}")
        print(f"  {YELLOW}Warnings: {total_warn}{RESET}")

    print(f"\n{BOLD}Demo complete.{RESET}\n")


if __name__ == "__main__":
    main()
