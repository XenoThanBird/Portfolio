"""
Network Inventory & Audit — Network Visualizer

NetworkX + matplotlib graph visualization of discovered topology.
Nodes colored by device type, edges by connection type.
"""

import os
from typing import Optional

from scanner import DeviceInfo

try:
    import networkx as nx
    import matplotlib
    matplotlib.use("Agg")  # Non-interactive backend
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    HAS_VISUALIZATION = True
except ImportError:
    HAS_VISUALIZATION = False


# Default color scheme by device type
DEFAULT_COLORS = {
    "gateway": "#FF6B6B",
    "server": "#4ECDC4",
    "workstation": "#45B7D1",
    "iot": "#96CEB4",
    "unknown": "#DFE6E9",
    "scanner": "#FFD93D",
}


def build_topology_graph(
    devices: list,
    scanner_ip: str = "You",
) -> "nx.Graph":
    """
    Build a NetworkX graph from discovered devices.

    Creates a star topology with the scanner at the center and
    discovered devices as leaf nodes.
    """
    if not HAS_VISUALIZATION:
        raise RuntimeError(
            "networkx and matplotlib required — "
            "pip install networkx matplotlib"
        )

    G = nx.Graph()

    # Add scanner node at center
    G.add_node(
        scanner_ip,
        device_type="scanner",
        label=scanner_ip,
        open_ports=[],
    )

    # Add discovered devices
    for device in devices:
        label = device.hostname or device.ip
        if device.vendor:
            label += f"\n({device.vendor})"

        port_labels = [
            f"{p.port}/{p.service}" for p in device.open_ports[:5]
        ]
        if len(device.open_ports) > 5:
            port_labels.append(f"... +{len(device.open_ports) - 5} more")

        G.add_node(
            device.ip,
            device_type=device.device_type,
            label=label,
            open_ports=port_labels,
            os_guess=device.os_guess,
            risk_level=device.risk_level,
        )

        # Edge from scanner to device
        G.add_edge(
            scanner_ip,
            device.ip,
            ports=len(device.open_ports),
        )

    return G


def visualize_topology(
    devices: list,
    output_file: str = "network_topology.png",
    figsize: tuple = (14, 10),
    colors: dict = None,
    scanner_ip: str = "You",
) -> str:
    """
    Generate a network topology visualization.

    Returns the path to the saved image file.
    """
    if not HAS_VISUALIZATION:
        raise RuntimeError(
            "networkx and matplotlib required — "
            "pip install networkx matplotlib"
        )

    if colors is None:
        colors = DEFAULT_COLORS

    G = build_topology_graph(devices, scanner_ip)

    fig, ax = plt.subplots(1, 1, figsize=figsize)
    ax.set_title(
        "Network Topology — Device Inventory",
        fontsize=16,
        fontweight="bold",
        pad=20,
    )

    # Layout
    if len(G.nodes) <= 1:
        pos = nx.spring_layout(G, seed=42)
    else:
        pos = nx.spring_layout(G, k=2.5, seed=42, iterations=50)

    # Color nodes by device type
    node_colors = []
    for node in G.nodes():
        dtype = G.nodes[node].get("device_type", "unknown")
        node_colors.append(colors.get(dtype, colors.get("unknown", "#DFE6E9")))

    # Draw nodes
    nx.draw_networkx_nodes(
        G, pos, ax=ax,
        node_color=node_colors,
        node_size=2000,
        alpha=0.9,
        edgecolors="#333333",
        linewidths=2,
    )

    # Draw edges
    nx.draw_networkx_edges(
        G, pos, ax=ax,
        edge_color="#AAAAAA",
        width=2,
        alpha=0.6,
    )

    # Draw labels
    labels = {
        node: G.nodes[node].get("label", node) for node in G.nodes()
    }
    nx.draw_networkx_labels(
        G, pos, labels, ax=ax,
        font_size=8,
        font_weight="bold",
    )

    # Add port annotations
    for node in G.nodes():
        if node == scanner_ip:
            continue
        ports = G.nodes[node].get("open_ports", [])
        if ports:
            x, y = pos[node]
            port_text = "\n".join(ports[:4])
            if len(ports) > 4:
                port_text += f"\n+{len(ports) - 4} more"
            ax.annotate(
                port_text,
                xy=(x, y),
                xytext=(15, -15),
                textcoords="offset points",
                fontsize=6,
                color="#666666",
                bbox=dict(
                    boxstyle="round,pad=0.3",
                    facecolor="white",
                    edgecolor="#CCCCCC",
                    alpha=0.8,
                ),
            )

    # Legend
    legend_patches = []
    for dtype, color in colors.items():
        count = sum(
            1 for n in G.nodes()
            if G.nodes[n].get("device_type") == dtype
        )
        if count > 0:
            legend_patches.append(
                mpatches.Patch(
                    color=color,
                    label=f"{dtype.title()} ({count})",
                )
            )
    if legend_patches:
        ax.legend(
            handles=legend_patches,
            loc="upper left",
            fontsize=9,
            framealpha=0.9,
        )

    ax.axis("off")
    plt.tight_layout()

    # Save
    os.makedirs(os.path.dirname(output_file) or ".", exist_ok=True)
    plt.savefig(output_file, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)

    return output_file
