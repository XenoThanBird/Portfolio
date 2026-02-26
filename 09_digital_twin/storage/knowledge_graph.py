"""
Knowledge Graph implementation using NetworkX.
Supports relationship modeling, centrality analysis, community detection,
and temporal queries. Designed for upgrade to Neo4j at production scale.
"""

import pickle
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

import networkx as nx


class KnowledgeGraph:
    """
    Knowledge graph for modeling relationships between entities.
    Built on NetworkX with a directed multi-graph for typed edges.
    """

    def __init__(self, persist_path: Optional[str] = None):
        """
        Initialize knowledge graph.

        Args:
            persist_path: Path to persist the graph (pickle format)
        """
        self.persist_path = Path(persist_path) if persist_path else None

        if self.persist_path:
            self.persist_path.parent.mkdir(parents=True, exist_ok=True)

        self.graph = nx.MultiDiGraph()

        if self.persist_path and self.persist_path.exists():
            self.load()

    def add_node(
        self,
        node_id: str,
        node_type: str,
        properties: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Add a node to the graph."""
        props = properties or {}
        props["node_type"] = node_type
        props["created_at"] = datetime.now().isoformat()
        self.graph.add_node(node_id, **props)
        return node_id

    def add_edge(
        self,
        from_node: str,
        to_node: str,
        edge_type: str,
        properties: Optional[Dict[str, Any]] = None,
    ) -> Tuple[str, str, str]:
        """Add a typed edge between two nodes (auto-creates missing nodes)."""
        props = properties or {}

        if not self.graph.has_node(from_node):
            self.add_node(from_node, node_type="auto_created")
        if not self.graph.has_node(to_node):
            self.add_node(to_node, node_type="auto_created")

        props["edge_type"] = edge_type
        props["created_at"] = datetime.now().isoformat()

        self.graph.add_edge(from_node, to_node, key=edge_type, **props)
        return (from_node, to_node, edge_type)

    def get_node(self, node_id: str) -> Optional[Dict[str, Any]]:
        """Get node properties by ID."""
        if not self.graph.has_node(node_id):
            return None
        return dict(self.graph.nodes[node_id])

    def get_neighbors(
        self,
        node_id: str,
        edge_type: Optional[str] = None,
        direction: str = "out",
    ) -> List[Tuple[str, Dict]]:
        """Get neighbors of a node, optionally filtered by edge type and direction."""
        if not self.graph.has_node(node_id):
            return []

        neighbors = []
        if direction in ("out", "both"):
            for _, neighbor, key, data in self.graph.out_edges(node_id, keys=True, data=True):
                if edge_type is None or key == edge_type:
                    neighbors.append((neighbor, data))
        if direction in ("in", "both"):
            for predecessor, _, key, data in self.graph.in_edges(node_id, keys=True, data=True):
                if edge_type is None or key == edge_type:
                    neighbors.append((predecessor, data))
        return neighbors

    def find_path(
        self,
        from_node: str,
        to_node: str,
        max_length: Optional[int] = None,
    ) -> Optional[List[str]]:
        """Find shortest path between two nodes."""
        try:
            path = nx.shortest_path(self.graph, from_node, to_node)
            if max_length and len(path) - 1 > max_length:
                return None
            return path
        except nx.NetworkXNoPath:
            return None

    def find_central_nodes(
        self, metric: str = "degree", top_k: int = 10
    ) -> List[Tuple[str, float]]:
        """
        Find most central nodes using the specified metric.

        Args:
            metric: 'degree', 'betweenness', 'closeness', or 'pagerank'
            top_k: Number of top nodes to return
        """
        if metric == "degree":
            centrality = dict(self.graph.degree())
        elif metric == "betweenness":
            centrality = nx.betweenness_centrality(self.graph)
        elif metric == "closeness":
            centrality = nx.closeness_centrality(self.graph)
        elif metric == "pagerank":
            centrality = nx.pagerank(self.graph)
        else:
            raise ValueError(f"Unknown centrality metric: {metric}")

        return sorted(centrality.items(), key=lambda x: x[1], reverse=True)[:top_k]

    def find_communities(self) -> List[Set[str]]:
        """Detect communities using greedy modularity (undirected projection)."""
        undirected = self.graph.to_undirected()
        try:
            from networkx.algorithms import community
            return [set(c) for c in community.greedy_modularity_communities(undirected)]
        except ImportError:
            return [set(c) for c in nx.connected_components(undirected)]

    def temporal_query(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        node_id: Optional[str] = None,
    ) -> List[Tuple[str, str, str, Dict]]:
        """Query edges by timestamp range, optionally filtered by node."""
        edges = []
        for u, v, key, data in self.graph.edges(keys=True, data=True):
            if node_id and u != node_id and v != node_id:
                continue
            if "created_at" in data:
                edge_time = datetime.fromisoformat(data["created_at"])
                if start_date and edge_time < start_date:
                    continue
                if end_date and edge_time > end_date:
                    continue
            edges.append((u, v, key, data))
        return edges

    def stats(self) -> Dict[str, Any]:
        """Get graph statistics."""
        node_types: Dict[str, int] = {}
        for _, data in self.graph.nodes(data=True):
            t = data.get("node_type", "unknown")
            node_types[t] = node_types.get(t, 0) + 1

        edge_types: Dict[str, int] = {}
        for _, _, key in self.graph.edges(keys=True):
            edge_types[key] = edge_types.get(key, 0) + 1

        return {
            "num_nodes": self.graph.number_of_nodes(),
            "num_edges": self.graph.number_of_edges(),
            "density": nx.density(self.graph),
            "node_types": node_types,
            "edge_types": edge_types,
            "is_connected": nx.is_weakly_connected(self.graph) if self.graph.number_of_nodes() > 0 else True,
            "num_components": nx.number_weakly_connected_components(self.graph) if self.graph.number_of_nodes() > 0 else 0,
        }

    def save(self, path: Optional[str] = None):
        """Persist graph to disk (pickle)."""
        save_path = Path(path) if path else self.persist_path
        if save_path is None:
            raise ValueError("No persist path configured")
        save_path.parent.mkdir(parents=True, exist_ok=True)
        with open(save_path, "wb") as f:
            pickle.dump(self.graph, f, pickle.HIGHEST_PROTOCOL)

    def load(self, path: Optional[str] = None):
        """Load graph from disk."""
        load_path = Path(path) if path else self.persist_path
        if load_path and load_path.exists():
            with open(load_path, "rb") as f:
                self.graph = pickle.load(f)

    def clear(self):
        """Remove all nodes and edges."""
        self.graph.clear()
