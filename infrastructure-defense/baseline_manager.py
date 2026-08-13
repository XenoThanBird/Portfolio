"""
Baseline Manager — The Sentinel Script
----------------------------------------
Manages file integrity baseline snapshots: creation, versioning,
comparison, and audit reporting. Uses portable JSON format.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("sentinel.baseline")


class BaselineManager:
    """
    Handles baseline file integrity snapshots.

    Baselines are stored as JSON files:
        baselines/baseline_2024-01-20T10-30-00.json

    Each file contains:
        {
            "metadata": { "created_at", "name", "file_count", ... },
            "files": { "/path/to/file": { "hash", "size", ... }, ... }
        }
    """

    def __init__(self, config: dict):
        bl_cfg = config.get("baseline", {})
        self.storage_path = Path(bl_cfg.get("storage_path", "baselines"))
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.auto_backup: bool = bl_cfg.get("auto_backup", True)
        self.max_versions: int = bl_cfg.get("max_versions", 10)

        self._watch_paths = config.get("watch", {}).get("paths", [])
        self._hash_algorithm = config.get("scanning", {}).get("hash_algorithm", "sha256")

    def save(self, file_records: Dict[str, Any], name: Optional[str] = None) -> Path:
        """
        Save a new baseline snapshot.

        Args:
            file_records: {path: FileRecord} dict from a scan
            name: Optional human-readable label

        Returns:
            Path to the saved baseline file
        """
        now = datetime.utcnow()
        metadata = {
            "created_at": now.isoformat(),
            "name": name or "auto",
            "file_count": len(file_records),
            "watch_paths": self._watch_paths,
            "hash_algorithm": self._hash_algorithm,
        }

        serialized_files = {}
        for path, record in file_records.items():
            if hasattr(record, "to_dict"):
                serialized_files[path] = record.to_dict()
            elif isinstance(record, dict):
                serialized_files[path] = record
            else:
                serialized_files[path] = vars(record)

        baseline = {"metadata": metadata, "files": serialized_files}

        filename = self._baseline_filename(name)
        filepath = self.storage_path / filename

        with open(filepath, "w") as f:
            json.dump(baseline, f, indent=2, default=str)

        logger.info("Baseline saved: %s (%d files)", filepath.name, len(file_records))

        self._prune_old()
        return filepath

    def load_latest(self) -> Optional[Dict[str, dict]]:
        """Load the most recent baseline. Returns {path: record_dict} or None."""
        baselines = sorted(self.storage_path.glob("baseline_*.json"))
        if not baselines:
            return None
        return self._load_file(baselines[-1])

    def load(self, name_or_path: str) -> Optional[Dict[str, dict]]:
        """Load a specific baseline by name or file path."""
        path = Path(name_or_path)
        if path.exists():
            return self._load_file(path)

        for bl_file in self.storage_path.glob("baseline_*.json"):
            if name_or_path in bl_file.name:
                return self._load_file(bl_file)

        return None

    def list_baselines(self) -> List[Dict[str, Any]]:
        """List all available baselines with metadata summaries."""
        results = []
        for bl_file in sorted(self.storage_path.glob("baseline_*.json")):
            try:
                with open(bl_file) as f:
                    data = json.load(f)
                meta = data.get("metadata", {})
                results.append({
                    "path": str(bl_file),
                    "name": meta.get("name", "unknown"),
                    "created_at": meta.get("created_at", "unknown"),
                    "file_count": meta.get("file_count", 0),
                })
            except (json.JSONDecodeError, OSError) as e:
                logger.warning("Could not read baseline %s: %s", bl_file, e)
        return results

    def compare_baselines(self, path_a: str, path_b: str) -> Dict[str, Any]:
        """
        Diff two baselines. Returns structured change report.

        Args:
            path_a: Path or name of first baseline (older)
            path_b: Path or name of second baseline (newer)

        Returns:
            Dict with added, removed, modified lists and summary stats
        """
        files_a = self.load(path_a) or {}
        files_b = self.load(path_b) or {}

        paths_a = set(files_a.keys())
        paths_b = set(files_b.keys())

        added = sorted(paths_b - paths_a)
        removed = sorted(paths_a - paths_b)

        modified = []
        for path in sorted(paths_a & paths_b):
            rec_a = files_a[path]
            rec_b = files_b[path]
            if rec_a.get("hash") != rec_b.get("hash"):
                modified.append(path)

        return {
            "added": added,
            "removed": removed,
            "modified": modified,
            "summary": {
                "added_count": len(added),
                "removed_count": len(removed),
                "modified_count": len(modified),
                "unchanged_count": len(paths_a & paths_b) - len(modified),
            },
        }

    def export_report(self, baseline_name: Optional[str] = None) -> str:
        """Generate a human-readable report of a baseline."""
        if baseline_name:
            files = self.load(baseline_name)
        else:
            files = self.load_latest()

        if not files:
            return "No baseline found."

        total_size = sum(r.get("size", 0) for r in files.values())
        extensions: Dict[str, int] = {}
        for path in files:
            ext = Path(path).suffix or "(no ext)"
            extensions[ext] = extensions.get(ext, 0) + 1

        top_ext = sorted(extensions.items(), key=lambda x: x[1], reverse=True)[:10]

        lines = [
            "BASELINE REPORT",
            "=" * 50,
            f"  Files indexed:    {len(files)}",
            f"  Total size:       {total_size / (1024 * 1024):.1f} MB",
            f"  File types:       {len(extensions)}",
            "",
            "  Top extensions:",
        ]
        for ext, count in top_ext:
            lines.append(f"    {ext:<15} {count:>6} files")

        lines.append("=" * 50)
        return "\n".join(lines)

    def _load_file(self, path: Path) -> Optional[Dict[str, dict]]:
        """Load and parse a baseline JSON file."""
        try:
            with open(path) as f:
                data = json.load(f)
            return data.get("files", {})
        except (json.JSONDecodeError, OSError) as e:
            logger.error("Failed to load baseline %s: %s", path, e)
            return None

    def _prune_old(self):
        """Remove oldest baselines if count exceeds max_versions."""
        baselines = sorted(self.storage_path.glob("baseline_*.json"))
        while len(baselines) > self.max_versions:
            oldest = baselines.pop(0)
            oldest.unlink()
            logger.info("Pruned old baseline: %s", oldest.name)

    def _baseline_filename(self, name: Optional[str] = None) -> str:
        """Generate baseline filename with timestamp."""
        ts = datetime.utcnow().strftime("%Y-%m-%dT%H-%M-%S")
        suffix = f"_{name}" if name else ""
        return f"baseline_{ts}{suffix}.json"
