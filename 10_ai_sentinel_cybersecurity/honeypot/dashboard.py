"""
Threat Intelligence Honeypot — Dashboard

Streamlit mini-dashboard: connection timeline, top IPs table,
port heatmap, and attack pattern charts.

Usage:
    streamlit run dashboard.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import streamlit as st
    import json
    from collections import Counter, defaultdict
    from datetime import datetime

    from session_logger import SessionLogger
    from threat_analyzer import analyze_sessions, profile_attacker
except ImportError as e:
    print(f"Missing dependency: {e}")
    print("Install with: pip install streamlit")
    sys.exit(1)


def load_sessions(log_dir: str = "honeypot_logs") -> list:
    """Load all sessions from the log directory."""
    logger = SessionLogger(log_dir=log_dir)
    return logger.read_all_sessions()


def main():
    st.set_page_config(
        page_title="Honeypot Threat Intelligence",
        page_icon="🍯",
        layout="wide",
    )

    st.title("Honeypot Threat Intelligence Dashboard")
    st.caption("Connection analysis from simulated honeypot services")

    # Sidebar: configuration
    with st.sidebar:
        st.header("Settings")
        log_dir = st.text_input("Log Directory", value="honeypot_logs")
        top_n = st.slider("Top N Attackers", 5, 25, 10)
        min_conn = st.slider("Min Connections to Flag", 1, 10, 3)

    # Load data
    sessions = load_sessions(log_dir)

    if not sessions:
        st.warning(
            "No session data found. Run `python example.py` first to "
            "generate simulated attack logs."
        )
        return

    # Analyze
    summary = analyze_sessions(
        sessions, top_n=top_n, min_connections_to_flag=min_conn
    )

    # ── Metrics Row ──────────────────────────────────────────
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Sessions", summary.total_sessions)
    col2.metric("Unique IPs", summary.unique_ips)
    col3.metric("With Payload", summary.sessions_with_payload)
    col4.metric("Avg Payload (bytes)", f"{summary.avg_payload_size:.0f}")

    # ── Top Attackers Table ──────────────────────────────────
    st.subheader("Top Attacking IPs")
    if summary.top_attackers:
        st.table(summary.top_attackers)

    # ── Charts Row ───────────────────────────────────────────
    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("Port Distribution")
        if summary.port_distribution:
            port_labels = [
                f"Port {p}" for p in summary.port_distribution.keys()
            ]
            port_values = list(summary.port_distribution.values())
            import pandas as pd
            port_df = pd.DataFrame({
                "Port": port_labels,
                "Connections": port_values,
            })
            st.bar_chart(port_df.set_index("Port"))

    with col_right:
        st.subheader("Attack Classifications")
        if summary.classification_distribution:
            import pandas as pd
            class_df = pd.DataFrame({
                "Type": list(summary.classification_distribution.keys()),
                "Count": list(summary.classification_distribution.values()),
            })
            st.bar_chart(class_df.set_index("Type"))

    # ── Hourly Timeline ──────────────────────────────────────
    st.subheader("Hourly Activity Pattern")
    if summary.hourly_distribution:
        import pandas as pd
        hours = {str(h): 0 for h in range(24)}
        hours.update(summary.hourly_distribution)
        hour_df = pd.DataFrame({
            "Hour": [f"{int(h):02d}:00" for h in sorted(hours.keys(), key=int)],
            "Connections": [hours[h] for h in sorted(hours.keys(), key=int)],
        })
        st.line_chart(hour_df.set_index("Hour"))

    # ── Service Distribution ─────────────────────────────────
    st.subheader("Service Distribution")
    if summary.service_distribution:
        import pandas as pd
        svc_df = pd.DataFrame({
            "Service": list(summary.service_distribution.keys()),
            "Connections": list(summary.service_distribution.values()),
        })
        st.bar_chart(svc_df.set_index("Service"))

    # ── High Frequency IPs ───────────────────────────────────
    if summary.high_frequency_ips:
        st.subheader(f"High-Frequency IPs (>= {min_conn} connections)")
        for ip in summary.high_frequency_ips[:10]:
            profile = profile_attacker(ip, sessions)
            with st.expander(
                f"{ip} — {profile.total_connections} connections"
            ):
                st.write(f"**First Seen:** {profile.first_seen}")
                st.write(f"**Last Seen:** {profile.last_seen}")
                st.write(f"**Services:** {', '.join(profile.targeted_services)}")
                st.write(f"**Ports:** {', '.join(map(str, profile.targeted_ports))}")
                st.write(f"**Classifications:** {', '.join(profile.classifications)}")
                st.write(f"**Avg Payload:** {profile.avg_payload_size} bytes")

    # ── Raw Sessions ─────────────────────────────────────────
    with st.expander("Raw Session Data (last 50)"):
        import pandas as pd
        from dataclasses import asdict
        recent = sessions[-50:]
        if recent:
            df = pd.DataFrame([asdict(s) for s in recent])
            st.dataframe(df, use_container_width=True)


if __name__ == "__main__":
    main()
