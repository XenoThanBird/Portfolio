"""
Threat Intelligence Honeypot — Server

Async TCP listener (asyncio) simulating SSH, HTTP, and Telnet services
on non-standard ports. Logs all connection attempts for threat analysis.

Uses non-standard ports (2222, 8080, 2323) to avoid conflicts and
privilege requirements. No actual credential capture — only logs
connection metadata.
"""

import asyncio
import secrets
import signal
import sys
from datetime import datetime, timezone
from typing import Optional

from session_logger import SessionLogger, SessionRecord


class HoneypotProtocol(asyncio.Protocol):
    """Protocol handler for a single honeypot connection."""

    def __init__(
        self,
        service: str,
        port: int,
        banner: str,
        logger: SessionLogger,
        max_payload: int = 4096,
    ):
        self.service = service
        self.port = port
        self.banner = banner
        self.logger = logger
        self.max_payload = max_payload
        self.transport = None
        self.session_id = secrets.token_hex(8)
        self.connected_at = datetime.now(timezone.utc)
        self.payload_data = b""
        self.peer = None

    def connection_made(self, transport):
        self.transport = transport
        self.peer = transport.get_extra_info("peername")
        peer_str = f"{self.peer[0]}:{self.peer[1]}" if self.peer else "unknown"

        print(
            f"  [{self.service}] Connection from {peer_str} "
            f"(session {self.session_id})"
        )

        # Send service banner
        if self.banner:
            transport.write(self.banner.encode("utf-8", errors="replace"))

    def data_received(self, data: bytes):
        if len(self.payload_data) < self.max_payload:
            self.payload_data += data[: self.max_payload - len(self.payload_data)]

        # Close after receiving data (low-interaction honeypot)
        self.transport.close()

    def connection_lost(self, exc):
        duration = (
            datetime.now(timezone.utc) - self.connected_at
        ).total_seconds()

        # Classify the connection
        classification = _classify_payload(
            self.payload_data, self.service
        )

        # Create safe payload preview (printable chars only)
        preview = self.payload_data[:256].decode(
            "utf-8", errors="replace"
        ).replace("\n", "\\n").replace("\r", "\\r")

        record = SessionRecord(
            session_id=self.session_id,
            timestamp=self.connected_at.isoformat(),
            source_ip=self.peer[0] if self.peer else "unknown",
            source_port=self.peer[1] if self.peer else 0,
            dest_port=self.port,
            protocol="tcp",
            service=self.service,
            payload_preview=preview,
            payload_bytes=len(self.payload_data),
            duration_seconds=round(duration, 3),
            geo_country="",  # Stub — would use GeoIP in production
            geo_city="",
            classification=classification,
        )

        self.logger.log_session(record)


def _classify_payload(payload: bytes, service: str) -> str:
    """Basic payload classification based on content heuristics."""
    if not payload:
        return "scan"

    payload_lower = payload.lower()

    # SSH brute force indicators
    if service == "ssh" and (b"password" in payload_lower or len(payload) < 50):
        return "brute_force"

    # HTTP exploit indicators
    if service == "http":
        if any(
            pattern in payload_lower
            for pattern in [b"../", b"cmd=", b"<script", b"union select"]
        ):
            return "exploit"
        if b"GET " in payload or b"POST " in payload:
            return "scan"

    # Telnet brute force
    if service == "telnet" and len(payload) < 100:
        return "brute_force"

    if len(payload) > 500:
        return "exploit"

    return "unknown"


class HoneypotServer:
    """
    Multi-service honeypot server using asyncio.

    Runs simulated SSH, HTTP, and Telnet listeners concurrently,
    logging all connection attempts.
    """

    def __init__(self, logger: SessionLogger):
        self.logger = logger
        self.servers = []
        self._running = False

    async def start_listener(
        self, service: str, port: int, banner: str
    ) -> None:
        """Start a single service listener."""
        loop = asyncio.get_event_loop()

        def protocol_factory():
            return HoneypotProtocol(
                service=service,
                port=port,
                banner=banner,
                logger=self.logger,
            )

        try:
            server = await loop.create_server(
                protocol_factory, "127.0.0.1", port
            )
            self.servers.append(server)
            print(f"  [{service.upper()}] Listening on 127.0.0.1:{port}")
        except OSError as e:
            print(f"  [{service.upper()}] Failed to bind port {port}: {e}")

    async def run(
        self,
        services: list = None,
        duration: int = None,
    ) -> None:
        """
        Run all honeypot listeners.

        Args:
            services: List of (service, port, banner) tuples
            duration: Auto-stop after N seconds (None = run forever)
        """
        if services is None:
            services = [
                ("ssh", 2222, "SSH-2.0-OpenSSH_8.9p1 Ubuntu-3ubuntu0.1\r\n"),
                (
                    "http",
                    8080,
                    "HTTP/1.1 200 OK\r\nServer: Apache/2.4.52\r\n\r\n",
                ),
                ("telnet", 2323, "Ubuntu 22.04 LTS\nlogin: "),
            ]

        self._running = True

        for service, port, banner in services:
            await self.start_listener(service, port, banner)

        if not self.servers:
            print("  No listeners started. Exiting.")
            return

        print(f"\n  Honeypot active. Press Ctrl+C to stop.\n")

        if duration:
            await asyncio.sleep(duration)
            await self.stop()
        else:
            # Run until stopped
            try:
                while self._running:
                    await asyncio.sleep(1)
            except asyncio.CancelledError:
                pass

    async def stop(self) -> None:
        """Stop all listeners."""
        self._running = False
        for server in self.servers:
            server.close()
            await server.wait_closed()
        self.servers.clear()
        print("\n  Honeypot stopped.")


async def main():
    """Run the honeypot server."""
    logger = SessionLogger(log_dir="honeypot_logs")

    server = HoneypotServer(logger)

    # Handle Ctrl+C
    loop = asyncio.get_event_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, lambda: asyncio.create_task(server.stop()))
        except NotImplementedError:
            # Windows doesn't support add_signal_handler
            pass

    await server.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nShutdown complete.")
